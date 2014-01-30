# python
import os
import shutil

# application
from __main__ import qt, slicer

# external
from Xnat import *
from MokaUtils import *

# module
from XnatSlicerGlobals import *
from XnatSlicerUtils import *
from SessionManager import *





class Loader(object):
    """ 
    Loader is the parent class to the various Loader classes of XNATSlicer.  
    Loaders are responsible for downloading, caching and loading a certain filetype
    from XNAT into Slicer.
    """

        
    def __init__(self, MODULE, _src, fileUris = None):
        """ 
        Init function.

        @param MODULE: The XNATSlicer module.
        @type MODULE: XnatSlicerWidget

        @param _src: The source URI to begin the load from.
        @type _src: str

        @param fileUris: The fileUrs to download from (in case the download is of
           an entire 'files' folder).
        @type fileUris: list(str)
        """
        self.MODULE = MODULE
        self._src = _src
        self._dst = ''
        self.fileUris = fileUris
        self.useCached = None
        self._dstBase = XnatSlicerGlobals.LOCAL_URIS['downloads']
        

        
    @property
    def loadArgs(self):
        return {'src': self._src, 'dst': self._dst}

        

    def extractDst(self):
        """
        Extracts the downloaded zip file and its contents
        to the appropriate dst.
        """
        
        #--------------------
        # UNZIP The FILE SET
        #--------------------       
        self.extractPath = os.path.join(os.path.dirname(self._dst), 'files')
        


        #--------------------
        # Remove existing zipfile extract path if it exists
        #--------------------
        if os.path.exists(self.extractPath): 
            shutil.rmtree(self.extractPath)



        #--------------------
        # Decompress zips.
        #--------------------
        # return if self._dst == None (result of a cancel)
        if not os.path.exists(self._dst):
            return
        MokaUtils.file.decompress(self._dst, self.extractPath)



        #--------------------
        # Add to files in the decompressed destination 
        # to downloadedDicoms list.
        #--------------------
        #print "%s Inventorying downloaded files..."%(MokaUtils.debug.lf())  
        self.extractedFiles = []
        for root, dirs, files in os.walk(self.extractPath):
            for relFileName in files:          
                self.extractedFiles.append(MokaUtils.path.adjustPathSlashes(os.path.join(root, relFileName)))



        #--------------------
        # Move downloaded files to extactly 'self._dst'
        #--------------------
        newExtractFiles = []
        for fileName in self.extractedFiles:
            newExtractFile = self._dst.split('.zip')[0] + '/' + os.path.basename(fileName)
            try:
                #
                # Make the dstDir if it doesn't exist.
                #
                dstDir = os.path.dirname(newExtractFile)
                if not os.path.exists(dstDir):
                    os.makedirs(dstDir)
                #
                # Move the files
                #
                shutil.move(fileName, newExtractFile)
                newExtractFiles.append(newExtractFile)
            except Exception, e:
                print "Warning: Error moving filename '%s' to '%s'.  Error: %s"%(fileName, newExtractFile, str(e))
        self.extractedFiles = newExtractFiles



class Loader_File(Loader):
    """
    A subclass of the Loader class for downlading individual files.
    """

    def __init__(self, MODULE, _src, fileUris = None):
        """
        Init function.

        @param MODULE: The XNATSlicer module.
        @type MODULE: XnatSlicerWidget

        @param _src: The source URI to begin the load from.
        @type _src: str

        @param fileUris: The fileUrs to download from (in case the download is of
           an entire 'files' folder).
        @type fileUris: list(str)
        """
        super(Loader_File, self).__init__(MODULE, _src, fileUris)
        self._dst = os.path.join(self._dstBase , 'projects' + self._src.split('projects')[1])
        


    def load(self):
        """ 
        Generic file load.
        """
        if not os.path.exists(self._dst): return 
        SlicerUtils.loadNodeFromFile(self._dst)





class Loader_Images(Loader):
    """
    A subclass of the Loader class for downlading image sets (DICOM, Analyze, etc.).
    """

    def __init__(self, MODULE, _src, fileUris):
        """
        Init function.

        @param MODULE: The XNATSlicer module.
        @type MODULE: XnatSlicerWidget

        @param _src: The source URI to begin the load from.
        @type _src: str

        @param fileUris: The fileUrs to download from (in case the download is of
           an entire 'files' folder).
        @type fileUris: list(str)
        """
        super(Loader_Images, self).__init__(MODULE, _src, fileUris)

        #--------------------
        # Derive a src and dst
        #--------------------
        self._src, self._dst = Xnat.path.modifySrcDstForZipDownload(self._src, self._dstBase)


        #--------------------
        # Perform cache check
        #--------------------
        self.useCached = self.checkCache(self.fileUris) and self.isUseCacheChecked()
        if self.useCached: 
            self.performUseCacheUpdates()

            
        #--------------------
        # Sync file URIs if necessary
        #--------------------
        for fileUri in self.fileUris:
            if XnatSlicerUtils.isDICOM(fileUri):
                self.syncFileUris()
                return



    def syncFileUris(self):
        """
        Updates the internal variables to have equivalent directory URIs.  
        Usually for DICOM downloads.
        
        @note: The reason this exists is because when querying for file contents
            of a given folder, the XNAT metadata returns a URI that is relative
            to the experiment ID of the files to be downloaded, not the project.
        """
    
        fileDirs = []
        for fileUri in self.fileUris:
            if XnatSlicerUtils.isDICOM(fileUri):
                fileDir = os.path.dirname(fileUri)
                if not fileDir in fileDirs:
                    fileDirs.append(fileDir)

                    
        self._oldSrc = None
        if len(fileDirs) == 1 and self._dst != None:
            self._oldSrc = self._src
            self._oldDst = self._dst
            self._src = self._src.split('/data/')[0] + fileDirs[0] # + '?format=zip'
            self._dst = self._dstBase + fileDirs[0] + '.zip'

            #--------------------
            # Remove any folders that 
            # exist after the 'files' level in self._src
            # We don't need them.
            #--------------------  
            splitter = 'files'
            self._src = self._src.split(splitter)[0] + splitter + '?format=zip'
            
            

        #--------------------
        # Update the download popup
        #--------------------            
        if self.MODULE.Workflow_Load.XnatDownloadPopup and self._oldSrc:
            self.MODULE.Workflow_Load.XnatDownloadPopup.changeRowKey(self._oldSrc.replace('?format=zip', ''), 
                                                                    self._src.replace('?format=zip', ''))




    def isUseCacheChecked(self):
        """
        Queries the XNATSlicer module's SettingsFile to determine if the "use cached images"
        checkbox is checked.

        This method is utilized by image-type loaders (loader_Dicom, loader_Analyze).

        @return: Wether the settings file's 'Use Cache' checkbox is checked.
        @rtype: bool
        """
        useCachedSettingList = self.MODULE.SettingsFile.getSetting(
            self.MODULE.LoginMenu.hostDropdown.currentText, 
            self.MODULE.Settings['CACHE'].USE_CACHED_IMAGES_TAG)
        #print "USE CACHED SETTING", useCachedSettingList
        useCachedSetting = True if (len(useCachedSettingList) > 0 and 'True' in useCachedSettingList[0]) else False

        return useCachedSetting 



    def performUseCacheUpdates(self):
        """
        """
        self._dst = None
        folderUri = self._src.replace('?format=zip', '')
        
        # Update the download popup
        self.MODULE.Workflow_Load.XnatDownloadPopup.setText(folderUri, 
                                                           "USING CACHED<br>'%s'"%(self.MODULE.Workflow_Load.XnatDownloadPopup.makeDownloadPath(folderUri)))
        self.MODULE.Workflow_Load.XnatDownloadPopup.setProgressBarValue(folderUri, 100)
        self.MODULE.Workflow_Load.XnatDownloadPopup.setEnabled(folderUri, False)
        self.extractedFiles = self.cachedFiles
        return




    def checkCache(self, *args):
        """
        To be inherited by the subclass.  Will contain the specific 
        cache checking mechanisms for the image set that will be downloaded.
        """
        pass

