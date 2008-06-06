#
#  main.py
#  MacLibre3
#
#  Created by Ezra on 5/26/08.
#  Copyright __MyCompanyName__ 2008. All rights reserved.
#

#import modules required by application
import objc
import Foundation
import AppKit

from PyObjCTools import AppHelper

# import modules containing classes required to start application and load MainMenu.nib
import MacLibre3AppDelegate
import MacLibre3

# pass control to AppKit
AppHelper.runEventLoop()
