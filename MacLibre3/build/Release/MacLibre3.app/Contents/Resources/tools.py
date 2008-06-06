

def byteSizeToReadableSize(byteSize):
    
    def onlyTwo(strSize):
	return strSize[:strSize.index('.')+3]
    
    """ This method receive a size in byte and return a string corresponding to the same size but in a more readable format """
    kilobyte=1024.0
    megabyte=1024.0*1024.0
    if byteSize < kilobyte :
	return onlyTwo(str(byteSize)) + ' bytes'
    elif byteSize < megabyte :
	return onlyTwo(str(byteSize/kilobyte)) + ' KB'
    else:
	return onlyTwo(str(byteSize/megabyte)) + ' MB'


def cleanString( string ):
    """ This method cleans a string. ie : delete tabulations, double whitespaces and whitespaces at the beginning."""
    cleanString = ""
    for line in string.splitlines() :
	cleanString += ' '.join( line.split() ) + '\n'
    return cleanString

def getResourcesPath():
    """ This method returns a path to resources."""
    import os
    import re
    usingResources = re.search('\/Contents\/Resources$', os.getcwd() )
    if( usingResources ):
        return os.getcwd()
    else:
        return os.getcwd()+'/MacLibre3.app/Contents/Resources'
