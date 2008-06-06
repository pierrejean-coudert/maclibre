import os
import commands
import codecs
import tempfile

#<User>
class User:
    """ This class provide and store informations about user """

    sudoPath = '/usr/bin/sudo '

    def __init__(self,password):
        self.canUseSudoCmd = None
        self.password = password

    def invalidateSudoSession(self):
        cmdUnvalidate = User.sudoPath + ' -K'
        commands.getoutput(cmdUnvalidate)
	
    def useSudo(self,command,outputFile=''):
        # password in stdin
        
        (fd, pwdpath) = tempfile.mkstemp()
        pwdfile = codecs.open(pwdpath,'w','utf-8')
        pwdfile.write(self.password)
        pwdfile.close()

        # launch sudo
        sudoCmd = User.sudoPath + ' -S '+command+' < '+ pwdpath
        if outputFile != '':  sudoCmd += ' > ' + outputFile
        (status, result) = commands.getstatusoutput(sudoCmd)

        os.remove(pwdpath) # remove password file
        self.invalidateSudoSession()

        return (status, result)
	
    def canUseSudo(self):
        """ This method return a boolean equal to True if user can use the command sudo or else False. User's password 
        must have been set."""

        if self.canUseSudoCmd is not None : return self.canUseSudoCmd

        # unvalidate previous session, if any :
        self.invalidateSudoSession()

        # using sudo is allowed :
        (status, result) = self.useSudo(' -l ')
        if status == 0 and '(ALL) ALL' in result: self.canUseSudoCmd = True
        else: self.canUseSudoCmd = False
        
        return self.canUseSudoCmd
#</User>

#<main>
if __name__ == "__main__":
    print User.__doc__
#</main>
