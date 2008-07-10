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
        'installedPackages':[],
        'downloads':[]
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
            installed=[package for package in installed if package[0] != self.name]
            installed.append((self.name, self.version, self.location))
        else:
            installed=[(self.name, self.version, self.location)]
        print "added self"
        defaults.removeObjectForKey_('installedPackages')
        defaults.setObject_forKey_(installed, 'installedPackages')
        print "updated installed"

class Prefs:
    _defaultPrefs = {
        'installedPackages':[],
        'downloads':[]
    }
    
    def __init__(self):
        defaults=NSUserDefaults.standardUserDefaults()
        defaults.registerDefaults_(self._defaultPrefs)
        self.installed=defaults.objectForKey_('installedPackages')
        
    def getTodo(self, name, todo):
        current = [package for package in self.installed if package[0] == name]
        if todo == '':
            if current:
                return 'UPDATE'
            else:
                return 'INSTALL'
        else:
            return ''
            
    def getDownload(self, filename):
        """Get the partial download data for a file of the given name"""
        defaults=NSUserDefaults.standardUserDefaults()
        downloads=defaults.objectForKey_('downloads')
        downloads = [package for package in downloads if package[0]==filename]
        if len(downloads):
            print type(downloads[0].objectAtIndex_(2))
            print downloads[0].objectAtIndex_(2)
            print type(NSUnarchiver.unarchiveObjectWithData_(downloads[0].objectAtIndex_(2)))
            print NSUnarchiver.unarchiveObjectWithData_(downloads[0].objectAtIndex_(2))
            return (downloads[0].objectAtIndex_(1), NSUnarchiver.unarchiveObjectWithData_(downloads[0].objectAtIndex_(2)))
            #plist, format, error = NSPropertyListSerialization.propertyListFromData_mutabilityOption_format_errorDescription_(downloads[0].objectAtIndex_(1), NSPropertyListImmutable, None, None)
            #return plist
        return (None, None)
    
    def setDownload(self, filename, data, response):
        """Store partial download data"""
        #print data
        #serializedData=NSPropertyListSerialization.dataFromPropertyList_format_errorDescription_(data, NSPropertyListXMLFormat_v1_0, None)
        #print serializedData
        defaults=NSUserDefaults.standardUserDefaults()
        downloads=defaults.objectForKey_('downloads')
        downloads = [packege for package in downloads if package[0]!=filename]
        downloads.append((filename, data, NSArchiver.archivedDataWithRootObject_(response)))
        defaults.removeObjectForKey_('downloads')
        defaults.setObject_forKey_(downloads, 'downloads')
        
    def clearDownload(self, filename):
        """Clear partial download data.  Call when download is complete."""
        defaults=NSUserDefaults.standardUserDefaults()
        downloads=defaults.objectForKey_('downloads')
        downloads = [packege for package in downloads if package[0]!=filename]
        defaults.removeObjectForKey_('downloads')
        defaults.setObject_forKey_(downloads, 'downloads')
        
#    def setDefaults(self, configuration):
#        defaults=NSUserDefaults.standardUserDefaults()
#        configs=[c.makeDict() for c in configuration.configs]
#        defaults.registerDefaults_(c)
    
def downloadXML(url):
    request=NSURLRequest.requestWithURL_(NSURL.URLWithString_(url))
    (data, response, error)= NSURLConnection.sendSynchronousRequest_returningResponse_error_(request)
    return data
    
def parse(data):
    parser=Parser(data, True)
    return parser.parse()