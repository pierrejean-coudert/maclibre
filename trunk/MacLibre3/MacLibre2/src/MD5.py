
import string
import sys
import md5 as md5_module
import os.path

class MD5:
    """ This class provide a way to calculate and check a file's md5 """

    def __init__(self, file, md5Given=None ):
	"""
	file : the file you want to work on
	md5Given : optional. If you want to use isCorrect() you need to specify it
	"""
	self.file = file
	self.md5Given = md5Given
	self.hexStr = string.hexdigits

    def isCorrect(self):
	""" This method return True if the md5 calculated from the file and the given md5 are egals, otherwise False """
	if not os.path.exists(self.file) or self.md5Given is None: return False
	return self.md5Given == self.calculate()

    def calculate(self):
	""" This method return a string representing the md5 sum of the file """
	m = md5_module.new()
	f = open(self.file, 'r')
	for line in f.readlines():
	    m.update(line)
	f.close()
	return self.__hexify( m.digest() )
	
    def __hexify(self,str):
	r = ''
	for ch in str:
	    i = ord(ch)
	    r = r + self.hexStr[(i >> 4) & 0xF] + self.hexStr[i & 0xF]
	return r

if __name__ == '__main__':
    print MD5.__doc__
