
import zipfile
import os

from PgmRetriever import PgmRetriever

#<ZipContainer>
class ZipContainer:
    """ This class provide access/informations to .zip archive """
    
    def __init__(self, filepath):
	self.pathZip = filepath
	self.pathDir = os.path.split(filepath)[0]
	self.retriever = PgmRetriever(self.pathDir)
	self.isExtracted = False
	
    def extract(self):
	""" This method extract a zip file in his current directory """

	if zipfile.is_zipfile(self.pathZip):
	    zf = zipfile.ZipFile(self.pathZip)
	    for file in zf.namelist():
		newPath = os.path.join(self.pathDir,file)
		if not os.path.exists(newPath):
		    if not file.endswith('/'):
			newFile = open(newPath, 'wb')
			newFile.write(zf.read(file))
			newFile.flush()
			newFile.close()
			if 'MacOS' in os.path.split(newPath)[0]:
			    os.chmod(newPath,0755)
		    else :
			os.makedirs(newPath)
	    zf.close()
	else:
	    print self.pathZip + " is not a zip file" 
	self.isExtracted = True

    def getDotApp(self):
	""" This method return a list of paths corresponding to the .app directories inside the archive. """
	return self.retriever.retrieveDir('.app')

    def getDotPkg(self):
	""" This method return a list of paths corresponding to the .pkg directories inside the archive. """
	return self.retriever.retrieveDir('.pkg')


#</ZipContainer>

#<main>
if __name__ == "__main__":
    print ZipContainer.__doc__

#</main>
