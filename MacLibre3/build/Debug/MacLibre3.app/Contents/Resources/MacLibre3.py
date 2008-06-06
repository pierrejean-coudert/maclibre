from Foundation import *
from AppKit import *
import objc
import sys
from MacLibre import *
from Parser import Parser

class MacLibre3(NSObject):
    tabs = objc.IBOutlet()
    packList=objc.IBOutlet()
    maclibre=MacLibre()
    
    @objc.IBAction
    def nextPage_(self, sender):
        if self.tabs.indexOfTabViewItem_(self.tabs.selectedTabViewItem()) == 0:
            if self.maclibre.chooseWebXml():
                parserWeb = Parser(self.maclibre.xmlMaclibrePath)
                parserUser = Parser(self.maclibre.xmlUserPath)
                self.packList.dataSource().load_(parserWeb.parse())
                self.tabs.selectNextTabViewItem_(1)
        else:
            self.tabs.selectNextTabViewItem_(1)

    @objc.IBAction
    def previousPage_(self, sender):
        self.tabs.selectPreviousTabViewItem_(1)
        
    @objc.IBAction
    def quit_(self, sender):
        sys.exit()

