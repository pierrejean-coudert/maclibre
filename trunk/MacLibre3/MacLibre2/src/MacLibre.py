#<Thanks>
#<Francois>
# to Google's Summer of Code Program for such an opportunity
# to PJ Coudert for making me a part of this program
# to Sonia, who has waited while i was coding
#</Francois>
#</Thanks>

import sys
import os

from Foundation import *
from Downloader3 import Downloader
from GUI_MaclibreWizard import *
import Config
from tools import getResourcesPath

#<TODO/Suggestions>
# * path to external command : hdiutil, sudo and installer
# * maclibre path : unix convention ( ie : ~/.prog_name ) != OSX convention
# * replace :
#              for X in Xs:
#                 self.doSomething(a.b.c.d)
#   with :
#              D = a.b.c.d
#              for X in Xs:
#                 self.doSomething(D)
#</TODO>

#<MacLibre>
class MacLibre:
    """ This class fire up MacLibre """

    def __init__(self):
        self.version = '0.2'
        self.userHome = os.path.expanduser('~')
        self.maclibreDir = os.path.join(self.userHome,'.maclibre')
        self.maclibrePackagesDir = os.path.join(self.maclibreDir,'packages')
        self.xmlMaclibrePath = ''
        self.xmlUserPath = os.path.join(self.maclibreDir,'installed.xml')
        self.firstUse()
        self.host = self.__host()

        resPath = getResourcesPath()
        if resPath == '../bin':
            resPath = '../Resources'
        self.configuration = Config.Configuration(resPath+'/config.xml')
        self.configuration.getDefaultConfig().printInfo()
	
        ## GUI
        mlw = GUI_MaclibreWizard(0)
        mlw.maclibre = self
        mlw.addPage( GUI_FirstPage(mlw) )
        mlw.addPage( GUI_PackageSelection(mlw) )
        #mlw.addPage( GUI_SelectionConfirmation(mlw) )
        #mlw.addPage( GUI_ProgressionPage(mlw) )
        #mlw.addPage( GUI_FinishedPage(mlw) )
        #mlw.wizard.FitToPage( mlw.pages[0] )    
        #mlw.run()
        #mlw.Destroy()

    def firstUse(self):
        """ This method create some maclibre specific directories before any first utilisation, if necessary """
        if not os.path.exists( self.maclibreDir ):
            os.makedirs(self.maclibreDir)
        if not os.path.exists( self.maclibrePackagesDir ):
            os.makedirs( self.maclibrePackagesDir )
	    
    def chooseWebXml(self):
        """download the maclibre.xml file """
        ### use sourceforge repository for downloading the last version of the xml file	
        defaultUrl = self.configuration.getDefaultConfig().url
        xmlMacLibre = os.path.join( self.maclibreDir , os.path.split(defaultUrl)[1] )
        
        if os.path.exists(xmlMacLibre):
            os.remove(xmlMacLibre)
        down = Downloader.alloc().init()
        down.setup(defaultUrl,xmlMacLibre)

        NSLog('start')
        down.start()
        NSLog('join')
        down.join()

        result = down.downloadResult()

        if result == True :
            self.xmlMaclibrePath = xmlMacLibre
        else:
            self.xmlMaclibrePath = ''

        return result

    def __host(self):
        """ This method return a string corresponding to the branch of OSX used."""
        darwinVersion = os.uname()[2]
        darwinList = [('1.3.1', '10.0'), ('1.4.1', '10.1'), ('5.1', '10.1.1'), ('5.2', '10.1.2'), ('5.3', '10.1.3'), ('5.4', '10.1.4'),
                  ('5.5', '10.1.5'), ('6.0', '10.2'), ('6.1', '10.2.1'), ('6.2', '10.2.2'), ('6.3', '10.2.3'), ('6.4', '10.2.4'),
                  ('6.5', '10.2.5'), ('6.6', '10.2.6'), ('6.7', '10.2.7'), ('6.8', '10.2.8'), ('7.0', '10.3'), ('7.1', '10.3.1'),
                  ('7.2', '10.3.2'), ('7.3', '10.3.3'), ('7.4', '10.3.4'), ('7.5', '10.3.5'), ('7.6', '10.3.6'), ('7.7', '10.3.7'),
                  ('7.8', '10.3.8'), ('7.9', '10.3.9'), ('8.0', '10.4'), ('8.1', '10.4.1'), ('8.2', '10.4.2'), ('8.3', '10.4.3'),
                  ('8.4', '10.4.4'), ('8.5', '10.4.5'), ('8.6', '10.4.6'), ('8.7', '10.4.7')]

        previousOSX='10.0'
        for (darwin,osx) in darwinList:
            if darwinVersion < darwin:
                return previousOSX
            previousOSX = osx 
        return '10.4'

#</MacLibre>

#<main>
if __name__ == "__main__":
    if sys.platform == "darwin":
        maclibre=MacLibre()
    else:
        print "MacLibre is a free software distribution for MacOSX"
#</main>
