from xml.dom import minidom
from xml.parsers.expat import ExpatError
from tools import getResourcesPath

#<Config>
class Config:
    """ This class store parsed informations about the distribution config."""
    def __init__(self,name='MacLibre',version='', versionNumber='',language='', url=''):
        self.name = name                                  # config name
        self.version = version                            # version of config (online/offline/mixed)
        self.versionNumber = versionNumber                # version number of config
        self.language = language                          # config language
        self.url = url                                    # distribution file url

    def __eq__(self,other):
        if self.name==other.name and self.version==other.version and self.language==other.language and self.versionNumber==other.versionNumber :
            return True
        else: 
            return False

    def printInfo(self):
        print '\nConfig:\n---------'
        print 'Name: ' + self.name
        print 'Version: ' + self.version
        print 'VersionNumber: ' + self.versionNumber
        print 'Language: ' + self.language
        print 'Url: ' + self.url
        print

    def makeDict(self):
        return {"name":self.name, "version":self.version, "versionNumber":self.versionNumber, "language":self.language, "url":self.url}

#</Config>

#<Configuration>
class Configuration:
    """ This class store parsed informations about available configs in configuration file of MacLibre (config.xml)."""
    def __init__(self,xmlConfigPath='config.xml'):
        self.xmlConfigPath = xmlConfigPath              # path to config xml file
        self.version = ''                               # configuration version
        self.defaultConfig = ''                         # default config name
        self.configs = []                               # list of configs
        self.parse()
    
    #<parse>
    def parse(self):
        """ This method parse the xml config file"""
        try:
            xml = minidom.parse(self.xmlConfigPath)
        except (IOError, ExpatError):
            return False
	
        xmlConfiguration = xml.getElementsByTagName('Configuration')
        
        if len(xmlConfiguration) == 0 :
            return False
        else:	    
            xmlConfiguration = xmlConfiguration[0]
            
            #attributes
            try : self.version = xmlConfiguration.attributes['Version'].value
            except KeyError: pass
            try : self.defaultConfig = xmlConfiguration.attributes['DefaultConfig'].value
            except KeyError: pass
            
            self.__parseConfigs(xmlConfiguration.getElementsByTagName('Config'))

        return True
    #</parse>

    #<parseConfigs>
    def __parseConfigs(self,configs):
        self.configs = []
        
        for xmlConfig in configs:
	    
            objConfig = Config()
            
            #attributes
            try :  objConfig.name = xmlConfig.attributes['Name'].value
            except KeyError: pass
            
            versionNodes = xmlConfig.getElementsByTagName('Version')
            for versionNode in versionNodes:
                tmpVersion = versionNode.firstChild.data
                
                if tmpVersion == 'online' or tmpVersion == 'offline' or tmpVersion == 'mixed': 
                    objConfig.version = tmpVersion
            
            versionNumberNodes = xmlConfig.getElementsByTagName('VersionNumber')
            for versionNumberNode in versionNumberNodes:
                objConfig.versionNumber = versionNumberNode.firstChild.data

            languageNodes = xmlConfig.getElementsByTagName('Language')
            for languageNode in languageNodes:
                objConfig.language = languageNode.firstChild.data

            urlNodes = xmlConfig.getElementsByTagName('Url')
            for urlNode in urlNodes:
                objConfig.url = self.__getUrl(urlNode.firstChild.data)

            self.configs.append(objConfig)

        return True
        
    #</parseConfigs>
    
    
    #<getUrl>
    def __getUrl(self, url):
        import re
        isUrlLocalFile = re.search('^file://', url)
        if isUrlLocalFile:
                filename = re.sub('file://','',url)
                path = getResourcesPath() 
                if path == '../bin':
                    url = '../xml/' + filename
                else:
                    url = path + '/xml/' + filename
                return url
        else:
            return url
    #</getUrl>
    
    #<getDefaultConfig>
    def getDefaultConfig(self):
        if self.defaultConfig == '':
            return self.configs[0]
        else:
            for config in self.configs:
                if config.name == self.defaultConfig:
                    return config
            return self.configs[0]
    #</getDefaultConfig>

#</Configuration>


#<main>
if __name__ == '__main__':
    print 'Configuration : '+ Configuration.__doc__
    print 'Config : '+ Config.__doc__
#</main>
