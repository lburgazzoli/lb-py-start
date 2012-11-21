#!/usr/bin/python

import os
import sys
import gtk
import appindicator as AI
import xml.etree.ElementTree as ET

################################################################################
#
################################################################################

class LBLauncher:
    def __init__(self):
        self.__menu = gtk.Menu()

    def build(self,cfg):
        if os.path.exists(cfg):
            tree = ET.parse(cfg)
            self.__process(tree.getroot(),self.__menu)

    def run(self):
        self.__add_menu_separator(self.__menu)
        self.__add_menu_item(
            k_menu    = self.__menu,
            k_label   = "Quit",
            k_submenu = False,
            k_icon    = gtk.STOCK_QUIT,
            k_data    = '__QUIT'
        )

        ind = AI.Indicator("lb_menu",gtk.STOCK_NETWORK,AI.CATEGORY_APPLICATION_STATUS)
        ind.set_label("Launch")
        ind.set_status(AI.STATUS_ACTIVE)
        ind.set_menu(self.__menu)
        gtk.main()

    def __process(self,root,menu):
        for item in root:
            label = item.get('label')
            cmd   = item.get('cmd')
            icon  = item.get('icon')
            mn    = menu
            if label:
                if label == 'separator':
                    self.__add_menu_separator(menu)
                elif cmd:
                    if not icon:
                        icon = gtk.STOCK_EXECUTE

                    args = []
                    for arg in item:
                        if arg.tag == 'arg':
                            args.append(arg.get('value'))

                    mn = self.__add_menu_item(
                        k_menu    = menu,
                        k_label   = label,
                        k_submenu = False,
                        k_icon    = gtk.STOCK_EXECUTE,
                        k_data    = {
                            'cmd'  : cmd,
                            'args' : args
                        }
                    )
                else:
                    if not icon:
                        icon = gtk.STOCK_DIRECTORY

                    mn = self.__add_menu_item(
                        k_menu    = menu ,
                        k_label   = label,
                        k_submenu = True,
                        k_icon    = gtk.STOCK_DIRECTORY
                    )

            self.__process(item,mn)

    def __add_menu_item(self,**kvargs):
        mn = kvargs['k_menu'];

        mi = gtk.ImageMenuItem(kvargs['k_label'])
        mi.set_sensitive(True)

        if 'k_icon' in kvargs:
            img = gtk.image_new_from_stock(kvargs['k_icon'],gtk.ICON_SIZE_MENU)
            img.show()
            mi.set_image(img)

        if 'k_data' in kvargs:
            mi.connect("activate",self.__menuitem_callback,kvargs['k_data'])

        if 'k_submenu' in kvargs:
            if kvargs['k_submenu']:
                mn = gtk.Menu()
                mi.set_submenu(mn)

        mi.show()
        kvargs['k_menu'].append(mi)

        return mn

    def __add_menu_separator(self,menu):
        sep = gtk.SeparatorMenuItem()
        sep.show()
        menu.append(sep)

    def __menuitem_callback(self,w,item):
        if item:
            if item == '__QUIT':
                sys.exit(0)
            else:
                cmd  = item['cmd']
                args = item['args']
                os.spawnvp(os.P_NOWAIT,cmd,[cmd] + args)
                os.wait3(os.WNOHANG)
        else:
            pass

################################################################################
#
################################################################################

if __name__ == '__main__':
    lbl = LBLauncher()

    if len(sys.argv) == 2:
        lbl.build(sys.argv[1])
    else:
        lbl.build(os.getenv("HOME") + "/.lb_launcher/settings.xml");

    lbl.run()

