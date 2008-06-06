from Foundation import *

import objc
import AppKit
import tools
objc.setVerbose(1)


class PackageListItem(NSObject):
    
    def init_(self, type, value, category = None):
        self.type=type
        self.value=value
        self.category=category
        return self
        
class PackageList (NSObject):


    def load_(self, distribution):
        #self._classInfo = getClassList()
        #self.refreshClasses()
        self.dist=distribution
        return self


    def outlineView_child_ofItem_(self, outlineview, index, item):
        #NSLog('outlineView_child_ofItem_')
        #NSLog(str(item))
        if item is None:
            return PackageListItem.alloc().init_(True, index).retain()
        else:
            return PackageListItem.alloc().init_(False, index, item.value).retain()

    def outlineView_isItemExpandable_(self, outlineview, item):
        #NSLog('outlineView_isItemExpandable_')
        #NSLog(str(item))
        return item.type

    def outlineView_numberOfChildrenOfItem_(self, outlineview, item):
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
            return {0:package.name,
                    1:package.version,
                    2:package.todo,
                    4:tools.byteSizeToReadableSize(package.installations[0].sizeOnDisk),
                    3:tools.byteSizeToReadableSize(package.installations[0].file.size)}[outlineview.tableColumns().index(column)]

    def outlineView_shouldEditTableColumn_item_(self, outlineview, column, item):
        return False
        
    def outlineView_shouldSelectItem_(self, outlineview, item):
        if item.type:
            return False
        else:
            package=self.dist.categories[item.category].packages[item.value]
            if package.todo == 'INSTALL':
                package.todo = ''
            else:
                package.todo='INSTALL'
            return True
            
    def numberOfRowsInTableView_(self, tableview):
        self.targets=[]
        [self.targets.extend([package for package in category.packages if package.todo == 'INSTALL']) for category in self.dist.categories]
        return len(self.targets)
        
    def tableView_objectValueForTableColumn_row_(self, tableview, column, row):
        return self.targets[row].name
        
    def tableView_shouldEditTableColumn_row_(self, tableview, column, row):
        return False