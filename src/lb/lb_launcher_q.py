#!/usr/bin/env python
#
# Copyright (c) 2012, Luca Burgazzoli
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met: 
# 
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer. 
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution. 
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL 
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER 
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, 
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE 
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

import os
import sys
import argparse

import xml.etree.ElementTree as ET

from PySide import QtCore
from PySide import QtGui
        
################################################################################
#
################################################################################

class LBArgumentParser(argparse.ArgumentParser):
    def __init__(self,appid):
        super(LBArgumentParser,self).__init__()
        
        cfgroot    = os.path.join(os.getenv("HOME"),'/.lb')
        appcfgroot = os.path.join(cfgroot,appid)
         
        self.add_argument(
            '-s',
            '--settings-root',
            help='the settings root',
            default=appcfgroot)
            
    def parse(self):
        return self.parse_args()
        
################################################################################
#
################################################################################

class LBLauncher(QtGui.QSystemTrayIcon):
    """
    LBLauncher.
    """
    def __init__(self):
        QtGui.QSystemTrayIcon.__init__(self)
        self.cfg     = None
        self.ticons  = None
        self.cfgpath = None
        self.actions = {}
    
    ############################################################################
    #
    ############################################################################
    
    def setup(self,settings):
        self.cfgroot = settings
        self.cfgpath = os.path.join(self.cfgroot,'settings.xml')
        if(os.path.exists(self.cfgpath)):
            self.cfg    = ET.parse(self.cfgpath)
            self.ticons = self.cfg.getroot().find('tray-icons')
            
            self.__create_menu()
            
            self.setIcon(self.__get_icon_path('main'))
            
            return True
        else:
            return False   
        
    ############################################################################
    #
    ############################################################################
    
    def __refresh(self):
        pass
    
    def __terdown(self):
        QtCore.QCoreApplication.instance().quit()
        
    ############################################################################
    #
    ############################################################################
        
    def __create_menu(self):
        self.actions['refresh'] = self.__create_action('Refresh','refresh',self.__refresh)
        self.actions['quit'   ] = self.__create_action('Quit'   ,'quit'   ,self.__terdown)
        
        self.trayIconMenu = QtGui.QMenu()
        self.trayIconMenu.addAction(self.actions['refresh'])
        self.trayIconMenu.addSeparator()
        self.trayIconMenu.addAction(self.actions['quit'])
        
        self.setContextMenu(self.trayIconMenu)
            
    def __create_action(self,text,icon=None,slot=None):
        action = QtGui.QAction(self.tr(text),self)
        if icon is not None:
            action.setIcon(self.__get_icon_path(icon))
                
        if slot is not None:
            action.triggered.connect(slot)
            
        return action
        
    def __get_icon_path(self,icon):
        if(self.ticons.find(icon) is not None):
            return QtGui.QIcon(os.path.join(self.cfgroot,self.ticons.find(icon).text))
        else:
            return None
            
################################################################################
#
################################################################################
    
if __name__=='__main__':
    config = LBArgumentParser('lb_launcher')
    args   = config.parse()
    
    if(args.settings_root):
        app = QtGui.QApplication(sys.argv)
        win = LBLauncher()
        if(win.setup(args.settings_root)):
            win.show()
            sys.exit(app.exec_())
