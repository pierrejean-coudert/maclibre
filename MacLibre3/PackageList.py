#
#  PackageList.py
#  MacLibre3
#
#  Created by Ezra.
#
#  These classes handle the UI for choosing packages to be installed.

from Foundation import *

import objc
import AppKit
import tools

from Prefs import Prefs

objc.setVerbose(1)



class action():
    def __init__(self, name):
        self.name=name

class PackageListItem(NSObject):
    
    def init_(self, type, value, category = None):
        self.type=type
        self.value=value
        self.category=category
        return self
        
    def indexPath(self):#, arg1='None', arg2='N2'):
        #print arg1
        #print arg2
        return 2
    
class PackageList (NSObject):
    actions=[]
    #pkgs=NSSet.alloc().init()
    packages=[]
    dist=None
    
    def load_(self, distribution, installed):
        """Load the lists of packages and installed packages into instalnce variables."""
        #self._classInfo = getClassList()
        #self.refreshClasses()
        self.dist=distribution
        self.inst=installed
        prefs=Prefs()
        #self.values=['v1','v2','v3']
        #a=action.alloc().init_('a')
        #b=action.alloc().init_('b')
        #c=action.alloc().init_('c')
        #print 'theActions'
        #self.actions=[a,b,c]
        #self.pkgs=NSSet.setWithArray_([[a,b],b,c])
        #print self.pkgs
        #self.selectedx=1
        #self.actions=["","INSTALL"]
        
        pkgs = self.dist.categories[0].packages
        for pkg in pkgs:
            pkg.fileSize=str(pkg.installations[0].file.size/100000/10.0)+'MB'
            pkg.sizeOnDisk=str(pkg.installations[0].sizeOnDisk/100000/10.0)+'MB'
            pkg.logo=NSImage.imageNamed_(pkg.logoImageFile)
            pkg.todo=" "
            pkg.actions=[" ",prefs.getTodo(pkg.name,'')]
        self.packages=pkgs
        return self

    def outlineView_child_ofItem_(self, outlineview, index, item):
        """Delegate function.  Returns the 'index'th category or the 'index'th package in a given category."""
        #NSLog('outlineView_child_ofItem_')
        #NSLog(str(item))
        if item is None:
            return PackageListItem.alloc().init_(True, index).retain()
        else:
            return PackageListItem.alloc().init_(False, index, item.value).retain()

    def outlineView_isItemExpandable_(self, outlineview, item):
        """Delegate function.  If 'item' is a category, it is expandable.  Otherwise, it isn't."""
        #NSLog('outlineView_isItemExpandable_')
        #NSLog(str(item))
        return item.type

    def outlineView_numberOfChildrenOfItem_(self, outlineview, item):
        """Delegate function.  Returns the number of categories or the number of pakcages in category 'item'."""
        #NSLog('outlineView_numberOfChildrenOfItem_')
        #NSLog(str(item))
        if item is None:
            return len(self.dist.categories)
        elif item.type:
            return len(self.dist.categories[item.value].packages)
        else:
            return -1
        #return len(self._classTree[unwrap_object(item)])

    def outlineView_objectValueForTableColumn_byItem_(self, outlineview, column, item):
        """Delegate function.  Given a column and row, return what should be displayed there."""
        #NSLog(str(column.identifier()))
        if item is None:
            return 'None'
        elif item.type:
            if outlineview.tableColumns().index(column) is not 0:
                return ''
            return self.dist.categories[item.value].name
        else:
            #NSLog(str(dir(self.dist.categories[item.category].packages[item.value])))
            package=self.dist.categories[item.category].packages[item.value]
            #NSLog(package.name)
            #NSLog(str(package.version))
            #a=NSPopUpButtonCell.alloc().initTextCell_pullsDown_('xyzzy',False)
            #print a
            return {0:package.name,
                    1:package.version,
                    2:package.todo,
                    4:tools.byteSizeToReadableSize(package.installations[0].sizeOnDisk),
                    5:'c2',
                    3:tools.byteSizeToReadableSize(package.installations[0].file.size)}[outlineview.tableColumns().index(column)]

    def outlineView_shouldEditTableColumn_item_(self, outlineview, column, item):
        """Delegate function.  Make everything not editable."""
        return False
        
    def outlineView_shouldSelectItem_(self, outlineview, item):
        """Delegate function.  Categories can't be selected, selecting a package sets its todo appropriately."""
        if item.type:
            return False
        else:
            package=self.dist.categories[item.category].packages[item.value]
            prefs=Prefs()
            package.todo = prefs.getTodo(package.name, package.todo)
            return True
            
    #The next 3 functions handle the package confirmation view.
    
    def numberOfRowsInTableView_(self, tableview):
        self.targets=[]
        [self.targets.extend([package for package in category.packages if package.todo!=" "]) for category in self.dist.categories]
        return len(self.targets)
        
    def tableView_objectValueForTableColumn_row_(self, tableview, column, row):
        if tableview.tableColumns().index(column)==0:
            return self.targets[row].name
        else:
            return self.targets[row].todo
        
    def tableView_shouldEditTableColumn_row_(self, tableview, column, row):
        return False