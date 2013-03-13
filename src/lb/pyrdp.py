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
import ConfigParser

from PySide import QtGui

################################################################################
#
################################################################################

class PyRdp(QtGui.QWidget):
    def __init__(self):
        super(PyRdp, self).__init__()
        self.combo = None
        self.text = None
        self.remf = {}

    def initui(self):

        self.combo = QtGui.QComboBox(self)
        self.combo.setEditable(True)
        self.__load_remmina()

        vbox = QtGui.QVBoxLayout(self)
        vbox.addWidget(self.combo)

        self.setLayout(vbox)
        self.setWindowTitle('PyRdp')

    def __load_remmina(self):
        rroot = os.path.join(os.getenv("HOME"),'.remmina')
        if(os.path.exists(rroot)):
            for fname in os.listdir(rroot):
                config = ConfigParser.RawConfigParser()
                config.read(os.path.join(rroot,fname))
                if config.has_section('remmina'):
                    srv = config.get('remmina','server')
                    self.combo.addItem(srv)
                    self.remf[srv] = os.path.join(rroot,fname)


################################################################################
#
################################################################################

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    wid = PyRdp()
    wid.initui()
    wid.show()

    sys.exit(app.exec_())
