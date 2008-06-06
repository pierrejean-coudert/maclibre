
import commands
import os
import re
import shutil

from PgmRetriever import PgmRetriever

#<DmgContainer>
class DmgContainer:
    """ This class provide access/informations to .dmg images """
    
    hdiutilPath = '/usr/bin/hdiutil '
    diskImageMounter = '/System/Library/CoreServices/DiskImageMounter.app/Contents/MacOS/DiskImageMounter '

    def __init__(self, filepath):
        self.dmgpath = filepath
        self.mountpoint = ""
        self.devmountpoint = ""
        self.isMounted = False
        self.gzFound = False
        self.oldDirContent = set(os.listdir ('/Volumes'))

    def mount(self):
        """ This method mount the dmg image  """
        if self.isMounted == False:
            
            # check if we have to deal with dmg.gz files
            gzStatus = re.search('.*dmg\.gz$',self.dmgpath)
            if( gzStatus ):
                print "Unpacking gz archive"
                shutil.copy(self.dmgpath,self.dmgpath + '.temp')
                self.gunzip()
                shutil.move(self.dmgpath + '.temp', self.dmgpath)
                self.dmgpath = re.sub('\.gz','',self.dmgpath)
                self.gzFound = True
                print 'Archive unpacked to ' + self.dmgpath
            # mount command depending on dmg image
            if self.withLicense() == False:
                mountCmd = DmgContainer.hdiutilPath+' attach '
                (status, result) = commands.getstatusoutput( mountCmd + '"'+self.dmgpath+'"')
            else:
                mountCmd = DmgContainer.diskImageMounter
                status = os.system( mountCmd + '"'+self.dmgpath+'"')
                if self.getMountPoint() == False:
                    status = 1
                
            if status == 0:
                self.isMounted = True
                # getting mount point
                if self.withLicense() == True:
                    self.mountpoint = self.getMountPoint()
                    self.devmountpoint = self.mountpoint
                    print "Mountpoint " + self.mountpoint
                else:
                    volumesLine = ''
                    for line in result.split('\n'):
                        if 'Volumes' in line:
                            volumesLine = line
                    volumesLine = volumesLine.split()
                    for elem in volumesLine:
                        if '/dev' in elem:
                            self.devmountpoint = elem
                        elif '/Volumes' in elem:
                            self.mountpoint = ' '.join( volumesLine[ volumesLine.index(elem): ] )
                self.retriever = PgmRetriever(self.mountpoint)

    def umount(self):
        """ This method unmount the dmg image """
        if self.isMounted == True:
            print "Unmounting " + self.devmountpoint
            umountCmd = DmgContainer.hdiutilPath+' detach '
            (status, result) = commands.getstatusoutput( umountCmd + '"'+self.devmountpoint+'"' )
            if status == 0:
                self.mountpoint = ''
                self.devmountpoint=''
                self.isMounted = False
                if self.gzFound:
                    os.remove(self.dmgpath)

    def getDotApp(self):
	""" This method return a list of paths corresponding to the .app directories inside the image when it's mounted."""	
	return self.retriever.retrieveDir('.app')

    def getDotPkg(self):
	""" This method return a list of paths corresponding to the .pkg directories inside the image when it's mounted. """
	return self.retriever.retrieveDir('.pkg')
	
    def withLicense(self):
        """ This method checks if dmg displays license aggrement before mounting a disk image. """
        checkCmd = DmgContainer.hdiutilPath+' imageinfo '
        (status, result) = commands.getstatusoutput( checkCmd + '"'+self.dmgpath+'"|grep "Software License Agreement"')
        searchStatus = re.search('.*Software License Agreement: true.*',result)
        if( searchStatus ):
            return True
        else:
            return False
    
    def getMountPoint(self):
        """ This method search for mount point of dmg disk image."""
        for newDirName in os.listdir('/Volumes'):
            if(newDirName not in self.oldDirContent):
                return '/Volumes/' + newDirName
        return False
    
    def gunzip(self):
        """ This method unpack the the gz archive (used for dmg.gz disk images)."""
        (status, result) = commands.getstatusoutput( 'gunzip ' + '"'+self.dmgpath+'"')
        return status
        
    

#</DmgContainer>

#<main>
if __name__ == "__main__":
    print DmgContainer.__doc__
#</main>
    
