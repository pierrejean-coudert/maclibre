
import threading
import os
import urllib
import tools

from MD5 import *

#<Downloader>
class Downloader(threading.Thread):
    """ This class provide an easy way to download a file """

    def __init__(self,url,destination,filesize=0, GUI_ProgressionPage=None,md5=None):
        """ This __init__ method takes the url of the the file to download
        as first argument and the destination file (full path) as second.
        The file is downloaded in a separated thread.
        The third argument is the size of the file to download (in bytes)
        (Needed if you want to know the advancement of the download, cf method statement() ).
        The fourth argument is a GUI_ProgressionPage instance. If given, the behaviour of this class will be special:
        update a wx.Gauge and launch another Download. cf GUI_ProgressionPage and Installer.
        The fifth argument is the md5 of the file to download. If given, file's md5 sum is checked.
        """
        threading.Thread.__init__(self)	
        self.url = url
        self.destination = destination
        self.filesize = filesize
        self.counter = 0
        self.progressionPage = GUI_ProgressionPage
        self.md5 = md5
        self.download= ''
        self.useProgressFunction = False
        self.progressObject = None

        if self.progressionPage is not None:
            self.progressionPage.gauge.SetRange(100)

        if self.filesize > 1048576:
            self.blocksize = 307200
        else :
            self.blocksize = 8192
    
    def setProgressObject(self, useProgressFunction, progressObject):
        self.useProgressFunction = useProgressFunction
        self.progressObject = progressObject
    
    def run(self):
        """ This method launch the download """
        try:

            if os.path.exists(self.destination):
                os.remove(self.destination)

            if not self.useProgressFunction:
                print 'Downloading: ' + self.url
            
            webFile = urllib.urlopen(self.url)
            outputFile = open(self.destination,"wb")

            while 1:
                data = webFile.read(self.blocksize) # if connection is lost during downloading, it blocks here
                if not data: break
                outputFile.write(data)
                self.counter = self.counter + 1
                
                if self.useProgressFunction:
                    self.progressObject.setValue(self.statement())
            
                if self.progressionPage is not None and self.filesize != 0:
                    self.progressionPage.gauge.SetValue( self.statement() )
                    pkgPieceValue = self.progressionPage.installer.overallPkgPieceSize * self.statement() / 100
                    overallValue = self.progressionPage.installer.overallProgressValue + pkgPieceValue
                    self.progressionPage.installer.setOverallProgressValue( overallValue )
                    downloadedDataSize = self.counter * self.blocksize
                    if downloadedDataSize > self.filesize:
                        downloadedDataSize = self.filesize
                    #self.progressionPage.smallDesc.SetLabel('')
                    self.progressionPage.smallDesc.SetLabel( 
                    tools.byteSizeToReadableSize(downloadedDataSize) + ' of '+ tools.byteSizeToReadableSize(self.filesize) )
                    self.progressionPage.smallDesc.Refresh()

            
            webFile.close()
            outputFile.close()
            self.download = True

        except IOError, (errno, strerror):
            print "I/O error(%s): %s" % (errno, strerror)
            self.download = False
            
        if self.md5 is not None:
            if (MD5(self.destination,self.md5)).isCorrect():
                self.download = True
            else:
                self.download = False

        if self.progressionPage is not None:
            try:
                self.progressionPage.installer.correctlyDownloaded[self.progressionPage.installer.idPkg] = self.download
        
            except IndexError:
                self.progressionPage.installer.correctlyDownloaded.append(self.download)
        
                self.progressionPage.gauge.SetValue(0)
                self.progressionPage.gaugeDesc.SetLabel('')
                self.progressionPage.smallDesc.SetLabel('')


    def downloadResult(self):
        """ This method return False if the url is incorrect, the internet connection is down or the MD5 given and MD5 calculated aren't egal.
        True if the download ran smoothly. If the download has not been started or is running it return an empty string : '' """
        return self.download

    def statement(self):
        """ This method return a percentage of the download advancement if you have specified the file size, else None. """
        if self.filesize == 0:
            return None
        else :
            return ( self.counter*self.blocksize*100 ) / self.filesize

#</Downloader>

#<main>
if __name__ == "__main__":
    print Downloader.__doc__	
#</main>
