from Foundation import *

import objc
import AppKit
objc.setVerbose(1)


class PackageListItem():
    def __init__(self, type, value, category = None):
        self.type=type
        self.value=value
        self.category=category
        
class PackageList (NSObject):


    def load_(self, distribution):
        #self._classInfo = getClassList()
        #self.refreshClasses()
        self.dist=distribution
        return self


    def outlineView_child_ofItem_(self, outlineview, index, item):
        if item is None:
            return PackageListItem(True, index)
        else:
            return PackageListItem(False, index, item.value)

    def outlineView_isItemExpandable_(self, outlineview, item):
        return item.type



    def outlineView_numberOfChildrenOfItem_(self, outlineview, item):
        if item is None:
            return len(self.dist.categories)
        elif item.type:
            return len(self.dist.categories[item.value])
        else:
            return 0
        #return len(self._classTree[unwrap_object(item)])

    def outlineView_objectValueForTableColumn_byItem_(self, outlineview, column, item):
        NSLog(str(item))
        if item.type:
            return self.dist.categories[item.value].name
        else:
            return self.dist.categories[item.category].packages[item.value].name
