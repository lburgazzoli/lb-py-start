#
# Copyright 2014 lb.
#
# Licensed under the Apache License, Version 2.0 (the "License");
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
    def __init__(self, path):
        QtGui.QSystemTrayIcon.__init__(self)

        self.cfgroot = path

        settings_path = os.path.join(path, 'settings.json')
        if os.path.exists(settings_path):
            settings_fp = open(settings_path)
            settings = json.load(settings_fp)

            self.ticons = settings['icons']
            self.tcommands = settings['commands']
            self.tvars = settings['vars']

            menu = self.__fill_menu(settings['items'], QtGui.QMenu())
            menu.addSeparator()
            menu.addAction(
                self.__create_action(
                    'Quit',
                    'launcher-quit',
                    self.__teardown
                )
            )

            self.setContextMenu(menu)
            self.setIcon(self.__get_icon('launcher'))

            settings_fp.close()

    ############################################################################
    #
    ############################################################################

    @staticmethod
    def __teardown():
        QtCore.QCoreApplication.instance().quit()

    @staticmethod
    def __exec(data):
        command = data['cmd']
        command_args = data['args']

        if os.name == 'nt':
            os.spawnv(os.P_NOWAIT, command, [command] + command_args)
        else:
            os.spawnvp(os.P_NOWAIT, command, [command] + command_args)
            os.wait3(os.WNOHANG)

    ############################################################################
    #
    ############################################################################

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
                ipath = self.ticons[icon] % self.tvars
            else:
                ipath = icon


            if os.path.isabs(ipath):
                return QtGui.QIcon(ipath)
            else:
                return QtGui.QIcon(os.path.join(self.cfgroot, ipath))
        else:
            return None

    def __fill_menu(self, items, menu):
        for item in items:
            label = item['label']
            mn = menu
            icon = None
            if 'icon' in item.keys():
                icon = item['icon']

            if label == 'separator':
                menu.addSeparator()
            elif 'command' in item.keys():
                command = item['command']
                command_args = []

                if command in self.tcommands:
                    command = self.tcommands[command] % self.tvars
                if 'command-args' in item:
                    command_args = item['command-args']
                    for i in range(0, len(command_args)):
                        command_args[i] = command_args[i] % self.tvars

                mn.addAction(self.__create_action(
                    label,
                    icon,
                    functools.partial(self.__exec, {
                        'cmd': command,
                        'args': command_args
                    })
                ))
            else:
                tmpmn = QtGui.QMenu(label)
                if icon:
                    tmpmn.setIcon(icon)

                mn.addMenu(tmpmn)
                mn = tmpmn

            if 'items' in item.keys():
                self.__fill_menu(item['items'], mn)

        return menu

################################################################################
#
################################################################################

if __name__ == '__main__':
    cfgroot = os.getenv('PYSTART_CFG_ROOT')
    if not cfgroot:
        cfgroot = os.getenv('HOME') + '/.config/pystart'

    app = QtGui.QApplication(sys.argv)
    app.setAttribute(QtCore.Qt.AA_DontShowIconsInMenus, False)

    win = PyStart(cfgroot)
    win.show()

    sys.exit(app.exec_())
