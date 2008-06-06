
import wx
import wx.wizard as wiz
import wx.lib.mixins.listctrl as listmix
import sys
import tools
import os

from Installer import Installer
from Installer import InstallerProgressThread
from Parser import Parser
from User import User
from GUI_PackageChooser import *
from Distribution import *

### <TODO>
# add a link to host page for the 'download new version of this installer' MessageDialog
### </TODO>

#<GUI_Wizard>
class GUI_Wizard(wiz.Wizard):
    """ wx.wizard.Wizard  """

    def __init__(self, parent, id=-1, title=""):
	wiz.Wizard.__init__(self,parent, id, title)
	
    def DisableButton(self,the_id):
	"""Disable the button on the wizard with the given ID.
	Returns True if the button ID was found, false if not"""
	try:
	    button = self.FindWindowById(the_id)
	except:
	    return False
	button.Enable(False)
	return True

    def EnableButton(self,the_id):
	"""Enable the button on the wizard with the given ID.
	Returns True if the button ID was found, false if not"""
	try:
	    button = self.FindWindowById(the_id)
	except:
	    return False
	button.Enable(True)
	return True
#</GUI_Wizard>

#<GUI_MaclibreWizard>
class GUI_MaclibreWizard(wx.App):
    """ This class is the skeleton for the wizard """

    def OnInit(self):
        frame = wx.Frame(None,-1, "MacLibre")
	self.wizard = GUI_Wizard(frame, title="MacLibre" )
	self.pages = [] # a list for stocking pages
	self.user = '' # an instance of User
	self.distribution = Distribution() # : maclibre distribution
	#self.installed : previously installed distribution
	#self.selected : tree selected distribution
	#self.maclibre : current MacLibre instance
	return True

    def addPage(self,WizardPage):
	""" Add WizardPage to the wizard """
	self.pages.append(WizardPage)

	if len(self.pages) > 1:
	    wiz.WizardPageSimple_Chain( self.pages[-2] , self.pages[-1] )

    def run(self):
	""" launch the wizard """
	if self.wizard.RunWizard( self.pages[0] ):
	    print "Wizard completed successfully"
	else:
	    print "Wizard was cancelled"
#</GUI_MaclibreWizard>

#</GUI_WizardPage>
class GUI_WizardPage(wiz.WizardPageSimple):
    """ super class for each page in this wizard  """

    def __init__(self, MaclibreWizard, title):
	"""
	MaclibreWizard : an instance of GUI_MaclibreWizard
	title : title to set for this page
	"""
	wiz.WizardPageSimple.__init__(self, MaclibreWizard.wizard)

        self.titlePageFont = wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD)
	self.fieldFont = wx.Font(10, wx.SWISS, wx.NORMAL, wx.FONTWEIGHT_LIGHT)
	self.labelFont = wx.Font(11, wx.SWISS, wx.NORMAL, wx.BOLD)

        self.sizer = self.makePageTitle(title)
	self.Bind(wiz.EVT_WIZARD_PAGE_CHANGING, self.OnWizPageChanging)
	self.Bind(wiz.EVT_WIZARD_PAGE_CHANGED, self.OnWizPageChanged)
	self.Bind(wiz.EVT_WIZARD_CANCEL, self.OnWizCancel)
	self.maclibreWizard = MaclibreWizard
    
    def makePageTitle(self, title):
	sizer = wx.BoxSizer(wx.VERTICAL)
	self.SetSizer(sizer)
	title = wx.StaticText(self, -1, title)
	title.SetFont( self.titlePageFont )
	sizer.Add(title, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
	sizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND|wx.ALL, 5)
	return sizer
    
    def OnWizCancel(self,evt):
	""" used when the cancel button is pressed  """
	pass

    def OnWizPageChanging(self, evt):
	""" used when the current page is changing """
	pass

    def OnWizPageChanged(self, evt):
	""" used when the current page is changed """
	pass

#</GUI_WizardPage>

#</GUI_FirstPage>
class GUI_FirstPage(GUI_WizardPage):
    """ first page of the wizard. """
    
    def __init__(self, MaclibreWizard):
        GUI_WizardPage.__init__(self, MaclibreWizard , 'Welcome to MacLibre 2')
	
        # description 
        desc = wx.StaticText(self, -1,'MacLibre is a rigorous selection of free, legal software for OS X.')
        desc.SetFont( self.fieldFont )
        self.sizer.Add( desc, 1, wx.ALIGN_CENTRE|wx.ALL )

        # 	# languages choices
        
        #descChoice = wx.StaticText(self, -1,'Language of the packages : ')
        #descChoice.SetFont( self.fieldFont )
        # 	self.choice = wx.Choice(self, -1, (100, 50), choices = ['english', 'french'] )
        # 	self.choice.SetFont( self.fieldFont )
        #       self.Bind(wx.EVT_CHOICE, self.EvtChoice, self.choice)
        # 	choicesSizer = wx.BoxSizer(wx.HORIZONTAL)
        # 	choicesSizer.Add(descChoice)
        # 	choicesSizer.Add(self.choice)
        # 	self.sizer.Add(choicesSizer,0, wx.ALIGN_CENTRE|wx.ALL, 3)

        # stage Description

        self.gaugeDesc = wx.StaticText(self, -1,'                                      ', style=wx.ALIGN_CENTRE)
        self.gaugeDesc.SetFont( self.fieldFont )
        self.sizer.Add( self.gaugeDesc, 0, wx.ALIGN_CENTRE|wx.ALL, 3 )
        
        # background image
        self.backgroundImagePath = tools.getResourcesPath() + '/MacLibreBackground.png'
        
        if os.path.isfile(self.backgroundImagePath):
            self.backgroundImage = wx.StaticBitmap(self, -1)
            self.backgroundImage.SetPosition((50,60))
            png = wx.Image(self.backgroundImagePath , wx.BITMAP_TYPE_ANY).ConvertToBitmap()
            self.backgroundImage.SetBitmap(png)
        else:
            print "Couldn't find background image file at location:" + self.backgroundImagePath+os.getcwd()
        
            	
    def EvtChoice(self,evt):
        print evt.GetString()

    def OnWizPageChanged(self,evt):
        self.gaugeDesc.Enable(True)
        self.gaugeDesc.SetLabel('')

    def OnWizPageChanging(self, evt):
        """
        Download the latest package list (maclibre.xml), parse it and the installed.xml file.
        Check if the current version of this installer is sufficient for installing maclibre.
        call GUI_PackageSelection.GUI_PackageChooser.fill()
        """
        self.gaugeDesc.Enable(True)
        self.gaugeDesc.SetLabel('Download latest package list...')
        self.gaugeDesc.Refresh()
        
        # dl maclibre xml
        while self.maclibreWizard.maclibre.chooseWebXml() == False:
            md = wx.MessageDialog(self, 'Check your internet connection. Do you want to reconnect ?', caption="Can't continue", style=wx.YES_NO|wx.YES_DEFAULT )
            status = md.ShowModal()
            md.Destroy()
            if status == 5104:
                evt.Veto()
                sys.exit(1)
        
        self.gaugeDesc.SetLabel('Building packages tree...')
        self.gaugeDesc.Refresh()
        #parserWeb = Parser('/Users/powerbook/checkouts/MacLibre2/xml/en.xml')
        parserWeb = Parser(self.maclibreWizard.maclibre.xmlMaclibrePath)
        parserUser = Parser(self.maclibreWizard.maclibre.xmlUserPath)
        self.maclibreWizard.distribution = parserWeb.parse()
        if self.maclibreWizard.distribution.installerMinVersion > self.maclibreWizard.maclibre.version :
            # add a link to host page
            md = wx.MessageDialog(self, 'You need to download the new version of maclibre installer for upgrading this distribution', caption="Can't continue", style=wx.OK )
            md.ShowModal()
            md.Destroy()
            evt.Veto()
            sys.exit(1)
        else:
            self.maclibreWizard.installed =  parserUser.parse()
            self.maclibreWizard.pages[1].pkgCh.fill()
        
#</GUI_FirstPage>

#</GUI_PackageSelection>
class GUI_PackageSelection(GUI_WizardPage):
    """ second page of the wizard. contain a GUI_PackageChooser and a GUI_PanelDescription """

    def __init__(self, MaclibreWizard):
        GUI_WizardPage.__init__(self, MaclibreWizard , 'Package selection')

        
        # Package Chooser 
        self.panelDesc = GUI_PanelDescription(self)
        self.pkgCh = GUI_PackageChooser( self, self.panelDesc, self.maclibreWizard )

        #explanation text
        desc = wx.StaticText(self, -1,'Double Click for selecting the package you want to install, re-install or update', style=wx.ALIGN_CENTRE)
        desc.SetFont( self.fieldFont )

        #sizers
        container = wx.BoxSizer(wx.HORIZONTAL)
        container.Add( self.pkgCh, 2, wx.EXPAND|wx.ALL|wx.ALIGN_CENTER,5 )
        container.Add( self.panelDesc, 3,  wx.EXPAND|wx.ALL|wx.ALIGN_CENTER,5 )
        self.sizer.Add( desc, -1, wx.EXPAND|wx.ALL|wx.ALIGN_CENTER )
        self.sizer.Add( container, 0, wx.ALIGN_CENTER )


    def OnWizPageChanging(self, evt):
        """ call GUI_PackageSelection.GUI_PackageChooser.setSelectedDistribution() """
        
        if evt.GetDirection() == False:
            return
        
        self.maclibreWizard.pages[1].pkgCh.setSelectedDistribution()
        if len( self.maclibreWizard.selected.categories) == 0 and evt.GetDirection() :
            (wx.MessageDialog(self, 'No packages selected', caption="Nothing to do", style=wx.OK )).ShowModal()
            evt.Veto()
            return
        self.maclibreWizard.pages[2].createImageList()
        self.maclibreWizard.pages[2].fillSelectionList()

#</GUI_PackageSelection>

#</GUI_SelectionConfirmationPage>
class GUI_SelectionConfirmation(GUI_WizardPage):
    """ Selection confirmation wizard page. """
    
    def __init__(self, MaclibreWizard):
        GUI_WizardPage.__init__(self, MaclibreWizard , 'Selected packages')
	
        # description 
        self.desc = wx.StaticText(self, -1,"")
        self.desc.SetFont( self.fieldFont )
        
        # apps logos image list
        self.logosImages = {}
        self.listIcons = wx.ImageList(16, 16)
        self.imageListCreated = False
        
        # list control with packages after installation status
        self.listCtrl = AutoWidthListCtrl(self, -1,
                                     style=wx.LC_REPORT 
                                     #| wx.BORDER_SUNKEN
                                     #| wx.BORDER_NONE
                                     #| wx.LC_EDIT_LABELS
                                     #| wx.LC_SORT_ASCENDING
                                     #| wx.LC_NO_HEADER
                                     #| wx.LC_VRULES
                                     #| wx.LC_HRULES
                                     | wx.LC_SINGLE_SEL
                                     )
        self.listCtrl.SetMinSize( (300,130) )
        self.listCtrl.SetImageList(self.listIcons, wx.IMAGE_LIST_SMALL)

        
        # inserting new columns
        info = wx.ListItem()
        info.m_mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
        info.m_image = -1
        info.m_format = wx.LIST_FORMAT_CENTER
        info.m_text = "Your selection"
        self.listCtrl.InsertColumnInfo(0, info)
        self.listCtrl.SetColumnWidth(0, 110)
        
        # password 
        passwordExplanation = wx.StaticText(self, -1, 'In order to install software, we need your password :')
        passwordExplanation.SetFont( self.fieldFont )
        passwordFieldId = wx.NewId()
        self.password = wx.TextCtrl(self, passwordFieldId, "", style=wx.TE_PASSWORD)
        
        #sbox = wx.StaticBox(self, -1)
        #sbsizer = wx.StaticBoxSizer(sbox, wx.VERTICAL)
        self.sizer.Add( passwordExplanation, flag=wx.BOTTOM|wx.ALIGN_CENTER, border=10 )
        self.sizer.Add( self.password, flag=wx.ALIGN_CENTRE|wx.ALL,border=10 )
        self.sizer.Add( self.desc, 0, wx.ALIGN_CENTRE|wx.ALL,10 )
        self.sizer.Add( self.listCtrl, proportion=2, flag=wx.ALIGN_CENTER, border=10 )
        
        #self.sizer.Add( sbsizer, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 3  )
        
        self.password.SetFocus()
        
    def fillSelectionList(self):
        self.packagesCount = 0;
        self.imagesFilesTotalSize = 0;
        
        self.listCtrl.DeleteAllItems()
        for category in self.maclibreWizard.selected.categories:
            for package in category.packages:
                self.addPackageToSelectionList(package)
                self.packagesCount += 1
                self.imagesFilesTotalSize += package.installations[0].file.size
        
        
        distribVersion = self.maclibreWizard.maclibre.configuration.getDefaultConfig().version
            
        labelText = 'download '
                
        if distribVersion == 'offline' or (distribVersion == 'mixed' and package.diskImageLocation == 'offline'):
            labelText = 'copy '
                
        self.desc.SetLabel("Need to " + labelText + tools.byteSizeToReadableSize(self.imagesFilesTotalSize) + " in " + str(self.packagesCount) +" packages.")
    
    def addPackageToSelectionList(self, package):
        index = self.listCtrl.GetItemCount()
        self.listCtrl.InsertImageStringItem(index, package.name, self.logosImages[package.name])
        textFont = wx.Font(12, wx.SWISS, wx.NORMAL, wx.FONTWEIGHT_LIGHT)
        item = self.listCtrl.GetItem(index)
        item.SetFont(textFont)
        self.listCtrl.SetItem(item)
        
    def createImageList(self):
        # image list for list control
        if self.imageListCreated == False:
            # check current working directory for AppsLogos path
            self.pathToAppsLogos = tools.getResourcesPath() + '/AppsLogos/'
            
            # add apps logos to image list
            for category in self.maclibreWizard.distribution.categories:
                for package in category.packages:
                    if package.logoImageFile != '' and os.path.isfile(self.pathToAppsLogos + package.logoImageFile):
                        png = wx.Image(self.pathToAppsLogos + package.logoImageFile , wx.BITMAP_TYPE_ANY)
                        png.Rescale(16,16)
                        self.logosImages[package.name] = self.listIcons.Add(png.ConvertToBitmap())
                        # debug
                        #print 'Added logo image for:' + package.name
                    else:
                        self.logosImages[package.name] = None
            
            self.imageListCreated = True
            	
    def EvtChoice(self,evt):
        print evt.GetString()

    def OnWizPageChanged(self,evt):
        self.password.SetValue('')

    def OnWizPageChanging(self, evt):
        """
        Download the latest package list (maclibre.xml), parse it and the installed.xml file.
        Check if the current version of this installer is sufficient for installing maclibre.
        call GUI_PackageSelection.GUI_PackageChooser.fill()
        """
        #passwordDialog = wx.PasswordEntryDialog(self,"In order to install software, we need your password :")
        #passwordDialog.ShowModal()
        
        pwd = self.password.GetValue()
        
        if evt.GetDirection() == False:
            return
        
        if  pwd == '' and evt.GetDirection() == True:
            md = wx.MessageDialog(self, 'Fill the password box first', caption="Can't continue", style=wx.OK )
            md.ShowModal()
            md.Destroy()
            evt.Veto()
        else :
            self.maclibreWizard.user = User(pwd)
                    
#</GUI_SelectionConfirmationPage>

#<GUI_ProgressionPage>
class GUI_ProgressionPage(GUI_WizardPage):
    """ third page. gives informations on the installation status. use Installer. """

    def __init__(self, MaclibreWizard):
        GUI_WizardPage.__init__( self, MaclibreWizard , 'Installation progress' )
        self.F_OnOff = True

        #Installer object
        self.installer = Installer(self)
        
        #Logo image
        self.logoImage = wx.StaticBitmap(self, size=(48,48))
        self.pathToAppsLogos = tools.getResourcesPath() + '/AppsLogos/'
        
        #Gauge Description
        self.gaugeDesc = wx.StaticText(self, -1,'                                        ', size=(300,13),style=wx.ALIGN_CENTRE)
        self.gaugeDesc.SetFont( self.fieldFont )

        #Gauge
        self.gauge = wx.Gauge( self, -1, size=(300, 15), style=wx.GA_HORIZONTAL|wx.GA_SMOOTH )
        
        #smallest description
        self.smallDesc = wx.StaticText(self, -1,'                                        ', size=(300,13),style=wx.ALIGN_CENTRE)
        self.smallDesc.SetFont( self.fieldFont )

        #StaticBox 
        sbox = wx.StaticBox(self, -1,label=' ')
        sbsizer = wx.StaticBoxSizer(sbox, wx.VERTICAL)
        sbsizer.Add( self.logoImage, 0, wx.ALIGN_CENTRE|wx.BOTTOM, 10 )
        sbsizer.Add( self.gaugeDesc, 0, wx.ALIGN_CENTRE|wx.ALL, 0 )
        sbsizer.Add( self.gauge )
        sbsizer.Add( self.smallDesc, 0, wx.ALIGN_CENTRE|wx.ALL, 0 )

        
        self.sizer.Add( sbsizer, flag=wx.ALIGN_CENTER_HORIZONTAL|wx.TOP, border=0 )

        # overall progress bar with description
        
        #Gauge
        self.overallGauge = wx.Gauge( self, -1, size=(300, 25), style=wx.GA_HORIZONTAL|wx.GA_SMOOTH )

        #Gauge Description
        self.overallGaugeDesc = wx.StaticText(self, -1,'Overall progress', style=wx.ALIGN_CENTRE)
        self.overallGaugeDesc.SetFont( self.fieldFont )
        
        #smallest description
        self.overallSmallDesc = wx.StaticText(self, -1,'0 %',size=(300,10), style=wx.ALIGN_CENTRE)
        self.overallSmallDesc.SetFont( self.fieldFont )
        
        overallSbox = wx.StaticBox(self, -1,label=' ')
        overallSbsizer = wx.StaticBoxSizer(overallSbox, wx.VERTICAL)
        overallSbsizer.Add( self.overallGaugeDesc, 2, wx.ALIGN_CENTRE|wx.ALL, 5 )
        overallSbsizer.Add( self.overallGauge )
        overallSbsizer.Add( self.overallSmallDesc, 1, wx.ALIGN_CENTRE|wx.ALL, 1 )

        
        self.sizer.Add( overallSbsizer,flag=wx.ALIGN_CENTER_HORIZONTAL|wx.TOP, border=0 )
        
        #overwriting components
        self.yesBttn = wx.Button( self, wx.ID_YES )
        self.noBttn = wx.Button( self, wx.ID_NO )
        self.overwriteDesc = wx.StaticText(self, -1,'                                                                                      ',style=wx.ALIGN_CENTRE)
        self.overwriteDesc.SetFont( self.fieldFont )
        self.yesBttn.SetFont( self.fieldFont )
        self.noBttn.SetFont( self.fieldFont )

        self.Bind(wx.EVT_BUTTON, self.OnClickYes, self.yesBttn)
        self.Bind(wx.EVT_BUTTON, self.OnClickNo, self.noBttn)
        
        self.overwriteSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.overwriteSizer.Add( self.yesBttn , flag=wx.ALL, border=3 )
        self.overwriteSizer.Add( self.noBttn  , flag=wx.ALL, border=3 )

        self.sizer.Add(self.overwriteDesc, flag=wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, border=5 )
        self.sizer.Add(self.overwriteSizer,flag=wx.ALIGN_CENTER_HORIZONTAL|wx.TOP, border=5 )
    
    def showAppLogoImage(self, package):
        if package.logoImageFile != '' and os.path.isfile(self.pathToAppsLogos + package.logoImageFile):
            self.logoImage.Show(True)
            png = wx.Image(self.pathToAppsLogos + package.logoImageFile , wx.BITMAP_TYPE_ANY)
            png.Rescale(48,48)
            self.logoImage.SetBitmap(png.ConvertToBitmap())
            print 'Showing image of: ' + package.name
        else:
            self.logoImage.Show(False)
        self.logoImage.Refresh()

    
    def enableAppLogoImage(self, value):
        self.logoImage.Show(value)
        
    def ForwardOnOff(self):
	""" the forward button becomes clickable or unclickable according to his current state  """
	if self.F_OnOff:
	    self.GetParent().DisableButton(wx.ID_FORWARD)
	else:
	    self.GetParent().EnableButton(wx.ID_FORWARD)
	self.F_OnOff = not self.F_OnOff
	
    def OnWizPageChanged(self,evt):
	# block <back> and <next> buttons during installation.
	self.GetParent().DisableButton(wx.ID_BACKWARD)
	if self.F_OnOff:
	    self.ForwardOnOff()
	self.overwriteSizer.ShowItems(False)
	self.installer.install()

    def OnWizCancel(self,evt):
	import threading
	for runningThreads in threading.enumerate():
	    if not isinstance(runningThreads,threading._MainThread):
		runningThreads._Thread__stop()
	sys.exit(1)
	
    def OnClickYes(self,evt):
        self.__OnClick(True)

    def OnClickNo(self,evt):
        self.__OnClick(False)

    def __OnClick(self,overwriteValue):
        self.overwriteSizer.ShowItems(False)
        self.overwriteDesc.SetLabel(' ')
        self.installer.installationStatus[self.lastAppName]['overwriteValue'] = overwriteValue
        self.installer.installerProgressThread.join()
        self.installer.installerProgressThread = InstallerProgressThread(self.installer)
        self.installer.installerProgressThread.start()

    def Overwrite(self,appName):
        self.overwriteSizer.ShowItems(True)
        self.overwriteDesc.SetLabel(appName+' which has not been installed by MacLibre\n is already in the Applications folder, overwrite ?')
        self.lastAppName = self.installer.currentPkg.name
        self.installer.installationStatus[self.lastAppName]['overwrite'] = True
	
#</GUI_ProgressionPage>

#<GUI_FinishedPage>
class GUI_FinishedPage(GUI_WizardPage):
    """ last page, show a list of non installed package if  """

    def __init__(self, MaclibreWizard):
        GUI_WizardPage.__init__( self, MaclibreWizard , 'Summary' )
        
        # checkbox
        self.checkBox = wx.CheckBox(self,-1, 'Delete cached files on exit.')
        self.checkBox.SetFont(  self.labelFont  )
        self.checkBox.SetValue(True)
        self.sizer.Add( self.checkBox, proportion=1, flag=wx.ALIGN_CENTER, border=3 )

        # image list for list control
        self.successIconPath = tools.getResourcesPath() + '/success-small.png'
        self.failureIconPath = tools.getResourcesPath() + '/failure-small.png'
        
        self.listIcons = wx.ImageList(16, 16)

        self.failureIcon = self.listIcons.Add(wx.Image(self.failureIconPath , wx.BITMAP_TYPE_ANY).ConvertToBitmap())
        self.successIcon = self.listIcons.Add(wx.Image(self.successIconPath , wx.BITMAP_TYPE_ANY).ConvertToBitmap())
        
        # list control with packages after installation status
        self.listCtrl = AutoWidthListCtrl(self, -1,
                                     style=wx.LC_REPORT 
                                     #| wx.BORDER_SUNKEN
                                     #| wx.BORDER_NONE
                                     #| wx.LC_EDIT_LABELS
                                     #| wx.LC_SORT_ASCENDING
                                     #| wx.LC_NO_HEADER
                                     #| wx.LC_VRULES
                                     #| wx.LC_HRULES
                                     | wx.LC_SINGLE_SEL
                                     )
        self.listCtrl.SetMinSize( (400,200) )
        self.sizer.Add( self.listCtrl, proportion=3, flag=wx.ALIGN_CENTER, border=10 )
        self.listCtrl.SetImageList(self.listIcons, wx.IMAGE_LIST_SMALL)
        
        # inserting new columns
        info = wx.ListItem()
        info.m_mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
        info.m_image = -1
        info.m_format = 0
        info.m_text = "Application"
        self.listCtrl.InsertColumnInfo(0, info)
        
        self.listCtrl.InsertColumn(1, "Comment")
        self.listCtrl.SetColumnWidth(0, 130)
        self.listCtrl.SetColumnWidth(1, 270)

    def OnWizPageChanging(self,evt):
	# delete files on exit
	if evt.GetDirection():
	    if self.checkBox.GetValue():
		import shutil
		shutil.rmtree( self.maclibreWizard.maclibre.maclibrePackagesDir )

    def OnWizPageChanged(self,evt):
        # disable backward for last page
        self.GetParent().DisableButton( wx.ID_BACKWARD )

        messageInstalled = 'The following packages have been installed correctly : \n'
        cantBeInstalledFound = False
        listOfPackages = ''
        for category in self.maclibreWizard.selected.categories:
            for package in category.packages:
                for [pkg,reason] in self.cantBeInstalled:
                    if pkg.name == package.name:
                        cantBeInstalledFound = True
                        break
                if cantBeInstalledFound == False:
                    self.addToStatusList(package.name, True, 'Successful installation')
                    listOfPackages += package.name +'\n'
                else:
                    cantBeInstalledFound = False
        
        # time for bad news : which package haven't been installed and why
        str = ''
        if len(self.cantBeInstalled) > 0:
            str="The following packages haven't been installed : \n"
            for [pkg,reason] in self.cantBeInstalled:
                self.addToStatusList(pkg.name, False, self.reasonsDict[reason])
                str+=pkg.name+' : '+self.reasonsDict[reason]+'\n'

        #debug
        print
        print messageInstalled + listOfPackages + str
        print
        
    def addToStatusList(self, packageName, installationStatus, comment):
        """This method adds after installation status of the apps to list control."""
        index = self.listCtrl.GetItemCount()
        # successful or failure icon and color
        if installationStatus:
            index = self.listCtrl.InsertImageStringItem(index, packageName, self.successIcon)
            textColor = wx.BLACK
        else:
            index = self.listCtrl.InsertImageStringItem(index, packageName, self.failureIcon)
            textColor = wx.RED
        
        self.listCtrl.SetStringItem(index, 1, comment)
        item = self.listCtrl.GetItem(index)
        item.SetTextColour(textColor)
        self.listCtrl.SetItem(item)
        
#</GUI_FinishedPage>

class AutoWidthListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    def __init__(self, parent, ID, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        listmix.ListCtrlAutoWidthMixin.__init__(self)

#<GUI_>

#<main>
if __name__ == "__main__": 
    print GUI_MaclibreWizard.__doc__    
#</main>
