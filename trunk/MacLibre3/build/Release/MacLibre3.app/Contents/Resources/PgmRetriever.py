
import os

#<PgmRetriever>
class PgmRetriever:
    """ This class looks recursively for an extension in a directory  """

    def __init__(self,repository):
	"""repository : the path to the directory you want to look in."""
	self.repository = repository

    def retrieveFile(self,extension):
	""" This method return a list of file paths ended by the extension
	argument extension : the extension you are looking for"""
	pathList = []
	for root, dirnames, filenames in os.walk( self.repository ):
	    for fn in filenames:
		if fn.endswith( extension ):
		    pathList.append( os.path.join( root, fn ) )
	return pathList


    def retrieveDir(self,extension):
	""" This method return a list of directory paths ended by the extension
	argument extension : the extension you are looking for"""
	pathList = []
	for root, dirnames, filenames in os.walk( self.repository ):
	    for dn in dirnames:
		if dn.endswith( extension ) :
		    ## assure that '/Volumes/dmgmounted/bar.app/.../foo.app' don't go in the list
		    ## if '/Volumes/dmgmounted/bar.app' is already in
		    Add = True
		    for elem in pathList:
			if elem in os.path.join(root,dn) :
			    Add = False
		    ## problem with unzip 
		    if '__MACOSX' in os.path.join(root,dn) :
			Add = False
		    if Add : pathList.append( os.path.join(root,dn) )
	return pathList

#</PgmRetriever>

#<main>
if __name__ == "__main__":
    print PgmRetriever.__doc__
#</main>
