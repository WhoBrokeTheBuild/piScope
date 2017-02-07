import os,  wx, ifigure
import numpy as np
import wx.lib.platebtn as platebtn
import wx.lib.buttons as buttons
import wx.lib.agw.buttonpanel as bp
import ifigure.utils.cbook as cbook
from ifigure.mto.fig_axes import FigInsetAxes
import ifigure.widgets.dialog as dialog
from .navibar2 import make_bitmap_with_bluebox, TaskBtnList, ButtonInfo

btasks0 = [('goto_first', 'arrow_firstpage.png', 0, 'first page'),
           ('play_rev',   'arrow_revplay.png', 1, 'reverse play'),
           ('step_rev',   'arrow_revstep.png', 1, 'step reverse'),
           ('stop_play',  'stop_play.png', 1, 'stop'),
           ('step_fwd',   'arrow_fwdstep.png', 1, 'step forward'),            
           ('play_fwd',   'arrow_fwdplay.png', 1, 'forward play'), 
           ('goto_last',  'arrow_lastpage.png', 0, 'last page'),
           ('config',    'cog.png', 1 , 'config'),]

class VideoplayerBar(bp.ButtonPanel):
    def __init__(self, parent, id=-1, text='', *args, **kargs):
        super(VideoplayerBar, self).__init__(parent, id,  text, *args, **kargs)
        self.mode = ''    # mode of action (''=select, 'pan', 'zoom', 'text'....)
        self.ptype = ''   # palette type ('pmode', 'amode')
        self.rotmode = False
        self.simple_bar = True

        self.p0  = self.make_button_group(self, btasks0)
        self.btasks0 = btasks0[:]
        self.refresh_button()
        
    def make_button_group(self, parent, btasks):
      
        bts = TaskBtnList()
        for items in btasks:
           btask, icon, tg, hint = items[:4]
           if btask == '---':
              bts.append('---') 
#              bts.AddSpacer(icon)
              continue
           from ifigure.ifigure_config import icondir
           path=os.path.join(icondir, '16x16', icon)
           if icon[-3:]=='png':
              im = wx.Image(path, wx.BITMAP_TYPE_PNG)
              image = im.ConvertToBitmap()
#              im = im.ConvertToGreyscale()
#              im = im.ConvertToMono(0,0,0)
              if im.HasAlpha(): im.ConvertAlphaToMask()
              crs =  wx.CursorFromImage(im)
           if icon[-3:]=='bmp':
              im = wx.Image(path, wx.BITMAP_TYPE_BMP)
              image = im.ConvertToBitmap()
              if im.HasAlpha(): im.ConvertAlphaToMask()
              crs =  wx.CursorFromImage(im)
           #image.SetSize((8,8))
#           btnl = ButtonInfo(self, wx.NewId(), image)
           btnl = ButtonInfo(self, wx.ID_ANY, image)
           btnl.custom_cursor = crs
           btnl.btask = btask
           btnl.bitmap1 = image
           btnl.bitmap2 = make_bitmap_with_bluebox(image)
           if hint != '':
              btnl.SetShortHelp(hint)
           if tg == 1:
              btnl.SetKind('toggle')
           if len(items) > 4:
               btnl.use_in_simple_menu  = items[4] 
           bts.append(btnl)
           #           def func(evt, btask=btask): return self.OnButton(evt, btask)
           #           parent.Bind(wx.EVT_BUTTON, func, btnl)
        return bts

    def OnLeftUp(self, evt):
        ret = self.HitTest(evt.GetPositionTuple())
        if ret[0]==wx.NOT_FOUND:
            return  bp.ButtonPanel.OnLeftUp(self, evt)                    
        
        bp.ButtonPanel.OnLeftUp(self, evt)                    
        btask = self.allbinfo[ret[0]].btask    
        self.GetParent().OnButton(evt, btask)
    
        
    def AddButtonOrS(self, b):
        if isinstance(b, bp.ButtonInfo):
           if self.simple_bar and not b.use_in_simple_menu: return
           self.AddButton(b)
           self.allbinfo.append(b)
        else:
           self.AddSeparator()
    def Clear(self):
        self.allbinfo = []
        self.Freeze()        
        bp.ButtonPanel.Clear(self)
        
    def set_toggle(self, btask):
        for p in self.p0:
           if p.btask != btask:
               p.SetStatus('Normal')
               p.SetToggled(False)
           else:
               p.SetStatus('Toggled')
               p.SetToggled(True)
               
    def set_bitmap2(self, btask):
        for p in self.p0:
            if p.btask == btask:
                p.SetBitmap(p.bitmap2) 
            else:
                p.SetBitmap(p.bitmap1)
                
    def refresh_button(self):
        self.Clear()        
        for b in self.p0: self.AddButtonOrS(b)
        self.DoLayout()        
#    def OnKeyUp(self, evt):
#       if evt.GetKeyCode() == wx.WXK_SHIFT:
#           if self.mode == 'zoom': self.SetZoomUpDown('Up')

from .miniframe_with_windowlist import MiniFrameWithWindowList
class VideoplayerButtons(MiniFrameWithWindowList):
    def __init__(self, parent, id, title='', 
                 style=wx.CAPTION|
                       wx.CLOSE_BOX|
                       wx.MINIMIZE_BOX| 
                       wx.RESIZE_BORDER|
                       wx.FRAME_FLOAT_ON_PARENT,
                       pos=None):
        MiniFrameWithWindowList.__init__(self, parent, id, title, style=style)
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.btn = VideoplayerBar(self)
        self.SetSizer(vbox)
        vbox.Add(self.btn, 1, wx.EXPAND|wx.ALIGN_CENTER, 3)

        self.Layout()
        self.Fit()
        self.Show()
        self.Bind(wx.EVT_CLOSE, self.onClose)
        wx.GetApp().add_palette(self)
        wx.CallAfter(self.CentreOnParent)
        
    def onClose(self, evt):
        wx.GetApp().rm_palette(self)        
        self.GetParent().onPlayerButtonClose()
        evt.Skip()

    def OnButton(self, evt, btask):

        v = self.GetParent()
        if btask == 'goto_first':
            v.goto_first()
        elif btask == 'goto_last':
            v.goto_last()
        elif btask == 'config':
            v.videoviewer_config()
        elif btask == 'play_fwd':
            v.play_fwd()
            self.btn.set_toggle(btask)
            self.btn.set_bitmap2(btask)
            self.btn.refresh_button()
            
        elif btask == 'play_rev':
            v.play_rev()
            self.btn.set_toggle(btask)
            self.btn.set_bitmap2(btask)
            self.btn.refresh_button()
            
        elif btask == 'stop_play':
            v.stop_play()
            self.reset_btn_toggle_bitmap()
        elif btask == 'step_fwd':
            v.stop_play()            
            v.step_fwd()
        elif btask == 'step_rev':
            v.stop_play()            
            v.step_rev()            
        else:
            print btask
            
    def reset_btn_toggle_bitmap(self):
        self.btn.set_toggle('')
        self.btn.set_bitmap2('')
        self.btn.refresh_button()
    

               
            

