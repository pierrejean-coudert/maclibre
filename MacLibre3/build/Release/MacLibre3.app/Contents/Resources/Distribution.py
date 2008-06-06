
#<Distribution>
class Distribution:
    """ This class store parsed informations about the maclibre distribution. It can be compared to another distribution (use the version field). """

    def __init__(self,name='MacLibre',version='',language='',installerMinVersion='0.1',categories=[]):
	self.name = name                                  # name of the distribution
	self.version = version                            # version of the distribution
	self.language = language                          # language of the distribution : http://geotags.com/iso3166/countries.html
	self.installerMinVersion = installerMinVersion    # minimum version of the installer for installing this distribution
	self.categories = categories                      # list of Category Object

    def __eq__(self,other):
	if self.name==other.name and self.version==other.version and self.language==other.language:
	    return True
	else : 
	    return False

    def __ne__(self,other):
	return not self.__eq__(other)

    def __lt__(self,other):
	return self.version <  other.version
    def __le__(self,other):
	return self.version <= other.version
    def __gt__(self,other):
	return self.version >  other.version
    def __ge__(self,other):
	return self.version >= other.version


#</Distribution>

#<Category>
class Category:
    """ This class store parsed informations about category in the maclibre distribution  """

    def __init__(self,name='',packages=[]):
	self.name = name          # name of the category
	self.packages = packages  # list of Package object
    
    def __eq__(self,other):
	if self.name==other.name: return True
	else : return False

#</Category>

#<Package>
class Package:
    """ This class store parsed informations about packages in the maclibre distribution. It can be compared to another package (use the version field). """

    def __init__(self,name='',version='',showable=True,status='stable',description='',homepage='',xml='',installations=[],logoFile=''):
        self.name = name                      # name of the package
        self.version = version                # version of the package
        self.showable = showable              # the package could be shown in the tree
        self.status = status                  # status of the package, stable/unstable/testing
        self.diskImageLocation = 'online'     # disk image location, online - internet / offline - in MacLibre offline distribution
        self.description = description        # description of the package
        self.logoImageFile = logoFile         # logo image file of the package
        self.homepage = homepage              # homepage of the package
        self.xml = xml                        # xml corresponding to the package, useful for writing installed.xml.
        self.installations = installations    # list of Installation object
        self.todo = ''                        # what to do with this package. '' or 'INSTALL' or 'UPDATE' or 'REINSTALL'

    def __eq__(self,other):
	if self.name==other.name and self.version==other.version:
	    return True
	else : 
	    return False

    def __ne__(self,other):
	return not self.__eq__(other)

    def __lt__(self,other):
	return self.version <  other.version
    def __le__(self,other):
	return self.version <= other.version
    def __gt__(self,other):
	return self.version >  other.version
    def __ge__(self,other):
	return self.version >= other.version

    def hasDependencies(self):
	""" This method return True if this package has dependencies, else False """
	for installation in self.installations:
	    for dependence in installation.dependencies:
		return True
	return False

    def getDependencies(self,distribution,order=False):
	""" This method return a list of package corresponding to the dependencies of this packages, it looks in distribution parameter.
	If the last and optional argument is True this method return a tuple with the previous list as first element and as second element, a list of string
	corresponding to the install field of Dependence object."""
	if order:
	    install = []

	dependencies = []
	# that's a lot of for ! a better way to do this ?
	for installation in self.installations:
	    for dependence in installation.dependencies:
		for category in distribution.categories:
		    for package in category.packages :
			if dependence ==  package:
			    dependencies.append( package )			    
			    if order:
				install.append( dependence.install)

	if order : return ( dependencies, install )
	else:      return dependencies

#</Package>

#<Installation>
class Installation:
    """ This class store parsed informations about the Installation anchor in the maclibre distribution """

    def __init__(self,sizeOnDisk=0,OSMin='10.0',OSMax='10.4.7',file='',dependencies=[],version=''):
	self.sizeOnDisk = sizeOnDisk       # size on disk when installed
	self.OSMin = OSMin                 # minimal version of OSX for installing this package (included)
	self.OSMax = OSMax                 # maximal version of OSX for installing this package (included)
	self.file = file                   # list of File object
	self.dependencies = dependencies   # list of Dependence object
	self.version = version             # if a package has many installations with different versions.
#</Installation>

#<File>
class File:
    """ This class store parsed informations about the File anchor in the maclibre distribution """

    def __init__(self,name="",size=0,md5='',type='dmg',extension='app',urls=[]):
	self.name = name                # name of the file
	self.size = size                # size of the file
	self.md5 = md5                  # md5 of the file
	self.type = type                # type of the file. 'dmg' or 'zip'
	self.extension = extension      # extension of the program inside. 'pkg' or 'app'
	self.urls = urls                # list of url strings
#</File>

#<Dependence>
class Dependence:
    """ This class store parsed informations about the Dependence anchor in the maclibre distribution """

    def __init__(self,name='',version='',install=''):
	self.name = name          # name of the dependence ( same as the package it refers to )
	self.version = version    # version of the dependence ( same as the package it refers to )
	self.install = install    # when this dependence should be installed. 'after' or 'before' the package
#</Dependence>

#<main>
if __name__ == '__main__':
    print 'Distribution : '+ Distribution.__doc__
    print 'Category : '+ Category.__doc__
    print 'Package : '+ Package.__doc__
    print 'Installation : '+ Installation.__doc__
    print 'File : '+ File.__doc__
    print 'Dependence : '+ Dependence.__doc__    
#</main>
