#
#  Downloader3.py
#  MacLibre3
#
#  Created by Ezra on 6/9/08.
#
#  The Downloader class asynchronously downloads files.  This replaces Downloader.py from Maclibre2 and can be used the same way.
#

from Foundation import *
from AppKit import *
from WebKit import *
import objc

from Prefs import Prefs

class Downloader(NSObject):
    def setup(self, url, destination, filesize=0, GUI_ProgressionPage=None, md5=None, maclibre3=None):
        """Set up a Downloader will all relevant parameters."""
        self.url=url
        #self.destination=NSSearchPathForDirectoriesInDomains(NSApplicationSupportDirectory, NSUserDomainMask, True)[0]
        self.destination=destination
        print self.destination
        self.filesize=filesize
        self.progressionPage=GUI_ProgressionPage
        self.md5=md5
        self.download=False
        self.useProgressFunction=False
        self.progressObject = None
        self.response=None
        self.bytesReceived=0
        self.finishFunction=None
        self.prefs=Prefs()
        self.triedToResume=False
        maclibre3.registerDownloader(self)
        self.maclibre3=maclibre3
        
        if self.progressionPage is not None:
            self.progressionPage.gauge.SetRange(100)
            
        return self
    
    def registerFinishFunction(self, object, function):
        """After the download is successful, the 'function' method of the object 'object' will be called."""
        self.finishFunction=getattr(object, function)
    
    def setProgressObject(self, useProgressFunction, progressObject):
        self.useProgressFunction = useProgressFunction
        self.progressObject = progressObject
    
    def start(self):
        self.run()
    
    def join(self):
        """Block current thread until download finishes, while keeping UI responsive."""
        runloop=NSRunLoop.currentRunLoop()
        while self.download == False and runloop.runMode_beforeDate_(NSDefaultRunLoopMode, NSDate.distantFuture()):
            pass
    
    def run(self):
        """Start the download, resuming if appropriate."""
        objc.setVerbose(1)
        if not self.useProgressFunction:
            print 'Downloading: ' + self.url
        self.maclibre3.pauseButton.setHidden_(False)
        (resume,self.response,self.bytesReceived) = self.prefs.getDownload(self.url)
        if resume:
            try:
                print resume
                self.dl=NSURLDownload.alloc().initWithResumeData_delegate_path_(resume, self, self.destination)
                if self.dl:
                    self.dl.setDeletesFileUponFailure_(False)
                    return
            except:
                pass
        request=NSURLRequest.requestWithURL_(NSURL.URLWithString_(self.url))
        NSLog('request ok')
        self.dl=NSURLDownload.alloc().initWithRequest_delegate_(request, self)
        NSLog(str(self.dl))
        if self.dl:
            self.dl.setDestination_allowOverwrite_(self.destination,True)
            self.dl.setDeletesFileUponFailure_(False)
    
    def download_decideDestinationWithSuggestedFilename_(self, download, name):
        """Delegate function.  Called to determine where the download will be stored."""
        NSLog('decideDestinationWithSuggestedFilename')
        self.dl.setDestination_allowOverwrite_(self.destination,True)

    
    def download_didFailWithError_(self, download, error):
        """Delegate function.  Called when download fails."""
        self.maclibre3.pauseButton.setHidden_(True)
        if error.domain()==NSURLErrorDomain and error.code()==-3001:
            NSLog('Resume failed, starting from beginning')
            self.prefs.clearDownload(self.url)
            self.run()
            return
        NSLog('Download Failed')
        self.download=False
        #self.dl.release()
        NSLog(error.localizedDescription())
        print error.domain()
        print error.code()
        NSLog(error.userInfo().objectForKey_(NSErrorFailingURLStringKey))
        
    def downloadDidBegin_(self, download):
        NSLog('begin')
    
    def downloadDidFinish_(self, download):
        """Delegate function.  Called when download finishes successfully."""
        NSLog('didFinish')
        #self.dl.release()
        self.download=True
        self.prefs.clearDownload(self.url)
        self.maclibre3.pauseButton.setHidden_(True)
        #if self.progressionPage:
        #    self.progressionPage.installer.correctlyDownloaded[self.progressionPage.installer.idPkg] = self.download
        if self.finishFunction:
            self.finishFunction()
        
    def downloadResult(self):
        return self.download
        
    def statement(self):
        """Return the percentage of the download which is complete."""
        if self.response:
            total=self.response.expectedContentLength()
            if total is not NSURLResponseUnknownLength:
                return 100.0*self.bytesReceived/total
        else:
            return 0
        
    def download_didReceiveResponse_(self, download, response):
        """Delegate function.  Called when the downloader receives a response from the server."""
        NSLog('didReceiveResponse')
        self.bytesReceived=0
        self.response=response
        
    def download_didReceiveDataOfLength_(self, download, length):
        """Delegate function.  Called when downloader receives data.  Will be called frequently during downloads."""
        #print 'didReceiveData'
        #NSLog('didReceiveDataOfLength')
        self.bytesReceived+=length
        if self.progressionPage is not None:
            self.progressionPage.gauge.SetValue(self.statement())
            self.progressionPage.smallDesc.SetLabel("%.1fMB / %.1fMB"% (self.bytesReceived/1000000.0, self.response.expectedContentLength()/1000000.0))
        #print self.dl.resumeData()
        #self.dl.setDeletesFileUponFailure_(False)
        #self.dl.cancel()
        #print self.dl.resumeData()
        #print self.destination
        #resume=self.dl.resumeData()
        #self.prefs.setDownload(self.url,resume)
        #self.dl=NSURLDownload.alloc().initWithResumeData_delegate_path_(resume, self, self.destination)
        #self.dl.setDeletesFileUponFailure_(False)