__author__ = "Sunil Kumar (kumar.sunil.p@gmail.com)"
__copyright__ = "Copyright 2014, Washington University in St. Louis"
__credits__ = ["Sunil Kumar", "Steve Pieper", "Dan Marcus"]
__license__ = "XNAT Software License Agreement " + \
              "(see: http://xnat.org/about/license.php)"
__version__ = "2.1.1"
__maintainer__ = "Rick Herrick"
__email__ = "herrickr@mir.wustl.edu"
__status__ = "Production"


from XnatSlicerGlobals import *
from XnatSlicerUtils import *
from __main__ import vtk, ctk, qt, slicer

import datetime, time
import os
import sys



comment = """
There are two classes in this file:
XnatSessionArgs and SessionManager.s
  
XnatSessionArgs inherits the 'dict' type provided by python.  
The user cannot insert keys into this object. It is used for 
tracking XNAT-specifc data on a per-scene basis. Data being tracked 
includes: host, username, saveLevel, fileName, session start, etc.

TODO : 
"""



class XnatSessionArgs(dict):
    """ Inherits the 'dict' type of python.  Specifically tailored
        for XNAT tracking.  Keys are immutable, so the user cannot 
        add further keys.
    """
    
    def __init__(self, MODULE, srcPath = None, useDefaultXnatSaveLevel = True):
        """ Establish the relevant keys in the Session Manager.
        """

        self.MODULE = MODULE
        self.inserting = True 
        self['host'] = None
        self['username'] = None
        self['saveLevel'] = None
        self['saveUri'] = None
        self['otherDirs'] = None
        self['fileName'] = None 
        self['sessionStart'] = str(datetime.datetime.now())
        self["sessionType"] = None
        self["XnatIo"] = None
        self["metadata"] = None
        self.inserting = False
   
        if srcPath:
            self.makeSessionArgs_byPath(srcPath)
            
        dict.__init__(self) 



        
    def __setitem__(self, key, value):
        """ Assigns a value to a key.  User cannot add keys to object. 
        """
        if (key not in self) and (not self.inserting):
             raise KeyError("XnatSessionArgs is immutable -- you can't insert keys.")
        dict.__setitem__(self, key, value)



        
    def makeSessionArgs_byPath(self, filePath):
        """ 
        Consructs a number of the session values
        by one argument, 'filePath'.
        """
        saveLevelDir, slicerDir = XnatSlicerUtils.getSaveTuple(filePath) 
        self['host'] = self.MODULE.LoginMenu.hostDropdown.currentText
        self['username'] = self.MODULE.LoginMenu.usernameLine.text        
        self['saveLevel'] = saveLevelDir
        self['saveUri'] = slicerDir
        if os.path.basename(os.path.dirname(filePath)) == 'files':
            self["fileName"] = os.path.basename(filePath) 
        else:
            self["fileName"] = os.path.basename(saveLevelDir)           



        
    def printAll(self, prefStr=None):
        """ As stated. For debugging purposes.
        """
        if prefStr: 
            MokaUtils.debug.lf(('%s')%(prefStr))
        for k,v in self.iteritems():
            MokaUtils.debug.lf( "[\'%s\']=\t%s"%(k,v))





            
class SessionManager(object):
    """ Creates and maintains a 'SessionLog.txt' file 
        for writing XNATSession args to disc.
    """

    
    def __init__(self, MODULE):
        """ Init function.
        """
        self.MODULE = MODULE
        self.sessionFileName = os.path.join(XnatSlicerGlobals.LOCAL_URIS['settings'], 'SessionLog.txt')
        self.sessionArgs = None
        self.saveItem = None



        
    def startNewSession(self, sessionArgs):
        """ As stated.  Get's a new session by a new sessionArgs set.
        """
        if not sessionArgs.__class__.__name__ == "XnatSessionArgs":
            raise NameError("You can only use XnatSessionArgs to start a new session.")
        self.sessionArgs = sessionArgs
        self.writeSession()



        
    def clearCurrentSession(self):
        """ As stated.
        """
        ##print(MokaUtils.debug.lf() + "Clearing current session")
        self.sessionArgs = None


        

    def writeSession(self):
        """ Writes the self.sessionArgs dict to file.
        """
        fileLines = []
        for item in self.sessionArgs:
            fileLines.append("%s:\t\t%s\n"%(item, self.sessionArgs[item]))
        
        fileLines.append("\n\n")
        ##print(MokaUtils.debug.lf() + "Session log file: %s"%(self.sessionFileName))
        f = open(self.sessionFileName, 'a')
        f.writelines(fileLines)            
        f.close()
        del fileLines

        
    
