#
#  Prefs.py
#  MacLibre3
#
#  Created by Ezra on 6/25/08.
#  Copyright (c) 2008 g. All rights reserved.
#

from Foundation import *
import objc
from Parser import Parser

class InstalledPackage:

    _defaultPrefs = {
        'installedPackages':[]
    }
    def __init__(self, name, version, location):
        self.name=name
        self.version=version
        self.location=location
    
    def register(self):
        #self._defaultPrefs=[InstalledPackage("Dummy",0,"dummy")]
        defaults=NSUserDefaults.standardUserDefaults()
        print "got prefs"
        defaults.registerDefaults_(self._defaultPrefs)
        print "registered defaults"
        installed=defaults.objectForKey_('installedPackages')
        print "got installed"
        print str(installed)
        if installed:
            installed=[package for package in installed]
            installed.append((self.name, self.version, self.location))
        else:
            installed=[(self.name, self.version, self.location)]
        print "added self"
        defaults.removeObjectForKey_('installedPackages')
        defaults.setObject_forKey_(installed, 'installedPackages')
        print "updated installed"

class Prefs:
    def setDefaults(self, configuration):
        defaults=NSUserDefaults.standardUserDefaults()
        configs=[c.makeDict() for c in configuration.configs]
        defaults.registerDefaults_(c)
    
def downloadXML(url):
    request=NSURLRequest.requestWithURL_(NSURL.URLWithString_(url))
    (data, response, error)= NSURLConnection.sendSynchronousRequest_returningResponse_error_(request)
    return data
    
def parse(data):
    parser=Parser(data, True)
    return parser.parse()