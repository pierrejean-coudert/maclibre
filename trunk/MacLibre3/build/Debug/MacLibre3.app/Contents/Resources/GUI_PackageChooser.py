
import wx
import wx.gizmos as gizmos
import wx.lib.hyperlink as hl
import copy
import os

import tools
from Distribution import *

#<TODO>
# activate gimp -> activate X11 : 
#    need to work on setSelectedDistribution and on __Activated
#</TODO>

#<GUI_PackageChooser>
class GUI_PackageChooser(wx.Panel):
    """ This class is a tree containing category and package from maclibre distribution. """

    def __init__(self, parent, descriptionPanel, maclibreWizard):
	
	wx.Panel.__init__(self, parent, -1)
        self.tree = gizmos.TreeListCtrl( self, -1, style=wx.TR_MAC_BUTTONS|wx.TR_FULL_ROW_HIGHLIGHT|wx.TR_HIDE_ROOT)
	self.descriptionPanel = descriptionPanel
	self.maclibreWizard = maclibreWizard
	self.itemFont = wx.Font(10, wx.SWISS, wx.NORMAL, wx.FONTWEIGHT_LIGHT)
	self.itemNotInstallableFont = wx.Font(10, wx.SWISS, wx.ITALIC, wx.FONTWEIGHT_LIGHT)
	self.reason = "" # reason why a package can't be installed
	self.reasonsDict = { 'PKG_SUDO_TEST'     : "You need to be administrator for installing this package",
			     'HOST_TEST'         : "This package can't be installed on your OSX version",
			     'DEPENDENCE_TEST'   : "A dependencie of this package can't be installed"}

	# images
        isz = (16,16)
        il = wx.ImageList(isz[0], isz[1])
        self.fldridx     = il.Add( wx.ArtProvider_GetBitmap(wx.ART_FOLDER,      wx.ART_OTHER, isz) )
	self.fldropenidx = il.Add( wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN,   wx.ART_OTHER, isz) )
	self.fileidx     = il.Add( wx.ArtProvider_GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, isz) )
	self.tree.SetImageList(il)
        self.il = il

        # create some columns
        self.tree.AddColumn("Applications")
        self.tree.AddColumn("Action")
        self.tree.SetMainColumn(0)
        self.root = self.tree.AddRoot("MacLibre")
        self.tree.SetItemImage(self.root, self.fldridx, which = wx.TreeItemIcon_Normal)
        self.tree.SetItemImage(self.root, self.fldropenidx, which = wx.TreeItemIcon_Expanded)
	self.tree.SetColumnWidth(0, 130)
	
       	#bindings
	self.tree.Bind( wx.EVT_TREE_ITEM_ACTIVATED, self.__Activated )
	self.tree.Bind( wx.EVT_TREE_SEL_CHANGED, self.__Selected )
	self.Bind(wx.EVT_SIZE, self.__OnSize)

        self.tree.Expand(self.root)

    def fill(self):
	""" This method fill the tree with categories and packages which could be installed by user """

	if self.tree.ItemHasChildren(self.root):
	    self.tree.DeleteChildren(self.root)

	#cus = self.maclibreWizard.user.canUseSudo()

	for category in self.maclibreWizard.distribution.categories :

	    #add category
            child = self.tree.AppendItem(self.root, category.name)
            self.tree.SetItemText(child, "", 1)
	    self.tree.SetItemFont(child, self.itemFont )
            self.tree.SetItemImage(child, self.fldridx, which = wx.TreeItemIcon_Normal)
            self.tree.SetItemImage(child, self.fldropenidx, which = wx.TreeItemIcon_Expanded)
	    
	    for package in category.packages :
		if  package.showable:
		    if self.__installable(package):
			(previouslyInstalled, superiorVersion) = self.__getPackageCorrespondingInfos(package)
			status = Status(previouslyInstalled,superiorVersion)
			font = self.itemFont
		    else:
			(previouslyInstalled, superiorVersion) = self.__getPackageCorrespondingInfos(package)
			status = Status( previouslyInstalled, superiorVersion, cantBeInstalled=True, why=self.reasonsDict[self.reason] )
			font = self.itemNotInstallableFont

		    #add package
		    item = self.tree.AppendItem(child, package.name)
		    self.tree.SetItemPyData(item, status)
		    self.tree.SetItemText(item, status.getInitialText(), 1)
		    self.tree.SetItemFont(item, font )
		    self.tree.SetItemImage(item, self.fileidx, which = wx.TreeItemIcon_Normal)


	#debug
	print
	print 'tree populated'
	print 

    def setSelectedDistribution(self):
	""" This method fill selected distribution object with user' selection """
	
	self.maclibreWizard.selected = copy.copy( self.maclibreWizard.distribution )
	self.maclibreWizard.selected.categories = []
	self.dependenciesList = []

	(item, cookie) = self.tree.GetFirstChild(self.root)
	for i in range( self.tree.GetChildrenCount(self.root, False) ):

	    category = Category( self.__itemToCategory(item).name )
	    packages = []

	    # retrieve packages
	    (itemChild, cookieChild) = self.tree.GetFirstChild(item)
	    self.__fillPackageSelected(itemChild,packages)
	    for j in range( self.tree.GetChildrenCount(item) -1 ):
		(itemChild, cookieChild) = self.tree.GetNextChild(item,cookieChild)
		self.__fillPackageSelected(itemChild,packages)
	    (item, cookie) = self.tree.GetNextChild(self.root,cookie)
	    
	    #add them
	    if len(packages) > 0 :
		category.packages = packages
		self.maclibreWizard.selected.categories.append( category )
	
	#non showable package
	for dep in self.dependenciesList:
	    if not dep.showable:
		for category in self.maclibreWizard.distribution.categories:
		    if dep in category.packages:
			depCategory = category
			break
		for category in self.maclibreWizard.selected.categories:
		    if depCategory == category:
			category.packages.append(dep)
			
	#debug
	print
	print 'selected distribution : '
	for category in self.maclibreWizard.selected.categories:
	    print 'CATEGORY:',
	    print '\t' + category.name
	    for package in category.packages:
		print '\t' + '\t' + 'PACKAGE:',
		print '\t' + '\t' + package.name,
		print '\t' + '\t' + package.version,
		print '\t' + '\t' + package.todo
		for installation in package.installations:
		    print '\t' + '\t' + '\t' +  'INSTALLATION',
		    print '\t' + '\t' + '\t' +  installation.OSMin,
		    print '\t' + '\t' + '\t' +  installation.OSMax
	print


    def __fillPackageSelected(self,itemChild,packages):
	""" 
	Add package corresponding to the itemChild to packages, and all its dependencies.
	package.todo field is set in this method.
	"""
	todoText = self.tree.GetItemPyData(itemChild).text
	package = copy.deepcopy( self.__itemToPackage(itemChild) )

	if todoText != '' or package in self.dependenciesList:

	    if package.todo == '':
		package.todo = todoText

	    def recursivelyAddDependencies(self,pkg):
		if pkg.hasDependencies():
		    dependenciesList = pkg.getDependencies(self.maclibreWizard.distribution) 
		    for dep in dependenciesList:
			dep.todo = todoText
			recursivelyAddDependencies(self,dep)
			if dep not in self.dependenciesList:
			    self.dependenciesList.append( dep )

	    recursivelyAddDependencies(self,package)
	    if package not in packages:
		packages.append( package )
		

    def __Activated(self, event):
	""" Called when a leaf is activated. ie : double click/enter/space . Expand/Collapse if it's directory, set Action text if 
	it's a package """
	item = event.GetItem()
	if self.tree.ItemHasChildren(item):
	    if self.tree.IsExpanded(item):
		self.tree.Collapse(item)
	    else:
		self.tree.Expand(item)
	else :
	    status = self.tree.GetItemPyData(item)
	    self.tree.SetItemText( item, status.getActivatedText(), 1 )
	    

    def __Selected(self, event):
	""" called when a leaf is selected. If the leaf is a package this method call GUI_PanelDescription.fillWith """
	item = event.GetItem()
	if not self.tree.ItemHasChildren(item):

	    package = self.__itemToPackage(item)
	    self.descriptionPanel.fillWith(package)
	    self.descriptionPanel.warningLabel.SetLabel('')

	    status = self.tree.GetItemPyData(item)
	    if status.cantBeInstalled:
		self.descriptionPanel.warningLabel.SetLabel(status.why)


    def __OnSize(self, event):
        self.tree.SetSize(self.GetSize())

    def __itemToPackage(self,item):
	""" Retrieve a package from a given item """
	name = self.tree.GetItemText(item)
	for category in self.maclibreWizard.distribution.categories :
	    for package in category.packages :
		if package.name == name:
		    return package

    def __itemToCategory(self,item):
	""" Retrieve a category from a given item """
	name = self.tree.GetItemText(item)
	for category in self.maclibreWizard.distribution.categories :
	    if category.name == name:
		return category

    def __installable(self,package):
	""" This method returns True if the given package could/should be added in the tree, otherwise False. Delete unneeded Installations object in 
	Maclibre Distribution """

	installationsToRemove = []
	self.reason = ''

	# is installable : host is ok for this package + .pkg need to use sudo
	hostTest = False
	#pkgTests = True
	for installation in package.installations:
	    if self.maclibreWizard.maclibre.host>=installation.OSMin and self.maclibreWizard.maclibre.host<=installation.OSMax :
		hostTest = True
	    else :  installationsToRemove.append(installation)
	    #if installation.file.extension=='pkg' #and cus==False:
		#pkgTests = False

	#delete un-needed installations object
	for itr in installationsToRemove:
	    package.installations.remove(itr)
	
	if not hostTest: 
	    self.reason = 'HOST_TEST'
	    return False
	#if not pkgTests:
	#    self.reason = 'PKG_SUDO_TEST'
	#    return False
	
	# set Installation version (if exists) to Package version
	if package.version == '' and package.installations[0].version != '':
	    package.version = package.installations[0].version

	# all the same for dependencies
	if package.hasDependencies():
	    dependenciesList = package.getDependencies(self.maclibreWizard.distribution)
	    if len(dependenciesList) == 0:
		return False
	    for dep in dependenciesList :
		if not self.__installable(dep):
		    self.reason = 'DEPENDENCE_TEST'
		    return False

	return True

    def __getPackageCorrespondingInfos(self,packageArg):
	""" This method returns a tuple of boolean. The first is True if the given package or a previous version
	has already been installed, otherwise False. The second is True if this previously installed package is outdated, otherwise False"""
	for category in self.maclibreWizard.installed.categories :
	    for package in category.packages :
		if package.name == packageArg.name:
		    self.__installable(package) # clean package with unneeded Installation, and set Version Field if needed
		    if packageArg.version > package.version:
			return ( True, True )
		    else:
			return ( True, False )
	return ( False, False )

#</GUI_PackageChooser>

#<Status>
class Status:
    """ This class stocks informations about a package and what user want to do with it  """

    def __init__(self,previouslyInstalled,superiorVersion,cantBeInstalled=False, why=""):
	self.text =""
	self.previouslyInstalled=previouslyInstalled
	self.superiorVersion=superiorVersion
	self.initial = True
	self.cantBeInstalled = cantBeInstalled
	self.why = why

    def getInitialText(self):
	if self.initial and not self.cantBeInstalled :
	    self.initial=False
	    if self.previouslyInstalled and self.superiorVersion:
		self.text = "UPDATE"
	    else:
		self.text = ""
	    return self.text
	else :
	    return ''

    def getActivatedText(self):
	if self.cantBeInstalled: return ""

	if not self.previouslyInstalled :
	    if self.text == "":
		self.text = "INSTALL"
	    else:
		self.text = ""
	else:
	    if self.superiorVersion:
		if self.text == "":
		    self.text = "UPDATE"
		else:
		    self.text = ""
	    else:
		if self.text == "":
		    self.text = "REINSTALL"
		else:
		    self.text = ""
	return self.text

#</Status>

#<GUI_PanelDescription>
class GUI_PanelDescription(wx.Panel):
    """ This class is a panel which displays informations about package handled in GUI_PackageChooser. """    

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        self.SetMinSize( (380,270) )
        
        self.fontLabel = wx.Font( 11, wx.SWISS, wx.NORMAL, wx.BOLD   )
        self.fontField = wx.Font( 10, wx.SWISS, wx.NORMAL, wx.NORMAL )
        
        # check current working directory for AppsLogos path
        self.pathToAppsLogos = tools.getResourcesPath() + '/AppsLogos/'
        
        #print 'Path to AppsLogos: ' + self.pathToAppsLogos
        
        # logo image (empty)
        self.logoImage = wx.StaticBitmap(self, -1)
        self.logoImage.SetPosition((230,20))
        self.logoImage.Show(False)

        ## main sizer
        self.sbsizer = wx.StaticBoxSizer( wx.StaticBox(self, -1) , wx.VERTICAL)
        self.SetSizer(self.sbsizer)
            
        ## controls
        # warning label : print package can't be installed
        self.warningLabel = wx.StaticText( self )
        self.warningLabel.SetFont( wx.Font(10, wx.SWISS, wx.ITALIC, wx.FONTWEIGHT_LIGHT) )
        self.warningLabel.SetForegroundColour('RED')
        self.sbsizer.Add( self.warningLabel )

        # name
        nameLabel = self.__buildLabel("Package : ")
        self.nameField = self.__buildField()
        self.nameField.SetFont( wx.Font( 14, wx.SWISS, wx.NORMAL, wx.NORMAL ) )
        nameSizer = self.__buildSizer(nameLabel,self.nameField)

        #version
        versionLabel = self.__buildLabel("Version : ")
        self.versionField = self.__buildField()
        versionSizer = self.__buildSizer(versionLabel,self.versionField)

        #status
        statusLabel = self.__buildLabel("Status : ")
        self.statusField = self.__buildField()
        statusSizer = self.__buildSizer(statusLabel,self.statusField)

        #size on disk
        sizeOfImageFile = self.__buildLabel("Image size : ")
        self.sizeOfImageFile = self.__buildField()
        sizeOfImageFileSizer = self.__buildSizer(sizeOfImageFile,self.sizeOfImageFile)
        
        #size on disk
        sizeOnDiskLabel = self.__buildLabel("Size on disk : ")
        self.sizeOnDiskField = self.__buildField()
        sizeOnDiskSizer = self.__buildSizer(sizeOnDiskLabel,self.sizeOnDiskField)

        #homepage
        homepageLabel = self.__buildLabel("Homepage : ")
        self.homepageField = hl.HyperLinkCtrl(self, wx.ID_ANY)
        self.homepageField.SetFont( self.fontField )
        homepageSizer = self.__buildSizer(homepageLabel,self.homepageField)

        #description
        descriptionLabel = self.__buildLabel("Description : ")
        sizerH = wx.BoxSizer( wx.HORIZONTAL )
        sizerH.Add( descriptionLabel, -1, wx.ALIGN_CENTER|wx.ALL,5)
        self.sbsizer.Add( sizerH )

        self.descriptionField = self.__buildField()
        sizerH2 = wx.BoxSizer( wx.HORIZONTAL )
        sizerH2.Add( self.descriptionField, -1, wx.ALIGN_CENTER)
        self.sbsizer.Add( sizerH2 )
        self.descriptionField.SetLabel('                                                                                                       ')

    def fillWith(self,package):
        """ This method fill the description panel with the informations available for the given package """
        self.nameField.SetLabel(package.name)
        self.versionField.SetLabel(package.version)
        self.statusField.SetLabel(package.status)
        if len(package.installations) > 0:
            self.sizeOnDiskField.SetLabel( tools.byteSizeToReadableSize(package.installations[0].sizeOnDisk) )
            self.sizeOfImageFile.SetLabel( tools.byteSizeToReadableSize(package.installations[0].file.size) )
        else:
            self.sizeOnDiskField.SetLabel( ' ' )
            self.sizeOfImageFile.SetLabel( ' ' )
        self.homepageField.SetLabel( package.homepage )
        self.homepageField.SetURL( package.homepage )
        self.descriptionField.SetLabel( tools.cleanString(package.description) )
        
        # show application logo
        if package.logoImageFile != '' and os.path.isfile(self.pathToAppsLogos + package.logoImageFile):
            png = wx.Image(self.pathToAppsLogos + package.logoImageFile , wx.BITMAP_TYPE_ANY).ConvertToBitmap()
            self.logoImage.SetBitmap(png)
            self.logoImage.Show(True)
        else:
            self.logoImage.Show(False)

    def __buildLabel(self,title):
	""" This method build a label, for instance 'Name :' """
	label = wx.StaticText( self, label=title)
	label.SetFont( self.fontLabel )
	return label

    def __buildField(self):
	""" This method build a field to display informations about the package """
	field = wx.StaticText( self)
	field.SetFont( self.fontField )
	return field

    def __buildSizer(self,label,field):
	""" This method build a sizer which will contain a label and field, then it's added to the panel sizer  """
	sizer = wx.BoxSizer( wx.HORIZONTAL )
	sizer.Add( label, -1, wx.ALIGN_CENTER|wx.ALL,5)
	sizer.Add( field, -1, wx.ALIGN_CENTER|wx.ALL,1)
	self.sbsizer.Add( sizer )
	return sizer

#</GUI_PanelDescription>

#<main>
if __name__ == '__main__':
    print "GUI_PackageChooser : " + GUI_PackageChooser.__doc__
    print "Status : " + Status.__doc__
    print "GUI_PanelDescription : " + GUI_PanelDescription.__doc__
#</main>
