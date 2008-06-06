import copy
import os

import tools
import shutil
import Config
from Distribution import *
from Downloader import *
import Parser

#<DistributionGenerator>
class DistributionGenerator:
    """ This class is used for generation of MacLibre distribution."""

    def __init__(self, distribution=None, config=None, osxversion='all', appsDiskImagesPath='../bin/AppsDiskImages', downloadDirPath = '../bin/AppsDownloads'):	
        self.distribution = distribution
        self.config = config
        self.osxversion = osxversion
        self.appsDiskImagesPath = appsDiskImagesPath
        self.processStatus = False
        self.downloadDirPath = downloadDirPath

    def process(self):
        """ This method gets the list of packages which have to be downloaded for distribution generation"""
        for category in self.distribution.categories :
            for package in category.packages :
                if  package.showable:
                    if self.__installable(package):
                        print 'Processing package: ' + package.name
                                                
                        if ( self.config.version == 'mixed' and package.diskImageLocation == 'offline' ) or self.config.version == 'offline':
                            print 'Version: ' + self.config.version
                            self.download(package)
                        else:
                            print 'Version: online'
                    else:
                        print 'Error while processing: ' + package.name
        self.processStatus = True
        
    def download(self, package):
        
        for installation in package.installations:
            file = installation.file
            
            if installation.version != '':
                print 'app version: ' + installation.version
            else:
                print 'app version: ' + package.version

            
            alreadyDownloaded = False
            packageDir = os.path.join( '~/.maclibre/packages/', package.name )
            
            maclibreDir = os.path.join( packageDir, file.name ) 
            downloadFile = os.path.join ( self.downloadDirPath, file.name)
            destination = os.path.join( self.appsDiskImagesPath ,file.name)
            
            dirList = [ maclibreDir, downloadFile]
            
            for pkgFile in dirList:
                print 'Checking existence & md5 of ' + pkgFile
                if os.path.exists(pkgFile) and (MD5(pkgFile,file.md5)).isCorrect():
                    alreadyDownloaded = True
                    print 'Already downloaded, copying file:'
                    print 'source: ' + downloadFile
                    print 'destination: ' + destination  
                    shutil.copy( pkgFile, destination)
            
            lenUrl = len(file.urls)

            if alreadyDownloaded:
                continue
            else:
                url = file.urls[0]
                print 'url: ' + url
                print 'destination: ' + destination
                #os.makedirs( packageDir )
                downloader = Downloader( url , downloadFile , file.size, None, md5=file.md5 )
                downloader.setProgressObject(True, ProgressBar(100,'*') )
                downloader.start()
                downloader.join()
                
                #copy file to destination
                print 'Copying file:'
                print 'source: ' + downloadFile
                print 'destination: ' + destination           
                shutil.copy( downloadFile, destination)
        return True


    
    def createApp(self):
        print '\nBuilding .app for ' + self.config.version + ' distribution version'
        if self.config.version == 'offline' or self.config.version == 'mixed':
            os.system( "python setup.py py2app --offline" )
        else:
            os.system( "python setup.py py2app" )
        print 'Building .app finished'
    
    def createDmg(self):
        print '\nBuilding dmg image for ' + self.config.version + ' version...'
        oldCwd = os.getcwd()
        builderPath = os.path.join(oldCwd,'DmgBuilder')
        os.chdir(builderPath)
        if self.config.version == 'offline' or self.config.version == 'mixed':
            shutil.copy( os.getcwd() + '/offline.mk', os.getcwd() + '/config.mk' )
        else:
            shutil.copy( os.getcwd() + '/online.mk', os.getcwd() + '/config.mk' )
        
        os.system( "make" )
        os.remove( os.getcwd() + '/config.mk')
        os.chdir(oldCwd)
        print 'Building dmg image finished'
    
    def clean(self):
        print '\nCleaning after generation'
        shutil.rmtree( self.appsDiskImagesPath )
        

    def __installable(self,package):
        """ This method returns True if the given package could/should be added in the tree, otherwise False. Delete unneeded Installations object in 
        Maclibre Distribution """

        installationsToRemove = []

        installationNumber = 0
        print '\nPackage: ' + package.name +'\n----------------------------------'
        for installation in package.installations:
            print 'Installation ' + str(installationNumber) + ': ' + package.name + ' OSMin: ' + installation.OSMin + ' OSMax: ' + installation.OSMax 
            installationNumber += 1
            if self.osxversion != 'all':
                if not (self.osxversion >= installation.OSMin and self.osxversion <= installation.OSMax) :  
                    installationsToRemove.append(installation)

        print
        # delete un-needed installations object
        if self.osxversion != 'all':
            for itr in installationsToRemove:
                package.installations.remove(itr)        
        
        # set Installation version (if exists) to Package version
        if package.version == '' and package.installations[0].version != '':
            package.version = package.installations[0].version

        # all the same for dependencies
        if package.hasDependencies():
            dependenciesList = package.getDependencies(self.distribution)
            if len(dependenciesList) == 0:
                return False
            
            for dep in dependenciesList :
                if not self.__installable(dep):
                    return False

        return True


#</DistributionGenerator>

#<ProgressBar>
class ProgressBar: 
    def __init__(self, finalcount, progressChar=None):
        import sys
        self.finalcount = finalcount
        self.blockcount = 0
        
        # See if caller passed me a character to use on the
        # progress bar (like "*").  If not use the block
        # character that makes it look like a real progress
        # bar.
        if not progressChar: 
            self.block=chr(178)
        else:                
            self.block=progressChar
        # Get pointer to sys.stdout so I can use the write/flush
        # methods to display the progress bar.
        self.f = sys.stdout
        # If the final count is zero, don't start the progress gauge
        if not self.finalcount : 
            return
        
        self.f.write('\n------------------ % Progress ---------------------\n')
        self.f.write('0-----------------------------------------------100\n')
        return

    def setValue(self, count):
        # Make sure I don't try to go off the end (e.g. >100%)
        count = min(count, self.finalcount)
        # If finalcount is zero, I'm done
        if self.finalcount:
            percentcomplete=int(round(100*count/self.finalcount))
            if percentcomplete < 1: percentcomplete=1
        else:
            percentcomplete = 100
            
        blockcount=int(percentcomplete/2)

        if blockcount > self.blockcount:
            for i in range(self.blockcount,blockcount):
                self.f.write(self.block)
                self.f.flush()
                
        if percentcomplete == 100: 
            self.f.write("\n")
        self.blockcount = blockcount
        return
#</ProgressBar>


def prepare():
    print 'Preparing packages...'

    if os.path.isdir(appsDiskImagesPath):
        shutil.rmtree( appsDiskImagesPath )
    print 'Creating Apps Disk Images directory: ' + appsDiskImagesPath
    os.makedirs( appsDiskImagesPath )
        
    if not os.path.isdir(downloadDirPath):
        print 'Creating Apps downloads directory: ' + downloadDirPath
        os.makedirs( downloadDirPath )
    

    print 'Config file: ' + xmlConfigPath
    print 'Apps Disk Images path: ' + appsDiskImagesPath
    print 'Preparing for Mac OS X version: ' + osxversion
    
    
    defaultConfig.printInfo()
    # parse packages xml file
    parser = Parser.Parser(defaultConfig.url)
    distribution = parser.parse()
    # prepare for generation
    generator = DistributionGenerator(distribution, defaultConfig, osxversion, appsDiskImagesPath, downloadDirPath)
    generator.process()
    
    print 'Preparing finished'

class Usage:
    """
    DistribGenerator.py - script for generation of MacLibre distributions

    Usage:
        % python DistribGenerator.py <argument>
        
        Arguments:
            build-all - all steps of building distribution
            prepare   - preparing distribution packages 
            build-app - building .app (prepare has to be called before)
            build-dmg - building dmg disk image (prepare & build-app has to be called before)
            clean     - cleaning after generation
        
    For this help :
        % python DistribGenerator.py help
    """

#<main>
if __name__ == '__main__':
    print 'MacLibre Distribution Generator\n----------------------------------------\n'
    xmlConfigPath = '../xml/config.xml'
    appsDiskImagesPath = '../bin/AppsDiskImages'
    downloadDirPath = '/Volumes/Other/MacLibre/AppsDownloads'
    osxversion = 'all'
    
    # read configuration
    configuration = Config.Configuration(xmlConfigPath)
    # get default config
    defaultConfig = configuration.getDefaultConfig()

    import sys
    
    if len(sys.argv) <= 1:
        print Usage.__doc__
        sys.exit(1)
    
    if sys.argv[1] == 'prepare':
        prepare()
    elif sys.argv[1] == 'build-all':
        prepare()
        DistributionGenerator(config=defaultConfig).createApp()
        DistributionGenerator(config=defaultConfig).createDmg()
        DistributionGenerator(appsDiskImagesPath=appsDiskImagesPath).clean()
        
    elif sys.argv[1] == 'build-app':
        DistributionGenerator(config=defaultConfig).createApp()
    elif sys.argv[1] == 'build-dmg':
        DistributionGenerator(config=defaultConfig).createDmg()
    elif sys.argv[1] == 'clean':
        DistributionGenerator( appsDiskImagesPath=appsDiskImagesPath).clean()
    elif sys.argv[1] == 'help':
        print Usage.__doc__
    else:
        print Usage.__doc__

#</main>
