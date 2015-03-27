#!/usr/bin/python3

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
            stream = open(self.cfgpath , 'r') 
            settings = yaml.load(stream)

            for action in settings['actions']:
                if action['name'] == sys.argv[1] and action['type'] == 'mate-terminal':
                   self.run_mate_terminal(action)         

            stream.close()

    def run_mate_terminal(self, action):
        print("action = %s"  % action)

        command = 'mate-terminal'
        command_args = [
            "--profile=%s" % (action['profile']),
            "--title=%s"   % (action['title']  ),
            "--command=%s" % (action['command'])
        ]

        if action['tab'] == True:
            command_args.insert(0, '--tab')
        else:
            command_args.insert(0, '--window')

        PyRun.__exec(command, command_args)

    ############################################################################
    #
    ############################################################################

    def __exec(command, command_args):
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
