#
#  Copyright 2014 lb.
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

import configparser
import json
import pprint

from functools import partial

from PySide import QtCore
from PySide import QtGui

################################################################################
#
################################################################################

class PyStartArgParser(argparse.ArgumentParser):
    def __init__(self,appid):
        super(PyStartArgParser,self).__init__()

        cfgroot    = os.path.join(os.getenv("HOME"), '/.config/lb')
        appcfgroot = os.path.join(cfgroot, appid)

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
        self.json_data      = None
        self.cfg            = None
        self.ticons         = None
        self.cfgpath        = None
        self.cfgroot        = None
        self.tray_icon_menu = None

    ############################################################################
    #
    ############################################################################

    def setup(self,settings):
        self.cfgroot = settings
        self.cfgpath = os.path.join(self.cfgroot,'settings.json')
        if os.path.exists(self.cfgpath):
            self.json_data = open(self.cfgpath)
            self.cfg       = json.load(self.json_data) 
            self.ticons    = self.cfg['icons']

            self.__create_menu()

            self.setIcon(self.__get_icon('launcher'))

            self.json_data.close()

    ############################################################################
    #
    ############################################################################

    @staticmethod
    def __teardown():
        QtCore.QCoreApplication.instance().quit()

    @staticmethod
    def __exec(data):
        command      = data['cmd']
        command_args = data['args']

        if os.name == "nt":
            os.spawnv(os.P_NOWAIT, command, [command] + command_args)
        else:
            os.spawnvp(os.P_NOWAIT, command, [command] + command_args)
            os.wait3(os.WNOHANG)

    ############################################################################
    #
    ############################################################################

    def __create_menu(self):
        """
        Build main menu
        - read items from json settings
        - autogenerate menu for remmina settings (not yet)
        """
        self.tray_icon_menu = QtGui.QMenu()

        self.__fill_menu(self.cfg['items'],self.tray_icon_menu)
        self.tray_icon_menu.addSeparator()
        self.__fill_remmina_menu(self.tray_icon_menu)
        self.tray_icon_menu.addSeparator()
        self.tray_icon_menu.addAction(self.__create_action(
            'Quit', 
            'launcher-quit', 
            self.__teardown)
        )

        self.setContextMenu(self.tray_icon_menu)

    def __create_action(self, text, icon=None, slot=None):
        action = QtGui.QAction(self.tr(text), self)
        if icon is not None:
            ic = self.__get_icon(icon)
            if ic:
                action.setIcon(ic)
                action.setIconVisibleInMenu(True)

        if slot is not None:
            action.triggered.connect(slot)

        return action

    def __get_icon(self, icon):
        if icon in self.ticons.keys():
            ipath = self.ticons[icon]
        else: 
            ipath = icon

        if os.path.isabs(ipath):
            return QtGui.QIcon(ipath)
        else:
            return QtGui.QIcon(os.path.join(self.cfgroot, ipath))

    ############################################################################
    #
    ############################################################################

    def __fill_menu(self, items, menu):
        """
        "items" : 
        [ 
            { 
                "label" : "section1",
                "icon"  : "folder",
                "items" :
                [
                    {
                        "label"        : "command_1",  
                        "icon"         : "terminal",
                        "command"      : "run_ssh.sh",
                        "command-args" : [ "server1" ]
                    },
                    {
                        "label"        : "command_2",  
                        "icon"         : "terminal",
                        "command"      : "run_ssh.sh",
                        "command-args" : [ "server2" ]
                    }
                ] 
            }
        ]
        """        
        for item in items:
            label = item['label']
            mn    = menu

            if label == 'separator':
                menu.addSeparator()
            elif 'command' in item.keys():
                mn.addAction(self.__create_action(
                    label,
                    item['icon'],
                    partial(self.__exec, {
                        'cmd'  : item['command'],
                        'args' : item['command-args']
                    })
                ))
            else:
                tmpmn = QtGui.QMenu(label);
                if 'icon' in item.keys():
                    tmpmn.setIcon(self.__get_icon(item['icon']))

                mn.addMenu(tmpmn)
                mn = tmpmn

            if 'items' in item.keys():
                self.__fill_menu(item['items'], mn)

    def __fill_remmina_menu(self,menu):
        """
        This method reads remmina's configuration files in $HOME/.remmina and
        creates an entry for each file.

            [remmina]
            server=serner_name

        """
        remroot = os.path.join(os.getenv("HOME"),'.remmina')
        if os.path.exists(remroot):
            tmpmn = QtGui.QMenu("remmina");
            rdpi  = self.__get_icon('remmina')
            if rdpi is not None:
                tmpmn.setIcon(rdpi)

            menu.addMenu(tmpmn)
            for fname in os.listdir(remroot):
                if fname.endswith('.remmina'):
                    config = configparser.ConfigParser()
                    config.read(os.path.join(remroot,fname))

                    if config.has_section('remmina'):
                        tmpmn.addAction(self.__create_action(
                            config.get('remmina','name'),
                            'remmina',
                            partial(self.__exec, {
                                'cmd'  : '/usr/bin/remmina',
                                'args' : [ '-c',os.path.join(remroot,fname) ]
                            })
                        ))

################################################################################
#
################################################################################

if __name__=='__main__':
    config = PyStartArgParser('lb_launcher')
    args   = config.parse()

    if args.settings_root:
        app = QtGui.QApplication(sys.argv)
        app.setAttribute(QtCore.Qt.AA_DontShowIconsInMenus, False);

        win = PyStart()
        win.setup(args.settings_root)
        win.show()

        sys.exit(app.exec_())
