from Foundation import *

import threading
import os
import shutil
import time

#<AppManager>
class AppManager:
    """ This class provide a way to install an .app application """

    def __init__( self, appPath, todo, GUI_ProgressionPage=None, lenApps=0 ):
        """
        This __init__ construct an instance of AppManager.
        appPath : the path to the .app
        todo = what to do with the .app, UPDATE, INSTALL or REINSTALL.
        GUI_ProgressionPage : optional. An instance of GUI_ProgressionPage object.
          if given, the AppManager will call back Installer.installApps() when its job will be done and it will update the GUI_ProgressionPage
        """
        #threading.Thread.__init__(self)
        self.appPath = appPath
        self.appSize = self.__getDirSize(self.appPath)
        self.todo = todo
        self.progressionPage = GUI_ProgressionPage
        self.appResult = False
        self.lenApps = lenApps
        self.done=False
        
        self.appsUserPath = os.path.join( os.path.expanduser("~"), "Applications" )
        self.appsSystemPath = "/Applications"
        self.appName = os.path.split(appPath)[1]
        
        if os.access(self.appsSystemPath,os.W_OK): self.canWriteSlashApp = True
        else:  self.canWriteSlashApp = False

        if self.canWriteSlashApp : self.destination = os.path.join( self.appsSystemPath, self.appName )  # full path to the .app when installed
        else :
            if not os.path.exists(self.appsUserPath ):
                os.makedirs(self.appsUserPath)
            self.destination = os.path.join( self.appsUserPath, self.appName )
    
    def start(self):
        NSThread.detachNewThreadSelector_toTarget_withObject_('run:',self,None)
        return self.destination
    
    def run_(self, argToIgnore=None):
        pool=NSAutoreleasePool.alloc().init()
        NSLog('starting appManager')
        self.run()
        NSLog('ending appManager')
        del pool
    
    def join(self):
        NSLog('app.join() called')
        while self.done == False:# and runloop.runMode_beforeDate_(NSDefaultRunLoopMode, NSDate.distantFuture()):
            pass
        NSLog('appManager join done')
    
    def run(self):
        """ This method launch the installation in a separate thread"""
        if os.path.exists(self.destination):
            if self.todo == 'Install' :
                if self.progressionPage is not None:
                    self.appResult = False
                    return
            if (self.todo == 'Update' or self.todo == 'Reinstall') :
                shutil.rmtree(self.destination)
        
        if self.progressionPage is not None:
            
            #debug
            print
            print 'copying '+ self.appPath + ' to ' + self.destination
            print

            copyTh = CopyThread(self.appPath,self.destination)
            copyTh.start()
            while copyTh.isAlive():
                self.progressionPage.gauge.SetValue( self.__getDirSize(self.destination)*100/self.appSize )
                self.progressionPage.gauge.SetValue( self.__getDirSize(self.destination)*100/self.appSize )
                # overall progress bar value calculations
                oneAppValue = self.progressionPage.installer.overallPkgPieceSize / self.lenApps
                appCountDepend = self.progressionPage.installer.idApp * oneAppValue                
                overallValue = self.progressionPage.installer.overallProgressValue + appCountDepend
                pkgPieceValue =  oneAppValue * (self.__getDirSize(self.destination)*100/self.appSize)/ 100
                overallValue = overallValue + pkgPieceValue
                self.progressionPage.overallGauge.SetValue(overallValue)
            
            self.progressionPage.gauge.SetValue(0)
            self.appResult = self.progressionPage.installer.installApps(True)
        else:
            shutil.copytree(self.appPath,self.destination,symlinks=True)
        self.done=True
    
    def getAppResult(self):
        return self.appResult
	
    def __calcDirSize(self,arg, dir, files):
	""" method used by __getDirSize for calculating the size of a folder. correspond to os.path.walk syntax  """
        for file in files:
	    path = os.path.join(dir, file)
	    if not os.path.islink(path):
		size = os.stat(path)[6]
		arg.append(size)

    def __getDirSize(self,dir):
	""" return the size of the given directory in bytes"""
        sizes = []
        os.path.walk(dir, self.__calcDirSize, sizes)
        total = 0
        for size in sizes:
	    total = total + size
	return total

#</AppManager>

#<CopyThread>
class CopyThread:
    """ launch the copy in a separate thread """
    def __init__(self,src,dest):
	#threading.Thread.__init__(self)
	self.src =src
	self.dest=dest

    def start(self):
        self.alive=True
        NSThread.detachNewThreadSelector_toTarget_withObject_('run:',self,None)
    def run_(self, argToIgnore=None):
        pool=NSAutoreleasePool.alloc().init()
        NSLog('Starting copyThread')
        self.run()
        NSLog('Ending copyThread')
        del pool
        
        
    def isAlive(self):
        return self.alive
        
    def run(self):
	shutil.copytree(self.src,self.dest,symlinks=True)
        self.alive=False
#</CopyThread>

#<main>
if __name__ == "__main__":
    print AppManager.__doc__
#</main>
