from Foundation import *
from AppKit import *
from CoreData import *

import objc
import sys
import os
from Downloader3 import Downloader
from MacLibre import *
from Parser import Parser
from Installer import Installer
from Prefs import *


objc.loadBundle("SecurityInterface", globals(), 
bundle_path="/System/Library/Frameworks/SecurityFoundation.framework")

objc.loadBundle("SecurityInterface", globals(), 
bundle_path="/System/Library/Frameworks/SecurityInterface.framework")


class MacLibre3(NSObject):
    tabs = objc.IBOutlet()
    packList=objc.IBOutlet()
    packConf=objc.IBOutlet()
    auth=objc.IBOutlet()
    previousButton=objc.IBOutlet()
    nextButton=objc.IBOutlet()
    installation=objc.IBOutlet()
    pauseButton=objc.IBOutlet()
    webView=objc.IBOutlet()
    maclibre=MacLibre()
    
    @objc.IBAction
    def nextPage_(self, sender):
        if self.tabs.indexOfTabViewItem_(self.tabs.selectedTabViewItem()) == 0:
            #self.maclibre.chooseWebXml()
            defaultUrl = self.maclibre.configuration.getDefaultConfig().url
            #xmlMacLibre = os.path.join( self.maclibre.maclibreDir , os.path.split(defaultUrl)[1] )
            #down = Downloader.alloc().init()
            #down.setup(defaultUrl,xmlMacLibre)
            #down.registerFinishFunction(self,'processPackages')
            #down.start()
            #self.maclibre.xmlMaclibrePath=xmlMacLibre
            dist=self.processPackages()
            #dist=parse(downloadXML(defaultUrl))
            self.packList.dataSource().load_(dist, None)
            self.tabs.selectNextTabViewItem_(1)
            self.previousButton.setEnabled_(True)      
        else:
            if self.tabs.indexOfTabViewItem_(self.tabs.selectedTabViewItem()) == 1:
                self.packConf.setDataSource_(self.packList.dataSource())
                self.packConf.setDelegate_(self.packList.dataSource())
                self.auth.setDelegate_(self)
                self.auth.setString_("com.maclibre.auth")
                self.auth.setAutoupdate_(True)
                self.auth.updateStatus_(self)
                #self.nextButton.setEnabled_(self.auth.updateStatus_(self))
            self.tabs.selectNextTabViewItem_(1)
            if self.tabs.indexOfTabViewItem_(self.tabs.selectedTabViewItem()) == 3:
                self.installation.setSelected(self.packList.dataSource().dist, self.packList.dataSource().inst)
                self.installer=Installer(self.installation, self)
                self.installation.setup(self.installation, self.maclibre, self.installer)
                self.installer.install(getattr(self.tabs,'selectNextTabViewItem_'))

    @objc.IBAction
    def previousPage_(self, sender):
        #self.webView.setMainFrameURL_("https://winlibre.svn.sourceforge.net/svnroot/winlibre/MacLibre2/xml/en.xml")
        #self.tabs.selectPreviousTabViewItem_(1)
        #if self.tabs.indexOfTabViewItem_(self.tabs.selectedTabViewItem()) == 0:
        #    self.previousButton.setEnabled_(False)
        if (self.downloader):
            print self.downloader.dl.resumeData()
            self.downloader.dl.cancel()
            print self.downloader.dl.resumeData()
        
    @objc.IBAction
    def quit_(self, sender):
        NSApp.terminate_(None)
    
    @objc.IBAction
    def pauseOrResume_(self, sender):
        prefs=Prefs()
        if self.pauseButton.title() == "Pause Download":
            if (self.downloader):
                self.downloader.dl.cancel()
                resume=self.downloader.dl.resumeData()
                prefs.setDownload(self.downloader.url,resume,self.downloader.response, self.downloader.bytesReceived)
                self.pauseButton.setTitle_("Resume Download")
        else:
            self.installer.install(getattr(self.tabs,'selectNextTabViewItem_'))
            self.pauseButton.setTitle_("Pause Download")

    
    def authorizationViewDidAuthorize_(self, view):
        self.nextButton.setEnabled_(True)
        
    def authorizationViewReleasedAuthorization_(self, view):
        self.nextButton.setEnabled_(False)
        
    
    def processPackages(self):
        print "processPackages"
        url=NSURL.fileURLWithPath_("/Users/ezra/Documents/config3.xml")
        bundles=NSArray.arrayWithObject_(NSBundle.mainBundle())
        model=NSManagedObjectModel.mergedModelFromBundles_(bundles)
        coordinator=NSPersistentStoreCoordinator.alloc().initWithManagedObjectModel_(model)
        error=coordinator.addPersistentStoreWithType_configuration_URL_options_error_(NSXMLStoreType, None, url, None)
        managedObjectContext=NSManagedObjectContext.alloc().init()
        managedObjectContext.setPersistentStoreCoordinator_(coordinator)
        
        fetchRequest=model.fetchRequestFromTemplateWithName_substitutionVariables_('categories', None)
        (categories,error)=managedObjectContext.executeFetchRequest_error_(fetchRequest, None)
        
        fetchRequest=model.fetchRequestFromTemplateWithName_substitutionVariables_('packages', None)
        (packages,error)=managedObjectContext.executeFetchRequest_error_(fetchRequest, None)
        
        dist=Distribution()
        for category in categories:
            dist.categories.append(Category(category.valueForKey_('name'),[]))
            for package in packages:
                print package.valueForKey_('category').valueForKey_('name')
                print category.valueForKey_('name')
                if package.valueForKey_('category').valueForKey_('name') == category.valueForKey_('name'):
                    print 'adding'
                    dist.categories[-1].packages.append(Package(package.valueForKey_('name'),
                    package.valueForKey_('version'),True,'stable',package.valueForKey_('desc'),package.valueForKey_('homepage'),'',
                    [Installation(package.valueForKey_('sizeOnDisk'),package.valueForKey_('OSMin'),
                    file=File(package.valueForKey_('fileName'),package.valueForKey_('sizeOnDisk'),md5=package.valueForKey_('MD5Sum'),urls=[package.valueForKey_('url')]))]
                    ,package.valueForKey_('logo')))
        for category in dist.categories:
            print category
            print str(category.packages)
        return dist
        print packages
        print packages[0]
        print packages[0].valueForKey_('name')
        #parserWeb = Parser(self.maclibre.xmlMaclibrePath)
        #parserUser = Parser(self.maclibre.xmlUserPath)
        #self.packList.dataSource().load_(parserWeb.parse(), parserUser.parse())
        #self.tabs.selectNextTabViewItem_(1)
        
    def registerDownloader(self, downloader):
        self.downloader=downloader
        
    def applicationDidFinishLaunching_(self, sender):
        NSLog("Application did finish launching.")
    
    def applicationShouldTerminate_(self, sender):
        if (self.downloader and self.downloader.download == False):
                prefs=Prefs()
                self.downloader.dl.cancel()
                resume=self.downloader.dl.resumeData()
                prefs.setDownload(self.downloader.url,resume,self.downloader.response, self.downloader.bytesReceived)
        return True