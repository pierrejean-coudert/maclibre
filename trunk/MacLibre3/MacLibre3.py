from Foundation import *
from AppKit import *
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
    nextButton=objc.IBOutlet()
    installation=objc.IBOutlet()
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
            dist=parse(downloadXML(defaultUrl))
            self.packList.dataSource().load_(dist, None)
            self.tabs.selectNextTabViewItem_(1)      
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
                self.installer=Installer(self.installation)
                self.installation.setup(self.installation, self.maclibre, self.installer)
                self.installer.install()

    @objc.IBAction
    def previousPage_(self, sender):
        self.webView.setMainFrameURL_("https://winlibre.svn.sourceforge.net/svnroot/winlibre/MacLibre2/xml/en.xml")
        self.tabs.selectPreviousTabViewItem_(1)
        
    @objc.IBAction
    def quit_(self, sender):
        sys.exit()

    
    def authorizationViewDidAuthorize_(self, view):
        self.nextButton.setEnabled_(True)
        
    def authorizationViewReleasedAuthorization_(self, view):
        self.nextButton.setEnabled_(False)
        
    
    def processPackages(self):
        parserWeb = Parser(self.maclibre.xmlMaclibrePath)
        parserUser = Parser(self.maclibre.xmlUserPath)
        self.packList.dataSource().load_(parserWeb.parse(), parserUser.parse())
        self.tabs.selectNextTabViewItem_(1)