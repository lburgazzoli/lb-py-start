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

class IPlugin:
    def __init__(self):
        pass
    
    def setup(self,**kwargs):
        pass
    
    def run(self,**kwargs):
        pass

################################################################################
#
################################################################################

class RemminaPlugin(IPlugin):	
	def __init__(self):
		self.rmhome = os.path.join(os.getenv("HOME"),'.remmina')
    
    def setup(self,**kwargs):
        pass
    
    def run(self,**kwargs):
        pass

