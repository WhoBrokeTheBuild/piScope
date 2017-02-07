'''
    Video Viewer

    VideoViewer is a type of dynamic data generation, in which
    3D arrays is treated as video data.

     See image_video_demo() in ifigure.plot_demos for example

    VideoViewerMode is a mix-in class which repurpose multipage 
    feature of BookViewer to realize daynamic data generatation and 
    drawing. This class is also used in wave_viewer, in which
    frame data is generater dynamically using phasor.

'''
import wx
from ifigure.widgets.book_viewer import BookViewer, BookViewerFrame, ID_KEEPDATA
import ifigure.events
import weakref
import numpy as np
from .videoplayer_buttons import VideoplayerButtons

class VideoViewerMode(object):
    ID_PLAYERBUTTON = wx.NewId()        
    def __init__(self, *args, **kwargs):
        self._video_obj = weakref.WeakSet()        
        self._video_page = -1
        if not hasattr(self, '_playerbtn'):
            self._playerbtn = None
        self._playinterval = 100
        self._playloop = False
        self._is_playing = 0 # 0: stop, 1: forward, -1: backward        

    def add_all_video_obj(self):
        raise NotImplementedError('VideoViewerMode::add_all_video_obj should be overwritten')

    def add_video_obj(self, figobj):
        self._video_obj.add(figobj)
    
    def set_window_title(self):
        if self.book is None: 
            self.SetTitle('')
            return 
        title=self.book.get_full_path()+'(frame '+str(self._video_page+1)+')'
        self.SetTitle(title)
    
    def onGoToFrame(self, evt):
        from ifigure.utils.edit_list import DialogEditList
        list6 = [("Frame number (1-"+ str(self.num_page()) + ")",
                   str(self._video_page), 0, None),]
        value = DialogEditList(list6, modal = True, 
                     style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER,
                     tip = None, 
                     parent=self,)

        if value[0] is True:
            ipage = long(value[1][0])
        else:
            return 
        self.goto_frame(ipage)
        self.property_editor.onTD_ShowPage(evt)

    def goto_frame(self, ipage):
        self.UpdateImage(ipage)
        self.canvas.exit_layout_mode()
        self.set_window_title()
        wx.CallAfter(self.draw)

    def _onTD_ShowPage(self, evt):
        from ifigure.mto.fig_page import FigPage
        dt = evt.GetTreeDict() #dt fig_page
        if isinstance(dt, FigPage):
           self.book.set_open(False)
           dt.get_root_parent().set_pbook(dt.get_parent())
           self.book = dt.get_parent()
           self.ipage = 0
        elif dt == self.book:
           ipage = self._video_page
           pass
        else: 
           return
        ipage = self._video_page
        num_page = self.num_page()
        if evt.inc ==  '-1':
           if self._playloop:
               if self._video_page == 0:
                   ipage = num_page - 1
               else:
                   ipage = self._video_page - 1
           else:
               ipage = max([self._video_page-1, 0])
        elif evt.inc == '1':
           if self._playloop:
               if self._video_page == num_page-1:
                   ipage = 0
               else:
                   ipage = self._video_page+1
           else:
               ipage=min([self._video_page+1, num_page-1])
        elif evt.inc == 'first':
           ipage=0
        elif evt.inc == 'last':
           ipage=num_page-1
        else:
           pass
        self.goto_frame(ipage)
        self.property_editor.onTD_ShowPage(evt)
        
    def onTD_ShowPage(self, evt):
        if not evt.BookViewerFrame_Processed:
           self._onTD_ShowPage(evt)
           evt.BookViewerFrame_Processed = True
           evt.SetEventObject(self)
           if self._is_playing != 0:
               wx.CallLater(self._playinterval, self.onTime)
        evt.Skip()
        
    def onNextPage(self, evt):
        self.onNextVideoPage(evt)
        
    def onPrevPage(self, evt):        
        self.onPrevVideoPage(evt)        

    def onActivate(self, evt):
        if self._playerbtn is not None:
            self._playerbtn.Raise()
    def save_animgif(self, filename='animation.gif',
                     show_page = None):
        def show_page(args):
             k = args[0]
             self.goto_frame(k)
             self.draw()
        BookViewer.save_animgif(self, filename = filename,
                                show_page = show_page)
        
    def save_multipdf(self, filename='figure_allpage.pdf',
                      show_page = None):
        def show_page(args):
             k = args[0]
             self.goto_frame(k)
             self.draw()
        BookViewer.save_multipdf(self, filename = filename, 
                                show_page = show_page)

    def add_bookmenus(self, editmenu, viewmenu):

        self.add_menu(editmenu, VideoViewerMode.ID_PLAYERBUTTON,
                      "Go to Frame...", 
                      "select frame number",
                      self.onGoToFrame)
        editmenu.AppendSeparator()
        self.add_menu(editmenu, ID_KEEPDATA, 
                            "Keep Book in Tree",
                            "Book data is kept in tree when this window is closed", 
                            self.onKeepData, 
                            kind = wx.ITEM_CHECK)
        
        self._mm_player = self.insert_menu(viewmenu, 1, wx.ID_ANY,
                        "Player Panel", "toggle player button panel",
                         self.onTogglePlayerButton,
                        kind = wx.ITEM_CHECK)
        self._playerbtn = VideoplayerButtons(self, wx.ID_ANY, self.book.name)
        self._mm_player.Check(True)        
        self.add_menu(viewmenu, BookViewerFrame.ID_PM[4], 
                     "Next Page",  "next page",
                      self.onNextVideoPage)
        self.add_menu(viewmenu, BookViewerFrame.ID_PM[5], 
                     "Previous Page", "previous page",  
                     self.onPrevVideoPage)
        
    def onTogglePlayerButton(self, evt):
        if self._mm_player.IsChecked():
            if self._playerbtn is None:
                self._playerbtn = VideoplayerButtons(self, wx.ID_ANY, self.book.name)
        else:
            self._playerbtn.Destroy()
            self._playerbtn = None
            
    def onPlayerButtonClose(self):
        self._mm_player.Check(False)
        self._playerbtn = None
        
    def goto_last(self):
        ifigure.events.SendShowPageEvent(self.book, self, 'last')
        
    def goto_first(self):
        ifigure.events.SendShowPageEvent(self.book, self, 'first')
        
    def step_fwd(self):
        ifigure.events.SendShowPageEvent(self.book, self, '1')
        
    def step_rev(self):
        ifigure.events.SendShowPageEvent(self.book, self, '-1')

    def onTime(self):
        num_page = self.num_page()        
        if self._is_playing != 0:
           if (self._video_page == 0 and self._is_playing == -1 and
               not self._playloop):
               self._is_playing = 0
               if self._playerbtn is not None:
                   self._playerbtn.reset_btn_toggle_bitmap()
               return
           if (self._video_page == num_page-1 and self._is_playing == 1 and
               not self._playloop):
               self._playerbtn.reset_btn_toggle_bitmap()
               self._is_playing = 0
               return
           ifigure.events.SendShowPageEvent(self.book, self, str(self._is_playing))
           
    def play_fwd(self):
        self._is_playing = 1
        wx.CallLater(self._playinterval, self.onTime)
        
    def play_rev(self):
        self._is_playing = -1
        wx.CallLater(self._playinterval, self.onTime)
        
    def stop_play(self):
        self._is_playing = 0
        
    def videoviewer_config(self):
        from ifigure.utils.edit_list import DialogEditList                
        l = [
            ["Interval(sec.)", str(float(self._playinterval)/1000.),
             0, {'noexpand': True}],
             [None, self._playloop, 3, {"text":"Loop", "noindent":None }],
             ]
        value = DialogEditList(l, parent=self, 
                   title = 'Player Config.',
                   style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        if not value[0]: return
        interval = min([50,int(float(value[1][0])*1000.)])
        self._playinterval = interval
        self._playloop = bool(value[1][1])
    
from ifigure.mto.fig_image import FigImage
class FigImageVideo(FigImage):
    def set_video_data(self, value):
        self._video = value
    def get_nframe(self):
        return self._video.shape[0]
    
    def save_data2(self, data=None):    
        data['FigImageVideo'] = (1, {'_vidoe': self._video})
        data = super(FigImageVideo, self).save_data2(data)
        return
                                 
    def load_data2(self, data=None):
        d = data['FigImageVideo']
        super(FigImageVideo, self).load_data2(data)
        self._video = d[1]['_video']

    def show_videoframe(self, i):                              
        self.setp('z', self._video[i])
        x, y, z  = self.getp(("x", "y", "z"))
        xp, yp, zp = self.interp_image(x, y, z)
        a = self._artists[0]
        a.set_array(zp)
        setattr(a.get_array(), '_xyp', (xp, yp))
        self.set_bmp_update(False)
                                 
def convert_figobj(obj):
    if obj.__class__ == FigImage:
        obj.__class__ = FigImageVideo
    
class VideoViewer(VideoViewerMode, BookViewer):
    def __init__(self, *args, **kwargs):
        self._video_obj = []
        kwargs['isattachable'] = False
        VideoViewerMode.__init__(self, *args, **kwargs)
        BookViewer.__init__(self, *args, **kwargs)
        if self.book is not None:
           self.add_all_video_obj()
        self.Bind(wx.EVT_ACTIVATE, self.onActivate)
        
    def onActivate(self, evt):
        VideoViewerMode.onActivate(self, evt)
        
    def image(self, *args, **kwargs):
        '''
        image(z)
        or
        image(x, y, z)
        '''
        if len(args) == 1:
            z = args[0]            
            x = np.arange(z.shape[-1])
            y = np.arange(z.shape[-2])
        elif len(args) == 3:
            x = args[0]
            y = args[1]
            z = args[2]
        if z.ndim != 3:
            raise ValueError('z data should have ndim = 3')
        
        o = BookViewer.image(self, x, y, z[0], **kwargs)
        if o is None: return
        convert_figobj(o)
        o.set_video_data(z)
        self.add_video_obj(o)        
        return o
    
    def add_all_video_obj(self):                
        for obj in self.book.walk_tree():
            if isinstance(obj, FigImageVideo): self.add_video_obj(obj)

    def num_page(self):
        return min([o.get_nframe() for o in self._video_obj])
    
    def onNextVideoPage(self, e):
        num_page=self.num_page()
        if self._video_page == num_page-1:
           return
        ifigure.events.SendShowPageEvent(self.book, self, '1') 

    def onPrevVideoPage(self, e):
        if self._video_page == 0:
           return
        ifigure.events.SendShowPageEvent(self.book, self, '-1')
   
#    def onTD_ShowPage(self, evt):
#        if not evt.BookViewerFrame_Processed:
#           VideoViewerMode.onTD_ShowPage(self, evt)
#           evt.BookViewerFrame_Processed = True
#           evt.SetEventObject(self)
#        evt.Skip()   

    def onAttachFigure(self, e):
        pass

    def adjust_attach_menu(self):
        pass
        
    def UpdateImage(self, i):
        for obj in self._video_obj:
            obj.show_videoframe(i)
        self._video_page = i



        
        










