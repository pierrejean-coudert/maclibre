#
#  main.py
#  MacLibreAdmin
#
#  Created by Ezra on 7/16/08.
#  Copyright g 2008. All rights reserved.
#

#import modules required by application
import objc
import Foundation
import AppKit

from PyObjCTools import AppHelper

# import modules containing classes required to start application and load MainMenu.nib
import MacLibreAdminDocument

# pass control to AppKit
AppHelper.runEventLoop()
