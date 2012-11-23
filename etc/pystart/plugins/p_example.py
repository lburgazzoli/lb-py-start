
import lb

################################################################################
#
################################################################################

def plugin_new(**kwargs):
    return ExamplePlugin()

###############################################################################
#
################################################################################

class ExamplePlugin(lb.IPlugin):
    def __init__(slef):
        super(ExamplePlugin,self).__init__()
    
    def setup(self,**kwargs):
        print "ExamplePlugin::setup"
        print kwargs
    
    def run(self,**kwargs):
        print "ExamplePlugin::run"
        print kwargs
