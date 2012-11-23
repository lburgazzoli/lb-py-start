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

import xml.etree.ElementTree
from functools import partial

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

class PyStart(QtGui.QSystemTrayIcon):
    """
    PyStart.
    """
    def __init__(self):
        QtGui.QSystemTrayIcon.__init__(self)
        self.cfg      = None
        self.ticons   = None
        self.cfgpath  = None
    
    ############################################################################
    #
    ############################################################################
    
    def setup(self,settings):
        self.cfgroot = settings
        self.cfgpath = os.path.join(self.cfgroot,'settings.xml')
        if(os.path.exists(self.cfgpath)):
            self.cfg    = xml.etree.ElementTree.parse(self.cfgpath)
            self.ticons = self.cfg.getroot().find('tray-icons')
            
            self.__create_menu()
            
            self.setIcon(self.__get_icon('main'))
        
    ############################################################################
    #
    ############################################################################
    
    def __refresh(self):
        pass
    
    def __terdown(self):
        QtCore.QCoreApplication.instance().quit()
        
    def __exec(self,data):
        cmd  = data['cmd']
        args = data['args']
        
        if os.name == "nt":
            os.spawnv(os.P_NOWAIT,cmd,[cmd] + args)
        else:
            os.spawnvp(os.P_NOWAIT,cmd,[cmd] + args)
            os.wait3(os.WNOHANG)
        
    ############################################################################
    #
    ############################################################################
                 
    def __create_menu(self):
        
        self.trayIconMenu = QtGui.QMenu()
        
        self.__fill_menu(self.cfg.getroot(),self.trayIconMenu)
        
        self.trayIconMenu.addSeparator()
        self.trayIconMenu.addAction(self.__create_action('Refresh','refresh',self.__refresh))
        self.trayIconMenu.addAction(self.__create_action('Quit'   ,'quit'   ,self.__terdown))
        
        self.setContextMenu(self.trayIconMenu)
     
                 
    def __create_action(self,text,icon=None,slot=None):
        action = QtGui.QAction(self.tr(text),self)
        if icon is not None:
            action.setIcon(self.__get_icon(icon))
                
        if slot is not None:
            action.triggered.connect(slot)
            
        return action
        
    def __get_icon(self,icon):
        if(self.ticons.find(icon) is not None):
            return QtGui.QIcon(os.path.join(self.cfgroot,self.ticons.find(icon).text))
        else:
            return None
        
    ############################################################################
    #
    ############################################################################
        
    def __fill_menu(self,root,menu):
        for item in root:
            label  = item.get('label')
            cmd    = item.get('cmd'  )
            icon   = item.get('icon' )
            mn     = menu
            
            if label:
                if label == 'separator':
                    menu.addSeparator()
                elif cmd is not None:
                    mn.addAction(self.__create_action(
                        label,
                        icon,
                        partial(self.__exec, { 
                            'cmd'  : cmd, 
                            'args' : [ arg.get('value') for arg in item if arg.tag == 'arg'] })
                    ))
                else:
                    tmpmn = QtGui.QMenu(label);
                    if icon is not None:
                        tmpmn.setIcon(self.__get_icon(icon))
                        
                    mn.addMenu(tmpmn)
                    mn = tmpmn

            self.__fill_menu(item,mn)
            
################################################################################
#
################################################################################
    
if __name__=='__main__':
    config = LBArgumentParser('lb_launcher')
    args   = config.parse()
    
    if(args.settings_root):
        app = QtGui.QApplication(sys.argv)
        
        win = PyStart()
        win.setup(args.settings_root)
        win.show()
        
        sys.exit(app.exec_())
