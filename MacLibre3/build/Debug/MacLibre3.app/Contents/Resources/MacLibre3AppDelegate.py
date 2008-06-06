#
#  MacLibre3AppDelegate.py
#  MacLibre3
#
#  Created by Ezra on 5/26/08.
#  Copyright __MyCompanyName__ 2008. All rights reserved.
#

from Foundation import *
from AppKit import *
from MacLibre import *
from PackageList import *

class MacLibre3AppDelegate(NSObject):
    def applicationDidFinishLaunching_(self, sender):
        NSLog("Application did finish launching.")
    
#    def pageTwo(self):
#	NSLog('Test')