#
#  Copyright 2012 the original author or authors.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import os
import sys
import argparse

import ConfigParser
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

    def __teardown(self):
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
        """
        Build main menu
        - read items from xml settings
        - autogenerate menu for remmina settings
        """
        self.trayIconMenu = QtGui.QMenu()

        self.__fill_menu(self.cfg.getroot(),self.trayIconMenu)
        self.trayIconMenu.addSeparator()
        self.__fill_remmina_menu(self.trayIconMenu)
        self.trayIconMenu.addSeparator()
        #self.trayIconMenu.addAction(self.__create_action('Refresh','refresh',self.__refresh))
        self.trayIconMenu.addAction(self.__create_action('Quit'   ,'quit'   ,self.__teardown))

        self.setContextMenu(self.trayIconMenu)


    def __create_action(self,text,icon=None,slot=None):
        action = QtGui.QAction(self.tr(text),self)
        if icon is not None:
            ic = self.__get_icon(icon)
            if ic:
                action.setIcon(ic)

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
        """
        XML configuration example:

            <item label="Terminal" cmd="/usr/bin/open" icon="terminal">
                <arg value="/Applications/Utilities/Terminal.app"/>
            </item>
        """
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
                            'args' : [ arg.get('value') for arg in item if arg.tag == 'arg'] 
                        })
                    ))
                else:
                    tmpmn = QtGui.QMenu(label);
                    if icon is not None:
                        tmpmn.setIcon(self.__get_icon(icon))

                    mn.addMenu(tmpmn)
                    mn = tmpmn

            self.__fill_menu(item,mn)


    def __fill_remmina_menu(self,menu):
        """
        This method reads remmina's configuration files in $HOME/.remmina and 
        creates an entry for each file.

            [remmina] 
            server=serner_name 

        """
        rroot = os.path.join(os.getenv("HOME"),'.remmina')
        if(os.path.exists(rroot)):
            tmpmn = QtGui.QMenu("Remmina");
            rdpi = self.__get_icon('remmina')
            if rdpi is not None:
                tmpmn.setIcon(rdpi)

            menu.addMenu(tmpmn)
            for fname in os.listdir(rroot):
                if fname.endswith('.remmina'):
                    config = ConfigParser.RawConfigParser()
                    config.read(os.path.join(rroot,fname))

                    if config.has_section('remmina'):
                        tmpmn.addAction(self.__create_action(
                            config.get('remmina','server'),
                            'remmina',
                            partial(self.__exec, {
                                'cmd'  : '/usr/bin/remmina',
                                'args' : [ '-c',os.path.join(rroot,fname) ]
                            })
                        ))

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
