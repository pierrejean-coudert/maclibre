from Foundation import *

import threading
import os
import shutil

from tools import getResourcesPath
from MD5 import *
from Distribution import *
from Downloader3 import Downloader
from DmgContainer import *
from ZipContainer import *
from AppManager import *
from PkgManager import *
from Prefs import *
#<TODO>
# the thread-class-update-GUI (ie:Downloader,AppManager,PkgManager) thing is ugly ! : 
#     use something like wx.PostEvent and a wx custom event in replacement.
#
# replace 
#    calculate all dependencies  -> download all -> install all packages -> save all
# by
#    calculate alld dependencies -> for package in self.orderToInstall ( download package -> install package -> save package )
#</TODO>

#<Installer>

class InstallerProgressThread:
    pass
#    def __init__(self,installer):
#        threading.Thread.__init__(self)	
#        self.installer = installer
#    
#    def run(self):
#        self.pool=NSAutoreleasePool.alloc().init()
#        self.installer.processInstallation()
#        print 'End of installation'
#        self.pool.release()

class Installer:
    """ This class does all the process of programs installation """

    def __init__(self,GUI_ProgressionPage, maclibre3=None):
        self.progressionPage = GUI_ProgressionPage
        self.installationStarted = False
        self.installationStatus = {}

        self.orderToInstall = [] # a list of packages used as a queue. package are added in this queue in order of installation
        self.correctlyDownloaded = [] # a list of booleans corresponding to self.orderToInstall.
        self.cantBeInstalled = [] # a list of tuples representing the packages which can't be installed and the reasons.
                                      # ie : [ [fooPkg,'DOWNLOAD_FAILED'], [barPkg,'ALREADY_IN_APP_DIR'] ]
        self.containers=[]        # a list of container corresponding to self.orderToInstall

        self.reasonsDict = { 'DOWNLOAD_FAILED'     : "Download failure",
                     'UNKNOW_CONTAINER'    : "Downloaded file uses a not supported format",
                     'UNKNOW_EXT'          : "Couldn't find .pkg or .app program",
                     'CANT_MOUNT_DMG'      : "Unable to mount dmg image",
                     'UNKNOWN_TODO'        : "You have request an unknown operation",
                     'ALREADY_IN_APP_DIR'  : "Already in your Applications folder",
                     'NO_APPS_FOUND'       : "No .app in package's file",
                     'NO_PKGS_FOUND'       : "No .pkg in package's file",
                     'CANT_INSTALL_DOTPKG' : "Can't install this .pkg program. (permission problem) ",
                     'NEWER_EXISTS': "Newer Software already exists on your computer" }

        self.todoKnown = {'Install':'Installing ','Reinstall':'Re-installing ','Update':'Updating '}
        self.reason = '' # reason why don't installing a package
        self.maclibre3=maclibre3

    def install(self, finishFunc=None):
        """ call self.calculateDependencies """
        self.calculateDependencies(finishFunc)

    def calculateDependencies(self, finishFunc=None):
        """ calculate dependencies. ie : add packages in the correct order (dependencies) in self.orderToInstall. call self.download when finished"""
        self.progressionPage.gaugeDesc.SetLabel('                                                                                      ')
        self.progressionPage.gaugeDesc.SetLabel('Calculating dependencies...')
        self.progressionPage.gaugeDesc.Refresh()
     
        for category in self.progressionPage.maclibreWizard.selected.categories:
            for package in category.packages:
                self.__addInOrderToInstall(package)
                if package.hasDependencies():
                    (dependenciesDict, order) = package.getDependencies(self.progressionPage.maclibreWizard.selected,order=True)

                    for i in range( len(dependenciesDict) ):
                        if order[i] == 'after':
                            if dependenciesDict[i] in self.orderToInstall:
                                self.orderToInstall.remove(dependenciesDict[i])
                                self.orderToInstall.append(dependenciesDict[i])
                        elif order[i] == 'before':
                            self.__addInOrderToInstall( dependenciesDict[i],  0 )


        #debug
        print
        print 'install queue : '
        for package in self.orderToInstall:
            print '\t' + '\t' + 'PACKAGE:',
            print '\t' + '\t' + package.name,
            print '\t' + '\t' + package.version,
            print '\t' + '\t' + package.todo
        print

        #self.installerProgressThread = InstallerProgressThread(self)
        #self.installerProgressThread.start()
        #self.processInstallation()
        NSThread.detachNewThreadSelector_toTarget_withObject_('processInstallation:', self, finishFunc)
        

    def processInstallation_(self, finishFunc):
        pool=NSAutoreleasePool.alloc().init()
        NSLog('starting installer')
        self.processInstallation()
        finishFunc(1)
        NSLog('ending installer')
        del pool

    def processInstallation(self):
        """Downloading and installing all selected packages"""
        # for each package
        if self.installationStarted == False:
            self.installationStatus = {}
            self.overallProgressValue = 0
            self.overallPkgPieceSize = 100 / (self.progressionPage.maclibreWizard.pages[2].packagesCount * 4)
        
        self.installationStarted = True
        self.idPkg = -1
        
        for package in self.orderToInstall:
            self.currentPkg = package
            self.idPkg += 1
            
            if package.name not in self.installationStatus:
                self.installationStatus[package.name] = {}
                self.installationStatus[package.name]['download'] = False
                self.installationStatus[package.name]['prepareContainer'] = False
                self.installationStatus[package.name]['install'] = False
                self.installationStatus[package.name]['overwrite'] = False
                self.installationStatus[package.name]['overwriteValue'] = False
                self.installationStatus[package.name]['finalize'] = False
                self.installationStatus[package.name]['appInitStatus'] = False       
        
            if self.installationStatus[package.name]['download'] == False:
                self.progressionPage.showAppLogoImage(self.currentPkg)
                if self.download(package):
                    
                    self.installationStatus[package.name]['download'] = True
                    #print "Couldn't downlad " + package.name
                    if not self.__AllPiecesCorrectlyDownloaded(self.idPkg):
                        self.addToCantInstall(True)
                        print 'Failure downloading ' + package.name
                        self.overallProgressValue += 3 * self.overallPkgPieceSize
                        self.setOverallProgressValue( self.overallProgressValue )
                        self.installationStatus[package.name]['prepareContainer'] = True
                        self.installationStatus[package.name]['install'] = True
                        self.installationStatus[package.name]['finalize'] = True
                    else:
                        print 'Successful download of ' + package.name
                else:
                    return
                        
                self.overallProgressValue += self.overallPkgPieceSize
                self.setOverallProgressValue( self.overallProgressValue )
        
        self.idPkg = -1
        for package in self.orderToInstall:
            # download
            self.idPkg += 1
            self.progressionPage.gaugeDesc.SetLabel('                                                                                      ')

            #add exception try except
            self.currentPkg = package

            

            # prepare container
            # prepare container thread
            if self.installationStatus[package.name]['prepareContainer'] == False:
                self.progressionPage.showAppLogoImage(self.currentPkg)
                if self.prepareContainer() == True:
                    self.installationStatus[package.name]['prepareContainer'] = True
                else:
                    print "Couldn't prepare container of " + package.name
                    if self.reason != 'CANT_MOUNT_DMG':
                        self.addToCantInstall(True)
                    else:
                        self.addToCantInstall(False)
                    self.overallProgressValue += 3 * self.overallPkgPieceSize
                    self.setOverallProgressValue( self.overallProgressValue )
                    self.installationStatus[package.name]['prepareContainer'] = True
                    self.installationStatus[package.name]['install'] = True
                    self.installationStatus[package.name]['finalize'] = True
                    
                    continue
                self.overallProgressValue += self.overallPkgPieceSize
                self.setOverallProgressValue( self.overallProgressValue )
            # install package
            # install app or pkg
            
            if self.installationStatus[package.name]['install'] == False:
                self.progressionPage.showAppLogoImage(self.currentPkg)
                if self.installPackage() == True:
                    self.installationStatus[package.name]['install'] = True
                else:
                    print "Couldn't install " + package.name
                    print "Reason: " + self.reason
                    if self.installationStatus[self.currentPkg.name]['overwrite'] == False:
                        self.addToCantInstall(False)
                        
                        self.installationStatus[package.name]['install'] = True
                        self.installationStatus[package.name]['finalize'] = True
                        
                        self.overallProgressValue += self.overallPkgPieceSize
                        self.setOverallProgressValue( self.overallProgressValue )
                        
                        self.finalizeContainer(package)
                        
                        self.overallProgressValue += self.overallPkgPieceSize
                        self.setOverallProgressValue( self.overallProgressValue )
                        continue
                    return False
                self.overallProgressValue += self.overallPkgPieceSize
                self.setOverallProgressValue( self.overallProgressValue )


            # finalize container (+thread for dmg container)
            if self.installationStatus[package.name]['finalize'] == False:
                self.progressionPage.showAppLogoImage(self.currentPkg)
                if self.finalizeContainer(package):
                    self.installationStatus[package.name]['finalize'] = True
                    self.overallProgressValue += self.overallPkgPieceSize
                    self.setOverallProgressValue( self.overallProgressValue )

        
        self.overallProgressValue = 100
        self.setOverallProgressValue( self.overallProgressValue )
        
        self.progressionPage.enableAppLogoImage(False)
        # save installation
        self.saveInstalled() 
        return True
        
    def setOverallProgressValue(self,value):
        self.progressionPage.overallGauge.SetValue( value )   
        self.progressionPage.overallSmallDesc.SetLabel( str(value) + ' %')
        self.progressionPage.overallSmallDesc.Refresh()
     
        

    def download(self, package='None', correctlyDone='init'):
        """Launch the download for current package. It's using Downloader class.
        If some files are already downloaded (good path and md5), it returns True"""
        
        if correctlyDone == 'init':
            self.idUrl = 0
        
        if correctlyDone == False:
            self.idUrl += 1
            
        if correctlyDone==False and self.idUrl >= self.lenUrl-1:
            return True
        else:

            packageDir = os.path.join( self.progressionPage.maclibreWizard.maclibre.maclibrePackagesDir, package.name )
            #packageDir=NSSearchPathForDirectoriesInDomains(NSApplicationSupportDirectory, NSUserDomainMask, True)[0]
            #packageDir+="/Maclibre3/"
            #packageDir+=package.name
            file = package.installations[0].file
            destination = os.path.join(packageDir,file.name)
            self.lenUrl = len(file.urls)

            noMoreUrls = self.idUrl > self.lenUrl -1
            alreadyDownloaded = os.path.exists(destination) and (MD5(destination,file.md5)).isCorrect()
            
            print 'Destination file: ' + destination
            #debug
            print '\t already downloaded : '+ str(alreadyDownloaded)
            print '\t no more urls available : '+ str(noMoreUrls)

            if noMoreUrls or alreadyDownloaded :
                print '\t launch next download '
            if alreadyDownloaded:
                #self.progressionPage.gaugeDesc.SetLabel('                                                                                      ')
                self.progressionPage.gaugeDesc.SetLabel(package.name+' already cached')
                self.progressionPage.gaugeDesc.Refresh()            
                self.correctlyDownloaded.append(True)
                return True
            else:
                print '\t launching download '
                if os.path.exists(packageDir) : shutil.rmtree(packageDir)
                url = file.urls[self.idUrl]
                if not os.path.exists(packageDir):
                    os.makedirs( packageDir )
                
                #distribVersion = self.progressionPage.maclibreWizard.maclibre.configuration.getDefaultConfig().version
            
                labelText = 'Downloading '

                #if distribVersion == 'offline' or (distribVersion == 'mixed' and package.diskImageLocation == 'offline'):
                if package.diskImageLocation == 'offline':
                    url = 'file:/' + getResourcesPath() + '/' + file.name
                    print url
                    labelText = 'Copying '

                #debug
                print
                print labelText + package.name
                
                if package.diskImageLocation == 'offline':
                    return True
                
                downloader = Downloader.alloc().init()
                downloader.setup( url , destination , file.size, self.progressionPage, md5=file.md5, maclibre3=self.maclibre3 )
                downloader.start()
                #self.progressionPage.gaugeDesc.SetLabel('                                                                                      ')
                self.progressionPage.gaugeDesc.SetLabel(labelText + package.name)
                self.progressionPage.gaugeDesc.Refresh()  
                downloader.registerFinishFunction(self,'processInstallation')
                #return False      
                downloader.join()
                
                if not downloader.downloadResult():
                    return self.download(package,False);
                
                return downloader.downloadResult()
            
            print

    def prepareContainer(self,lastStatement='init'):
        """Prepare container of current package. ie : mount dmgs and extract archives."""
        self.progressionPage.gauge.SetValue(0)

        #debug
        print
        print 'prepare container of '+ self.currentPkg.name
        print

        self.currentType = self.currentPkg.installations[0].file.type
        print 'idPkg: ' + str(self.idPkg)
        if not self.__AllPiecesCorrectlyDownloaded(self.idPkg):
            return False
        else:
            currentContainer = self.__getContainer()
        
            if self.reason != '':
                return False
            else:
                self.containers.append(currentContainer)
                print 'added to container: ' + str(self.idPkg) + ' ' + str(len(self.containers))
                print 'Adding container to ' + self.currentPkg.name
                if self.currentType == 'dmg':
                    #self.progressionPage.gaugeDesc.SetLabel('                                                                                      ')
                    self.progressionPage.gaugeDesc.SetLabel('Mounting ' + self.currentPkg.name + ' image')
                    self.progressionPage.gaugeDesc.Refresh()
                   
                    currentContainer.mount()
                    if not currentContainer.isMounted:
                        self.reason = 'CANT_MOUNT_DMG'
                        return False
                elif self.currentType == 'zip':
                    #self.progressionPage.gaugeDesc.SetLabel('                                                                                      ')
                    self.progressionPage.gaugeDesc.SetLabel('Extracting ' + self.currentPkg.name + ' archive')
                    self.progressionPage.gaugeDesc.Refresh()
               
                    currentContainer.extract()
        return True
    
    def addToCantInstall(self, addContainer=False):
        """Adding current package to cantInstall table."""
        if not self.__cantBeInstalled(self.currentPkg): #and self.reason != '':
            print 'cantbeinstalled: ' + str(self.idPkg)
            if addContainer:
                self.containers.append(None) # just for matching indexes
                print 'added to container: ' + str(self.idPkg) + ' ' + str(len(self.containers))
            self.cantBeInstalled.append( [self.currentPkg,self.reason] )
            self.reason = ''
            return True
        else:
            return False

    def installPackage(self,lastStatement='init'):
        """Install current package. It calls installApps or installPkgs according to the container of the package."""

        self.reason=''

        self.currentType = self.currentPkg.installations[0].file.type
        extension = self.currentPkg.installations[0].file.extension

        if extension == 'app':
            if not self.installApps():
                return False
        elif extension == 'pkg':
            if not self.installPkgs():
                return False
        else:
            self.reason = 'UNKNOWN_EXT'
            return False
        return True

    def installPkgs(self,correctlyDone='init'):
        """Recursive (more than one .pkg in the current container). This method install .pkg programs. it's using PkgManager."""

        dotPkgs = self.containers[self.idPkg].getDotPkg()
        self.lenPkgs = len(dotPkgs)

        if self.lenPkgs == 0:
            self.reason= 'NO_PKGS_FOUND'
            return False
        
        if correctlyDone == 'init':
            self.idDotPkg = 0
        elif correctlyDone == True: 
            self.idDotPkg += 1
        
        if self.idDotPkg >= self.lenPkgs and correctlyDone == True:
            return True
        else:
            todo = self.currentPkg.todo
            if todo in self.todoKnown:
                overwrite=False
                #self.progressionPage.gaugeDesc.SetLabel('')
                self.progressionPage.gaugeDesc.SetLabel( self.__getGaugeDescTxt( todo,self.lenPkgs,self.idDotPkg,overwrite ) )
                self.progressionPage.gaugeDesc.Refresh()
              
                pkgM = PkgManager( dotPkgs[self.idDotPkg], self.progressionPage.maclibreWizard.user , self.progressionPage, self.lenPkgs )
                pkgM.start()
                pkgM.join()
                if not pkgM.getPkgResult():
                    return False
            else:
                self.reason = 'UNKNOWN_TODO' 
                return False
        return True
		    
    def installApps(self,correctlyDone='init'):
        """Recursive (more than one .app in the current container). This method install .app programs. it's using AppManager."""
        print 'Debug idPkg: ' + str(self.idPkg)
        print 'Containers len: ' + str(len(self.containers))
        dotApps = self.containers[self.idPkg].getDotApp() # move somewhere else
        
        #debug 
        print
        print 'Apps found : '
        for elem in dotApps:
            print elem + '\t' ,
            print

        lenApps = len(dotApps)

        if lenApps == 0:
            self.reason ='NO_APPS_FOUND' # mostly dmg image unmounted by user
            return False
        
        if correctlyDone == 'init' and not self.installationStatus[self.currentPkg.name]['appInitStatus']:  
            self.idApp = 0
            self.installationStatus[self.currentPkg.name]['appInitStatus'] = True
            
        elif correctlyDone == True:  self.idApp += 1

        print 'idApp: ' + str(self.idApp)
        if self.idApp >= lenApps and correctlyDone == True:
            return True
        else:
            todo = self.currentPkg.todo
            if todo in self.todoKnown :
                overwriteText = False
                do = True

                if self.installationStatus[self.currentPkg.name]['overwrite'] and self.installationStatus[self.currentPkg.name]['overwriteValue']:
                    todo = 'UPDATE'
                    overwriteText=True
                    self.installationStatus[self.currentPkg.name]['overwrite'] = False
                    
                elif self.installationStatus[self.currentPkg.name]['overwrite'] and not self.installationStatus[self.currentPkg.name]['overwriteValue']:
                    self.installationStatus[self.currentPkg.name]['overwrite'] = False
                    self.reason = 'ALREADY_IN_APP_DIR'
                    return False
                
                if do:
                    self.progressionPage.gaugeDesc.SetLabel('') # stupid but needed : otherwise fonts can't be mixed
                    self.progressionPage.gaugeDesc.SetLabel( self.__getGaugeDescTxt(todo,lenApps,self.idApp,overwriteText) )
                    self.progressionPage.gaugeDesc.Refresh()

                    self.progressionPage.gauge.SetRange(100)
                    app = AppManager( dotApps[self.idApp], todo, self.progressionPage, lenApps )
                    installedLocation=app.start()
                    NSLog('calling app.join()')
                    app.join()
                    if not app.getAppResult():
                        if not self.installationStatus[self.currentPkg.name]['overwrite']:
                            self.progressionPage.Overwrite( os.path.split(dotApps[self.idApp])[-1] )
                        return False
            else:
                self.reason = 'UNKNOWN_TODO' 
                return False
            print str(self.currentPkg)
            record=InstalledPackage(self.currentPkg.name,self.currentPkg.version,installedLocation)
            record.register()
            return True

    def finalizeContainer(self,package="None",lastStatement='init'):
        """Finalize container of current package.
        This method finalize container if needed. for the moment, it simply unmount dmg images."""

        self.currentType = self.currentPkg.installations[0].file.type

        #debug
        print
        print 'finalize container of '+ self.currentPkg.name
        print self.currentType + ' ' + str(self.idPkg)

        if self.currentType == 'dmg':
            if self.containers[self.idPkg] is not None and self.containers[self.idPkg].isMounted:
                self.progressionPage.gaugeDesc.SetLabel('Unmounting ' + self.currentPkg.name + ' image')
                self.progressionPage.gaugeDesc.Refresh()
                self.containers[self.idPkg].umount()
        #elif self.currentType == 'zip':
        #    if self.containers[self.idPkg] is not None and self.containers[self.idPkg].isExtracted:
        #        self.progressionPage.gaugeDesc.SetLabel('Deleting unpacked ' + self.currentPkg.name + ' archive files')
        #        self.progressionPage.gaugeDesc.Refresh()
        #        self.containers[self.idPkg].finish()
        return True

    def saveInstalled(self):
        """ save user' selection in the installed.xml file. call self.finished when finished """
        return True

        #debug
        print
        print 'saving installed distribution '
        print

        #self.progressionPage.gaugeDesc.SetLabel('                                                                                      ')
        self.progressionPage.gaugeDesc.SetLabel('Saving entries')
        self.progressionPage.gaugeDesc.Refresh()
       
        pathInstalled = self.progressionPage.maclibreWizard.maclibre.xmlUserPath
        distribSelected = self.progressionPage.maclibreWizard.selected
        distribInstalled = self.progressionPage.maclibreWizard.installed

        if os.path.exists(pathInstalled):
            os.remove(pathInstalled)
        
        # TODO : make it unicode-y
        #import codecs
        #fileInstalled = codecs.open(pathInstalled,'w','utf-8')
        #fileInstalled.write(  '<?xml version="1.0" encoding="UTF-8" ?>\n')
        fileInstalled = open(pathInstalled,'w')

        distribWord =  ' <Distribution Name="'+distribSelected.name+ '" '
        if distribSelected.version != '': versionWord =  ' Version="'+distribSelected.version+ '"  '
        else : versionWord =  ''
        if distribSelected.language != '': languageWord =  ' Language="'+distribSelected.language+ '"  '
        else : languageWord =  ''
        if distribSelected.installerMinVersion != '': installerMinVersionWord = ' InstallerMinVersion="'+distribSelected.installerMinVersion+ '"  '
        else : installerMinVersionWord =  ''
        fileInstalled.write(distribWord+versionWord+languageWord+installerMinVersionWord+ '>\n')

        listCategoryNameSelected = []
        for categorySelected in distribSelected.categories:
            listCategoryNameSelected.append(categorySelected.name)

        # add categories and packages previously installed not in distribSelected
        for categoryInstalled in distribInstalled.categories:
            if categoryInstalled.name not in listCategoryNameSelected:
                categoryWord =   ' <Category Name="'+categoryInstalled.name+ '">\n '
                categoryWord +=  ' <Packages> \n'
                for package in categoryInstalled.packages:
                    categoryWord += package.xml+  '\n'
                categoryWord +=  ' </Packages> \n'
                categoryWord +=  ' </Category> \n'
                fileInstalled.write(categoryWord)

        #add categories and packages from distribSelected
        for category in distribSelected.categories:
            atLeastOnePackage = False
            categoryWord =   ' <Category Name="'+category.name+ '">\n '
            categoryWord +=  ' <Packages>\n'

            listPackageNameSelected = []
            for package in category.packages:
                if not self.__cantBeInstalled(package):
                    listPackageNameSelected.append(package.name)

            # rewrite previously installed packages in the same category than the current one
            for categoryInstalled in distribInstalled.categories:
                if category == categoryInstalled:
                    for packageInstalled in categoryInstalled.packages:
                        if packageInstalled.name not in listPackageNameSelected:
                            atLeastOnePackage = True
                            categoryWord += packageInstalled.xml+  '\n'

            # write fresh installed/updated/reinstalled packages
            for package in category.packages:
                if not self.__cantBeInstalled(package):
                    atLeastOnePackage = True
                    categoryWord += package.xml+  '\n'

            categoryWord +=  ' </Packages> \n'
            categoryWord +=  ' </Category> \n'

            if atLeastOnePackage :
                fileInstalled.write(categoryWord)
        
        fileInstalled.write( ' </Distribution> ')
        fileInstalled.close()
        self.finished()

    def finished(self):
        self.progressionPage.gaugeDesc.SetLabel('                                                                                      ')
        self.progressionPage.gaugeDesc.SetLabel('Installation process finished')
        self.progressionPage.ForwardOnOff()
        self.progressionPage.maclibreWizard.pages[-1].cantBeInstalled = self.cantBeInstalled
        self.progressionPage.maclibreWizard.pages[-1].reasonsDict     =	self.reasonsDict
        self.progressionPage.gaugeDesc.Refresh()


    
    def __getGaugeDescTxt(self,todo,len,id,overwrite=False):
        todoWord=self.todoKnown[todo]
        if overwrite: overwriteWord = ' , overwriting '
        else : overwriteWord = ''
        if len > 1: nbFilesWord = '. file %d/%d' % (id+1,len)
        else : nbFilesWord = ''
        return todoWord + self.currentPkg.name + overwriteWord + nbFilesWord

    def __getContainer(self):
        """
        This method a container instance corresponding to self.currentPkg .
        Currently DmgContainer and ZipContainer are supported.
        If for any reasons something goes wrong (the container isn't supported) this method set self.reason.
        """ 
        filepath = os.path.join( self.progressionPage.maclibreWizard.maclibre.maclibreDir,'packages',
                     self.currentPkg.name, self.currentPkg.installations[0].file.name )
        if self.currentPkg.diskImageLocation=='offline':
            filepath=getResourcesPath()+'/'+self.currentPkg.installations[0].file.name
        if self.currentType == 'dmg' :
            container = DmgContainer(filepath)
        elif self.currentType == 'zip':
            container = ZipContainer(filepath)
        else :
            self.reason = 'UNKNOW_CONTAINER'
            container = ''
        return container

    def __AllPiecesCorrectlyDownloaded(self,indexPkg):
        """ Recursive (dependencies).
        This method return true if all needed pieces to install the given package
        (its position in self.orderToInstall) have been correctly downloaded, otherwise self.reason is set and it returns false.
        """
        if self.currentPkg.diskImageLocation=='offline':
            return True
        if not self.correctlyDownloaded[indexPkg] :
            self.reason = 'DOWNLOAD_FAILED'
            return False
        if self.orderToInstall[indexPkg].hasDependencies():
            booleanList=[]
            for dep in self.orderToInstall[indexPkg].getDependencies(self.progressionPage.maclibreWizard.selected):
                booleanList.append( self.__AllPiecesCorrectlyDownloaded( self.orderToInstall.index(dep) )  )
                if False in booleanList :
                    self.reason = 'DOWNLOAD_FAILED'
                    return False
        return True

    def __cantBeInstalled(self,package):
        """Return True if the given package is in self.cantBeInstalled, otherwise False """
        for [pkg,reason] in self.cantBeInstalled:
            if pkg == package:
                return True
        return False

    
    def __addInOrderToInstall(self,package,index=None):
        """ This method add the given package in self.orderToInstall according to the kind of the package (dependence or package) """
        if index is None:
            if package not in self.orderToInstall:
                self.orderToInstall.append(package)
        else:
            if package in self.orderToInstall:
                self.orderToInstall.remove(package)
                self.orderToInstall.insert(index,package)
            else:
                self.orderToInstall.insert(index,package)
#</Installer>



