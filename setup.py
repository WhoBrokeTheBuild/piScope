#!/usr/bin/env python
import os
import re

rootdir = os.path.abspath(os.path.dirname(__file__))

from setuptools import setup, find_packages


def version():
    VERSIONFILE = os.path.join('python', 'ifigure', '__init__.py')
    initfile_lines = open(VERSIONFILE, 'rt').readlines()
    VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
    for line in initfile_lines:
        mo = re.search(VSRE, line, re.M)
        if mo:
            return mo.group(1)
    raise RuntimeError('Unable to find version string in %s.' % (VERSIONFILE,))

def install_requires():
    fname = os.path.join(rootdir, 'requirements.txt')
    if not os.path.exists(fname):
        return []
    fid = open(fname)
    requirements = fid.read().split('\n')
    fid.close()
    return requirements

platforms = """
Mac OS X
Linux
"""
metadata = {'name': 'piScope',
            'version': version(),
            'description': 'piScope data analysis workbench',
            'download_url': 'https://github.com/piScope/piScope',            
            'author': 'S. Shiraiwa',
            'author_email': 'shiraiwa@princeton.edu',
            'classifiers': ['Development Status :: 4 - Beta',
                            'Intended Audience :: Developers',
                            'Topic :: Scientific/Engineering :: Physics',
                            'License :: OSI Approved :: GPL-3',
                            'Programming Language :: Python :: 3.7',
                            'Programming Language :: Python :: 3.8',
                            'Programming Language :: Python :: 3.9',
                            'Programming Language :: Python :: 3.10', ],
            }

def run_setup():
    setup_args = metadata.copy()
    install_req = install_requires()
    
    setup(
        install_requires=install_req,
        packages=['python/ifigure'],
        extras_require={},
        package_data={},
        entry_points={},
        **setup_args)

def main():
    run_setup()
            
if __name__ == '__main__':
    main()
