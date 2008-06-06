
from Distribution import *
from xml.dom import minidom
from xml.parsers.expat import ExpatError

#<Parser>
class Parser:
    """ This class parse a maclibre xml. """

    #<init>
    def __init__(self,xmlPath):
	self.xmlPath = xmlPath
	self.distrib = Distribution()
    #</init>

    #<parse>
    def parse(self):
	""" This method parse the xml file and return a Distribution object"""
	try:
	    xml = minidom.parse(self.xmlPath)
	except (IOError, ExpatError):
	    return self.distrib

	xmlDistrib = xml.getElementsByTagName('Distribution')
	
	if len(xmlDistrib) == 0 :
	    return self.distrib
	else:	    
	    xmlDistrib = xmlDistrib[0]
	    
	    #attributes
	    try : self.distrib.name = xmlDistrib.attributes['Name'].value
	    except KeyError: pass
	    try : self.distrib.version = xmlDistrib.attributes['Version'].value
	    except KeyError: pass
	    try : self.distrib.language = xmlDistrib.attributes['Language'].value
	    except KeyError: pass
	    try : self.distrib.installerMinVersion = xmlDistrib.attributes['InstallerMinVersion'].value
	    except KeyError: pass
	    
	    #nodes
	    self.distrib.categories = self.__parseCategories(xmlDistrib.getElementsByTagName('Category'))

	return self.distrib
    #</parse>

    #<parseCategories>
    def __parseCategories(self,categories):
	objCategoryList=[]
	for xmlCategory in categories:
	    objCategory = Category()
	    
	    #attributes
	    try : objCategory.name = xmlCategory.attributes['Name'].value
	    except KeyError: pass
	    
	    #nodes
	    objCategory.packages = self.__parsePackages(xmlCategory.getElementsByTagName('Package'))

	    objCategoryList.append(objCategory)

	return objCategoryList
    #</parseCategories>

    #<parsePackages>
    def __parsePackages(self,packages):
        objPackageList=[]
        for xmlPackage in packages:
            objPackage = Package()

            ##attributes
            try: 
                objPackage.name = xmlPackage.attributes['Name'].value
            except KeyError: pass
            try: 
                objPackage.version = xmlPackage.attributes['Version'].value
            except KeyError: pass
            try:
                if xmlPackage.attributes['Showable'].value.lower() == 'false':  objPackage.showable = False
            except KeyError: pass
            try:
                tmp = xmlPackage.attributes['Status'].value.lower()
                if tmp == 'unstable' or tmp == 'testing' or tmp == 'beta': objPackage.status=tmp
            except KeyError: pass
            
            try:
                diskImageLocation = xmlPackage.attributes['DiskImageLocation'].value.lower()
                if diskImageLocation == 'online' or diskImageLocation == 'offline': 
                    objPackage.diskImageLocation = diskImageLocation
            except KeyError: pass
            ## for saving
            objPackage.xml = xmlPackage.toxml()

            ## nodes
            packageDescNodes = [node for node in xmlPackage.childNodes if node.nodeName == 'Description']
            for node in packageDescNodes :
                ps = node.getElementsByTagName('P') + node.getElementsByTagName('p')
                for p in ps:
                    objPackage.description += p.firstChild.data
            
                homepages = node.getElementsByTagName('Homepage')
                for homepage in homepages:
                    objPackage.homepage = homepage.firstChild.data
            
            # get logo image filename from xml
            for node in xmlPackage.childNodes: 
                if node.nodeName == 'Image' and node.attributes['id'].value.lower() == 'logo':
                    objPackage.logoImageFile = node.firstChild.data
                    #print 'LogoImageFile: ' + objPackage.logoImageFile
            
            objPackage.installations = self.__parseInstallations( xmlPackage.getElementsByTagName('Installation') )
            objPackageList.append(objPackage)
            
        return objPackageList
    #</parsePackages>

    #<parseInstallations>
    def __parseInstallations(self,installations):
	objInstallationList=[]
	for xmlInstallation in installations:
	    objInstallation = Installation()

	    ## attributes
	    try : objInstallation.sizeOnDisk= int(xmlInstallation.attributes['SizeOnDisk'].value)
	    
	    except KeyError: pass
	    except ValueError:pass
	    try : objInstallation.OSMin = xmlInstallation.attributes['OSMin'].value
	    except KeyError: pass
	    try : objInstallation.OSMax = xmlInstallation.attributes['OSMax'].value
	    except KeyError: pass
	    try : objInstallation.version = xmlInstallation.attributes['Version'].value
	    except KeyError: pass

	    
	    ## nodes
	    objInstallation.file = self.__parseFile(xmlInstallation.getElementsByTagName('File')[0])
	    objInstallation.dependencies = self.__parseDependencies(xmlInstallation.getElementsByTagName('Dependence'))
	    
	    objInstallationList.append(objInstallation)

	return objInstallationList
    #</parseInstallations>

    #<parseFile>
    def __parseFile(self,xmlFile):
        objFile = File()
        
        ## attributes	
        try: 
            objFile.name= xmlFile.attributes['Name'].value
        except KeyError: pass
        try:
            objFile.size= int(xmlFile.attributes['Size'].value)	    
        except KeyError: pass
        except ValueError:pass
        try: 
            objFile.md5 = xmlFile.attributes['MD5Sum'].value
        except KeyError: pass
        try: 
            objFile.type = xmlFile.attributes['Type'].value
        except KeyError: pass
        try: 
            objFile.extension = xmlFile.attributes['Extension'].value
        except KeyError: pass

        ## nodes
        urlNodes = [node for node in xmlFile.childNodes if node.nodeName == 'Url']
        urls = []
        for node in urlNodes :
            urls.append(node.firstChild.data)
        objFile.urls = urls

        return objFile
    #</parseFile>

    #<parseDependencies>
    def __parseDependencies(self,dependencies):
        objDependenceList=[]
        for xmlDependence in dependencies:
            objDependence = Dependence()

            ## attributes	
            try : objDependence.name= xmlDependence.attributes['Name'].value
            except KeyError: pass
            try : objDependence.version = xmlDependence.attributes['Version'].value
            except KeyError: pass
            try : objDependence.install = xmlDependence.attributes['Install'].value
            except KeyError: pass

            objDependenceList.append(objDependence)

        return objDependenceList
    #</parseDependencies>

#</Parser>

#<main>
if __name__ == "__main__":
    #print Parser.__doc__

    parser = Parser('maclibre.xml')
    maclibre = parser.parse()

    for category in maclibre.categories:
        print 'CATEGORY:'
        print '\t' + category.name
        print '\t' + category.description
        print '\t' + str(category.packages)
        for package in category.packages:
            print '\t' + '\t' + 'PACKAGE:'
            print '\t' + '\t' + package.name
            print '\t' + '\t' + package.version
            print '\t' + '\t' + str(package.showable)
            print '\t' + '\t' + package.status
            print '\t' + '\t' + package.homepage   
            for installation in package.installations:
                print '\t' + '\t' + '\t' +  'INSTALLATION'
                print '\t' + '\t' + '\t' +  str(installation.sizeOnDisk)
                print '\t' + '\t' + '\t' +  installation.OSMin
                print '\t' + '\t' + '\t' +  installation.OSMax
                print '\t' + '\t' + '\t' + '\t' +  'FILE'
                print '\t' + '\t' + '\t' + '\t' +  installation.file.name
                print '\t' + '\t' + '\t' + '\t' +  str(installation.file.size)
                print '\t' + '\t' + '\t' + '\t' +  installation.file.md5
                print '\t' + '\t' + '\t' + '\t' +  installation.file.type
                print '\t' + '\t' + '\t' + '\t' +  installation.file.extension
                print '\t' + '\t' + '\t' + '\t' +  str(installation.file.urls)
                for dependence in installation.dependencies:
                    print '\t' + '\t' + '\t' + '\t' +  'DEPENDENCE'
                    print '\t' + '\t' + '\t' + '\t' +  dependence.name
                    print '\t' + '\t' + '\t' + '\t' +  dependence.version
                    print '\t' + '\t' + '\t' + '\t' +  dependence.install
                    print '\t' + '\t' + '\t' + '\t' +  dependence.priority
#</main>
