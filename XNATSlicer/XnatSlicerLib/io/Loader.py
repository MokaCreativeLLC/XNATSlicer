# python
import os
import sys
import shutil

# application
from __main__ import qt, slicer

# external
from MokaUtils import *

# module
from XnatSlicerGlobals import *
from XnatSlicerUtils import *
from FileInfo import *
from SessionManager import *




class Loader(object):
    """ 
    Loader is the parent class to the various Loader classes.
    """

        
    def __init__(self, MODULE, _src, fileUris = None):
        """ 
        """
        self.MODULE = MODULE
        self._src = _src
        self._dst = ''
        self.fileUris = fileUris
        self._dstBase = XnatSlicerGlobals.LOCAL_URIS['downloads']
        self.useCached = None


        
    def runCacheCheckWorkflow(self):
        """
        """
        useCachedSettingList = self.MODULE.SettingsFile.getSetting(self.MODULE.LoginMenu.hostDropdown.currentText, 
                                                                   self.MODULE.CacheSettings.USE_CACHED_IMAGES_TAG)
        #print "USE CACHED SETTING", useCachedSettingList
        useCachedSetting = True if (len(useCachedSettingList) > 0 and 'True' in useCachedSettingList[0]) else False

        self.useCached = self.checkCache(self.fileUris) and useCachedSetting        
        

    def setZipSrcDst(self):   
        """
        """ 
        self._src = self._src + "?format=zip"
        self._dst = os.path.join(self._dstBase , 'projects' + 
                                 self._src.replace('?format=zip', '').split('projects')[1].split('/files')[0] + '/files.zip')
        #print "SRC:", self._src
        #print "DST:", self._dst


        
    def setFileSrcDst(self):
        """
        """
        self._dst = os.path.join(self._dstBase , 'projects' + self._src.split('projects')[1])
    


        
    @property
    def loadArgs(self):
        return {'src': self._src, 'dst': self._dst}



    def load(self):
        """
        """
        #--------------------    
        # If the zipfile does not exist, then exit.
        # (This is the result of the Cancel button in 
        # the download modal being clicked.) 
        #--------------------
        if not os.path.exists(self._dst):
            #print "%s exiting workflow..."%(self._src)  
            return False
        return True

        

    def extractDst(self):
        """
        """
        #--------------------
        # UNZIP THE FILE SET
        #--------------------       
        self.extractPath = self._dst.split(".")[0]
        
        #
        # Remove existing zipfile extract path if it exists
        #
        if os.path.exists(self.extractPath): 
            shutil.rmtree(self.extractPath)

        #
        # Decompress zips.
        #
        # return if self._dst == None (result of a cancel)
        if not os.path.exists(self._dst):
            return
        MokaUtils.file.decompress(self._dst, self.extractPath)

        #
        # Add to files in the decompressed destination 
        # to downloadedDicoms list.
        #
        #print "%s Inventorying downloaded files..."%(MokaUtils.debug.lf())  
        self.extractedFiles = []
        for root, dirs, files in os.walk(self.extractPath):
            for relFileName in files:          
                self.extractedFiles.append(MokaUtils.path.adjustPathSlashes(os.path.join(root, relFileName)))


        #
        # Move downloaded files to extactly 'self._dst'
        #
        newExtractFiles = []
        for fileName in self.extractedFiles:
            newExtractFile = self._dst.split('.zip')[0] + '/' + os.path.basename(fileName)
            shutil.move(fileName, newExtractFile)
            newExtractFiles.append(newExtractFile)
        self.extractedFiles = newExtractFiles
