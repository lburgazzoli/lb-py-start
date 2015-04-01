#!/usr/bin/env python3
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
import sys
import os
import yaml


class PyRun:
    def __init__(self, path):
        self.cfgroot = path
        self.cfgpath = os.path.join(path, 'settings.yaml')

    ############################################################################
    #
    ############################################################################

    def run(self):
        if os.path.exists(self.cfgpath):
            stream = open(self.cfgpath, 'r')
            settings = yaml.load(stream)

            if sys.argv[1] == 'list':
                for action in settings['actions']:                
                    print(action['name'])
                for action in settings['actions']:
                    if 'alias' in action:
                        print(action['alias'])
            else:
                for action in settings['actions']:
                    if action['type'] == 'mate-terminal':
                        if sys.argv[1] == action['name']:
                            self.run_mate_terminal(action)
                        if 'alias' in action:
                            if sys.argv[1] == action['alias']:
                                self.run_mate_terminal(action)         

            stream.close()

    def run_mate_terminal(self, action):
        command = 'mate-terminal'
        command_args = [
            "--profile=%s" % (action['profile']),
            "--title=%s"   % (action['title']  ),
            "--command=%s" % (action['command'])
        ]

        if action['tab']:
            command_args.insert(0, '--tab')
        else:
            command_args.insert(0, '--window')

        self.__exec(command, command_args)

    ############################################################################
    #
    ############################################################################

    def __exec(self, command, command_args):
        os.spawnvp(os.P_NOWAIT, command, [command] + command_args)
        os.wait3(os.WNOHANG)

################################################################################
#
################################################################################

if __name__ == '__main__':
    cfgroot = os.getenv('PYRUN_CFG_ROOT')
    if not cfgroot:
        cfgroot = os.path.join(os.getenv('HOME'), '.config/lb/pyrun')

    app = PyRun(cfgroot)
    app.run()
