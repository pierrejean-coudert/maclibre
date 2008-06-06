
import threading
import os
import time
import re

from User import *

#<TODO>
# Optimizing hard drive information
#</TODO>

#<PkgManager>
class PkgManager(threading.Thread):
    """ This class provide a way to install a .pkg application """

    installerPath = '/usr/sbin/installer'

    def __init__( self, pkgPath, User, GUI_ProgressionPage, lenPkgs):
        """
        This __init__ construct an instance of PkgManager.
        pkgPath : the path to the .pkg
        User = an instance of User object.
        GUI_ProgressionPage : optional. An instance of GUI_ProgressionPage object.
          if given, the PkgManager will call back Installer.installPkgs when its job will be done and it will update the GUI_ProgressionPage
        """
        threading.Thread.__init__(self)
        self.pkgPath = pkgPath
        self.user = User
        self.lenPkgs = lenPkgs
        self.progressionPage = GUI_ProgressionPage
        self.target=' / '
        self.pkgResult = False

    def run(self):
        """ This method launch the installation in a separate thread"""
        
        (fd, outputPath) = tempfile.mkstemp()

        if self.progressionPage is not None:
            updateGUI=PkgGUIThread(outputPath,self.progressionPage, self.lenPkgs)
            updateGUI.start()

        #debug
        print
        print 'installing '+ self.pkgPath
        print '\t' + PkgManager.installerPath + ' exist : '+ str( os.path.exists(PkgManager.installerPath) )

        (status,result) =  self.user.useSudo(PkgManager.installerPath+' -verboseR -pkg "'+self.pkgPath+'" -target '+self.target,outputPath)
        updateGUI.keepGoing = False

        
        #debug
        print '\t' + 'status '+ str(status)
        print

        if self.progressionPage is not None:
            self.progressionPage.gauge.SetValue(0)
            self.progressionPage.smallDesc.SetLabel('')
            if status == 0: 
                self.pkgResult = self.progressionPage.installer.installPkgs(True)
            else :
                file = open(outputPath,'r')
                installerResult = file.read()
                file.close()
                errorCodeFound = re.search('.*Newer Software already exists on your computer.*',installerResult)
                if( errorCodeFound ):
                    self.progressionPage.installer.reason= 'NEWER_EXISTS'
                else:
                    self.progressionPage.installer.reason= 'CANT_INSTALL_DOTPKG'
                self.pkgResult = False
                
        #delete temp file
        os.remove(outputPath)
        
    def getPkgResult(self):
        return self.pkgResult

#</PkgManager>

#<PkgGUIThread>
class PkgGUIThread(threading.Thread):
    """ update the GUI (ie: wx.Gauge) by reading output of installer command """

    def __init__(self,outputPath,GUI_ProgressionPage, lenPkgs):
        threading.Thread.__init__(self)
        self.outputPath = outputPath
        self.progressionPage = GUI_ProgressionPage
        self.keepGoing = True
        self.lenPkgs = lenPkgs

    def run(self):
        self.percent = 0
        while self.keepGoing:
            try:
                file = open(self.outputPath,'r')
                percentList = file.read().split('\n')

                percentList = [ line for line in percentList if 'installer:%' in line]
                if len(percentList) > 0:
                    percent = long(percentList[-1].split('.')[-1])/10000
                    if percent > self.percent :
                        self.percent = percent
                        self.progressionPage.gauge.SetValue(self.percent)
                        
                        
                        onePkgValue = self.progressionPage.installer.overallPkgPieceSize / self.lenPkgs
                        pkgCountDepend = self.progressionPage.installer.idDotPkg * onePkgValue                
                        overallValue = self.progressionPage.installer.overallProgressValue + pkgCountDepend
                        pkgPieceValue =  onePkgValue * self.percent / 100
                        overallValue = overallValue + pkgPieceValue
                        self.progressionPage.installer.setOverallProgressValue( overallValue )                        
                        
                        #pkgPieceValue = self.progressionPage.installer.overallPkgPieceSize * self.percent / 100
                        #overallValue = self.progressionPage.installer.overallProgressValue + pkgPieceValue
                        #self.progressionPage.installer.setOverallProgressValue( overallValue )
                file.close()
                time.sleep(0.5)
            except IOError:
                time.sleep(0.5)

#</PkgGUIThread>

#<main>
if __name__ == "__main__":
    print PkgManager.__doc__
#</main>
