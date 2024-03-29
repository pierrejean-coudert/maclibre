#
#  Prefs.py
#  MacLibre3
#
#  Created by Ezra on 6/25/08.
#  
#  The classes and functions in this file handle storing and retrieving information
#  from the Mac OS X preferences file stored in ~/Library/Preferences/
#

from Foundation import *
import objc
from Parser import Parser

class InstalledPackage:
    """Handle information about stored package."""
    
    _defaultPrefs = {
        'installedPackages':[],
        'downloads':[]
    }
    def __init__(self, name, version, location):
        """Initialize this object with the necessary information, but don't do anything with it yet."""
        self.name=name
        self.version=version
        self.location=location
    
    def register(self):
        """Store the information in the preferences file."""
        #self._defaultPrefs=[InstalledPackage("Dummy",0,"dummy")]
        defaults=NSUserDefaults.standardUserDefaults()
        print "got prefs"
        defaults.registerDefaults_(self._defaultPrefs)
        print "registered defaults"
        installed=defaults.objectForKey_('installedPackages')
        print "got installed"
        print str(installed)
        print self.version
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
        """Get the list of currently installed packages and store it in self.installed.""" 
        defaults=NSUserDefaults.standardUserDefaults()
        defaults.registerDefaults_(self._defaultPrefs)
        self.installed=defaults.objectForKey_('installedPackages')
        
    def getTodo(self, name, todo):
        """Given a package name and an action, return the appropriate opposite action."""
        current = [package for package in self.installed if package[0] == name]
        if todo == '':
            if current:
                return 'Update'
            else:
                return 'Install'
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
            return (downloads[0].objectAtIndex_(1), NSUnarchiver.unarchiveObjectWithData_(downloads[0].objectAtIndex_(2)), downloads[0].objectAtIndex_(3))
            #plist, format, error = NSPropertyListSerialization.propertyListFromData_mutabilityOption_format_errorDescription_(downloads[0].objectAtIndex_(1), NSPropertyListImmutable, None, None)
            #return plist
        return (None, None, 0)
    
    def setDownload(self, filename, data, response, bytes):
        """Store partial download data"""
        #print data
        #serializedData=NSPropertyListSerialization.dataFromPropertyList_format_errorDescription_(data, NSPropertyListXMLFormat_v1_0, None)
        #print serializedData
        defaults=NSUserDefaults.standardUserDefaults()
        downloads=defaults.objectForKey_('downloads')
        downloads = [package for package in downloads if package[0]!=filename]
        downloads.append((filename, data, NSArchiver.archivedDataWithRootObject_(response), bytes))
        defaults.removeObjectForKey_('downloads')
        defaults.setObject_forKey_(downloads, 'downloads')
        
    def clearDownload(self, filename):
        """Clear partial download data.  Call when download is complete."""
        defaults=NSUserDefaults.standardUserDefaults()
        downloads=defaults.objectForKey_('downloads')
        downloads = [package for package in downloads if package[0]!=filename]
        defaults.removeObjectForKey_('downloads')
        defaults.setObject_forKey_(downloads, 'downloads')
        
#    def setDefaults(self, configuration):
#        defaults=NSUserDefaults.standardUserDefaults()
#        configs=[c.makeDict() for c in configuration.configs]
#        defaults.registerDefaults_(c)
    
def downloadXML(url):
    """Download a Maclibre XML configuration file synchronously.""" 
    request=NSURLRequest.requestWithURL_(NSURL.URLWithString_(url))
    (data, response, error)= NSURLConnection.sendSynchronousRequest_returningResponse_error_(request)
    return data
    
def parse(data):
    """Parse a MacLibre XML configuration file stored in a string."""
    parser=Parser(data, True)
    return parser.parse()