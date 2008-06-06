
from Foundation import *
from AppKit import *
import objc
from Parser import Parser

class PackageList(NSObject):
    def __init__(self):
        from MacLibre3 import MacLibre3
        #next 3 lines from GUI_MacLibreWizard.py
        NSLog('init')
        parserWeb = Parser(MacLibre3.maclibre.xmlMaclibrePath)
        parserUser = Parser(MacLibre3.maclibre.xmlUserPath)
        self.distribution = parserWeb.parse()
        return self
        
    def awakeFromNib(self):
        NSLog('awakeFromNib')
    
    @objc.IBAction
    def outlineView_numberOfChildrenOfItem_(self, item):
        NSLog(str(item))
        return 0
        if item is None:
            return 3#len(self.distribution.categories)
        else:
            return 0
            
    @objc.IBAction
    def outlineView_isItemExpandable_(self, item):
        NSLog('IsItemExpandable')
        return False
        
    @objc.IBAction
    def outlineView_child_ofItem_(self, child, item):
        NSLog('child_ofItem')
        if item == None:
            return child
        return None
        
    @objc.IBAction
    def outlineView_objectValueForTableColumn_byItem_(self, column, item):
        NSLog('objectValueForTableColumn_byItem_')
        return self.distribution.categories[item].name