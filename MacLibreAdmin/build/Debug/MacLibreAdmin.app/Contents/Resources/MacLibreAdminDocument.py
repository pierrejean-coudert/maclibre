#
#  MacLibreAdminDocument.py
#  MacLibreAdmin
#
#  Created by Ezra on 7/16/08.
#  Copyright g 2008. All rights reserved.
#

from Foundation import *
from CoreData import *
from AppKit import *

class MacLibreAdminDocument(NSPersistentDocument):
    def init(self):
        self = super(MacLibreAdminDocument, self).init()
        # initialization code
        return self
        
    def windowNibName(self):
        return u"MacLibreAdminDocument"
    
    def windowControllerDidLoadNib_(self, aController):
        super(MacLibreAdminDocument, self).windowControllerDidLoadNib_(aController)
        # user interface preparation code
