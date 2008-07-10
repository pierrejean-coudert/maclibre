#
#  Downloader3.py
#  MacLibre3
#
#  Created by Ezra on 6/9/08.
#  Copyright (c) 2008 __MyCompanyName__. All rights reserved.
#

from Foundation import *
from AppKit import *
from WebKit import *
import objc

from Prefs import Prefs

class Downloader(NSObject):
    def setup(self, url, destination, filesize=0, GUI_ProgressionPage=None, md5=None, maclibre3=None):
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
        maclibre3.registerDownloader(self)
        
        if self.progressionPage is not None:
            self.progressionPage.gauge.SetRange(100)
            
        return self
    
    def registerFinishFunction(self, object, function):
        self.finishFunction=getattr(object, function)
    
    def setProgressObject(self, useProgressFunction, progressObject):
        self.useProgressFunction = useProgressFunction
        self.progressObject = progressObject
    
    def start(self):
        self.run()
    
    def join(self):
        runloop=NSRunLoop.currentRunLoop()
        while self.download == False and runloop.runMode_beforeDate_(NSDefaultRunLoopMode, NSDate.distantFuture()):
            pass
    
    def run(self):
        objc.setVerbose(1)
        if not self.useProgressFunction:
            print 'Downloading: ' + self.url
        (resume,self.response) = self.prefs.getDownload(self.url)
        if resume:
            print resume
            self.dl=NSURLDownload.alloc().initWithResumeData_delegate_path_(resume, self, self.destination)
            if self.dl:
                self.dl.setDeletesFileUponFailure_(False)
        else:
            request=NSURLRequest.requestWithURL_(NSURL.URLWithString_(self.url))
            NSLog('request ok')
            self.dl=NSURLDownload.alloc().initWithRequest_delegate_(request, self)
            NSLog(str(self.dl))
            if self.dl:
                self.dl.setDestination_allowOverwrite_(self.destination,True)
                self.dl.setDeletesFileUponFailure_(False)
    
    def download_decideDestinationWithSuggestedFilename_(self, download, name):
        NSLog('decideDestinationWithSuggestedFilename')
        self.dl.setDestination_allowOverwrite_(self.destination,True)

    
    def download_didFailWithError_(self, download, error):
        NSLog('Download Failed')
        self.download=False
        #self.dl.release()
        NSLog(error.localizedDescription())
        NSLog(error.userInfo().objectForKey_(NSErrorFailingURLStringKey))
        
    def downloadDidBegin_(self, download):
        NSLog('begin')
    
    def downloadDidFinish_(self, download):
        NSLog('didFinish')
        #self.dl.release()
        self.download=True
        self.prefs.clearDownload(self.url)
        #if self.progressionPage:
        #    self.progressionPage.installer.correctlyDownloaded[self.progressionPage.installer.idPkg] = self.download
        if self.finishFunction:
            self.finishFunction()
        
    def downloadResult(self):
        return self.download
        
    def statement(self):
        if self.response:
            total=self.response.expectedContentLength()
            if total is not NSURLResponseUnknownLength:
                return 100.0*self.bytesReceived/total
        else:
            return 0
        
    def download_didReceiveResponse_(self, download, response):
        NSLog('didReceiveResponse')
        self.bytesReceived=0
        self.response=response
        
    def download_didReceiveDataOfLength_(self, download, length):
        #NSLog('didReceiveDataOfLength')
        self.bytesReceived+=length
        if self.progressionPage is not None:
            self.progressionPage.gauge.SetValue(self.statement())
            self.progressionPage.smallDesc.SetLabel("%f / %f"% (self.bytesReceived, self.response.expectedContentLength()))
        #print self.dl.resumeData()
        #self.dl.setDeletesFileUponFailure_(False)
        #self.dl.cancel()
        #print self.dl.resumeData()
        #print self.destination
        #resume=self.dl.resumeData()
        #self.prefs.setDownload(self.url,resume)
        #self.dl=NSURLDownload.alloc().initWithResumeData_delegate_path_(resume, self, self.destination)
        #self.dl.setDeletesFileUponFailure_(False)