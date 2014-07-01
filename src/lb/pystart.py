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
import json

import functools

from PySide import QtCore
from PySide import QtGui

################################################################################
#
################################################################################

class PyStart(QtGui.QSystemTrayIcon):
    def __init__(self):
        QtGui.QSystemTrayIcon.__init__(self)
        self.json_data      = None
        self.cfg            = None
        self.ticons         = None
        self.tcommands      = None
        self.cfgpath        = None
        self.cfgroot        = None
        self.tray_icon_menu = None

    ############################################################################
    #
    ############################################################################

    def setup(self, settings):
        self.cfgroot = settings
        self.cfgpath = os.path.join(self.cfgroot, 'settings.json')
        if os.path.exists(self.cfgpath):
            self.json_data = open(self.cfgpath)
            self.cfg       = json.load(self.json_data) 
            self.ticons    = self.cfg['icons']
            self.tcommands = self.cfg['commands']

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
        self.tray_icon_menu = QtGui.QMenu()

        self.__fill_menu(self.cfg['items'], self.tray_icon_menu)
        self.tray_icon_menu.addSeparator()
        self.tray_icon_menu.addAction(
            self.__create_action(
                'Quit',
                'launcher-quit',
                self.__teardown
            )
        )

        self.setContextMenu(self.tray_icon_menu)

    def __create_action(self, text, icon=None, slot=None):
        action = QtGui.QAction(self.tr(text), self)
        if icon:
            ic = self.__get_icon(icon)
            if ic:
                action.setIcon(ic)
                action.setIconVisibleInMenu(True)

        if slot is not None:
            action.triggered.connect(slot)

        return action

    def __get_icon(self, icon):
        if icon is not None:
            if icon in self.ticons.keys():
                ipath = self.ticons[icon]
            else:
                ipath = icon

            if os.path.isabs(ipath):
                return QtGui.QIcon(ipath)
            else:
                return QtGui.QIcon(os.path.join(self.cfgroot, ipath))
        else:
            return None

    ############################################################################
    #
    ############################################################################

    def __fill_menu(self, items, menu):
        for item in items:
            label = item['label']
            mn    = menu
            icon  = None

            if label == 'separator':
                menu.addSeparator()
            elif 'command' in item.keys():
                command = item['command']
                if command in self.tcommands:
                    command = self.tcommands[command]

                mn.addAction(self.__create_action(
                    label,
                    item['icon'],
                    functools.partial(self.__exec, {
                        'cmd'  : command,
                        'args' : item['command-args']
                    })
                ))
            else:
                tmpmn = QtGui.QMenu(label)
                if 'icon' in item.keys():
                    tmpmn.setIcon(item['icon'])

                mn.addMenu(tmpmn)
                mn = tmpmn

            if 'items' in item.keys():
                self.__fill_menu(item['items'], mn)

################################################################################
#
################################################################################

if __name__=='__main__':
    cfgroot = os.getenv("PYSTART_CFG_ROOT")
    if not cfgroot:
        cfgroot = os.path.join(os.getenv("HOME"), '/.config/pystart')

    app = QtGui.QApplication(sys.argv)
    app.setAttribute(QtCore.Qt.AA_DontShowIconsInMenus, False);

    win = PyStart()
    win.setup(cfgroot)
    win.show()

    sys.exit(app.exec_())
