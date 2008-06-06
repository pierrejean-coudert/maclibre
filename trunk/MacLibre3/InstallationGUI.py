from Foundation import *
from AppKit import *
import objc

class Gauge(NSObject):
    def init_(self, progressbar):
        self.progressbar=progressbar
        return self
    
    def SetValue(self, value):
        self.progressbar.setDoubleValue_(value)
        
    def SetRange(self, range):
        self.progressbar.setMaxValue_(range)

class Label(NSObject):
    def init_(self, label):
        self.label=label
        return self
        
    def SetLabel(self, text):
        self.label.setStringValue_(text)
        
    def Refresh(self):
        pass
        
        
class Page(NSObject):
    def init_(self):
        self.packagesCount=0
        return self
    
    def increment(self, num):
        self.packagesCount+=num

class InstallationGUI(NSObject):
    overallProgress = objc.IBOutlet()
    packageIcon = objc.IBOutlet()
    packageProgress = objc.IBOutlet()
    packageStatus = objc.IBOutlet()
    overallStatus = objc.IBOutlet()
    smallStatus=objc.IBOutlet()
    
    def setup(self, wizard, maclibre, installer):
        self.maclibreWizard=wizard
        self.maclibre=maclibre
        self.installer=installer
        self.overallGauge=Gauge.alloc().init_(self.overallProgress).retain()
        self.gauge=Gauge.alloc().init_(self.packageProgress).retain()
        self.gaugeDesc=Label.alloc().init_(self.packageStatus).retain()
        self.overallSmallDesc=Label.alloc().init_(self.overallStatus).retain()
        self.smallDesc=Label.alloc().init_(self.smallStatus).retain()
    
    def showAppLogoImage(self, package):
        NSLog(package.logoImageFile)
        self.packageIcon.setImage_(NSImage.imageNamed_(package.logoImageFile))
        
    def setSelected(self, dist, inst):
        self.selected=dist
        self.installed=inst
        self.selected.categories=[category for category in dist.categories if len([package for package in category.packages if package.todo == 'INSTALL'])>0]
        self.pages=[None,None,Page.alloc().init_().retain()]
        for category in self.selected.categories:
            category.packages = [package for package in category.packages if package.todo == 'INSTALL']
            self.pages[2].increment(len(category.packages))
            
    def enableAppLogoImage(self, value):
        pass
        
    def ForwardOnOff(self):
        pass
            