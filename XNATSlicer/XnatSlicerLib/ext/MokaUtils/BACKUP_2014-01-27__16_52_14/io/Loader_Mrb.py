# external
from MokaUtils import *

# module
from XnatSlicerGlobals import *
from XnatSlicerUtils import *
from Loader import *
from SlicerUtils import *



class Loader_Mrb(Loader_File):
    """
    Loader_Mrb is a subclass of the Loader class.
    It contains specific functions for downloadloading scenes from an XNAT server, 
    and loading them into Slicer.  This is in contrast with loading DICOM sets, 
    individual files or analyze files.

    One of the unique aspects of loading scenes is the necessity to parse
    the scene MRML in order to convert all absolute paths to local paths. 
    """

        
    def load(self):
        """ 
        Main load function for downloading Slicer scenes
        and loading them into Slicer.  
        
        Refers to a number of functions below (__updateAbsoluteMrmlUrisToRelative, 
        __makeUnpackDir, etc.) to load the mrml.
        """


        if not os.path.exists(self._dst): 
            return     


        #-------------------------
        # Unpack the the mrml
        #-------------------------        
        unpackDir = self.__getUnpackDir(self._src) 
        self.__decompressMrb(self._dst, unpackDir)

        

        #-------------------------
        # Update all absolute MRML filenames to local
        #-------------------------
        mrmls = []
        def callback(localFile):
            if XnatSlicerUtils.isMRML(localFile) and not os.path.basename(localFile).startswith('.'):
                mrmls.append(self.__updateAbsoluteMrmlUrisToRelative(self._src, localFile))
        MokaUtils.path.fileWalk(unpackDir, callback)

        
        #-------------------------
        # Load the first mrml found in the package.
        #-------------------------
        if len(mrmls) > 0: 
            return self.loadFinish(mrmls[0])    
        
        return False


    

    def __decompressMrb(self, packageFileName, destDir):
        """ 
        As stated.  Unzips the '.zip' or '.mrb' Slicer file to 
        the destination provided in the arguments.

        @param packageFileName: The downloaded slicer .mrb.
        @type packageFileName: str
        
        @param destDir: The destination directory to unzip the .mrb to.
        @type destDir: str
        """

        #-------------------------
        # Unzip scenes with a .zip extension
        #-------------------------
        if packageFileName.endswith('.zip'):
            MokaUtils.decompress(packageFileName, destDir)
            
                
        #-------------------------
        # Unzip scenes with a .mrb extension
        #-------------------------
        elif packageFileName.endswith('.mrb'):          
            logic = slicer.app.applicationLogic()
            if not os.path.exists(destDir):
                os.makedirs(destDir)
            logic.Unzip(packageFileName, destDir)
            


    
    def __getUnpackDir(self, remoteUri):
        """ 
        Returns an unpack directory (cache) for the downloaded
        .mrb.

        @param remoteUri: The remoteUri of the .mrb.
        @type remoteUri: str

        @return: The path where to unpack the file.
        @rtype: str
        """
        
        slicerCache = os.path.join(XnatSlicerGlobals.LOCAL_URIS['downloads'], 
                                   'projects' + os.path.dirname(remoteUri.split('projects')[1]))
        return os.path.join(slicerCache, os.path.basename(remoteUri).rsplit('.', 1)[0])
        

    

    def __updateAbsoluteMrmlUrisToRelative(self, remoteUri, mrml):
        """ 
        Converts any absolute file paths in 
        the mrml to relative file paths.  

        @param remoteUri: The remoteUri of the .mrb.
        @type remoteUri: src

        @param mrml: The mrml file to update.
        @type mrml: str

        @return: The update mrml file name.
        @rtype: str
        """
        
        newRemoteDir = MokaUtils.path.getAncestorUri(remoteUri, "resources")
        filePathsToChange = {}
        
        mrmlBase = os.path.basename(mrml)
        if os.path.basename(os.path.dirname(mrml)) == "Data":
            #
            # Special case for url encoding
            #
            filePathsToChange[os.path.basename(urllib2.quote(mrmlBase))] = "./Data/" + urllib2.quote(mrmlBase)

        newMRMLFile = MokaUtils.path.addSuffixToFileName(mrml, "-LOCALIZED")       
        SlicerUtils.MrmlParser.changeValues(mrml, newMRMLFile,  {},  None, True)

        return newMRMLFile




            
    def loadFinish(self, mrml):
        """
        Loads a scene from a MRML file int Slicer.
        Creates a new XNATSession to be tracked by XNATSlicer.

        @param mrml: The mrml file name to open.
        @type mrml: str

        @return: Whether the load was successful or not.
        @rtype: bool
        """

        #-------------------------
        # Call slicer's native 'loadscene' function.
        #-------------------------
        ##print( "Loading '" + os.path.basename(self._src) + "'")
        slicer.util.loadScene(mrml) 


        
        #-------------------------
        # Create new XNAT session.
        #-------------------------
        sessionArgs = XnatSessionArgs(MODULE = self.MODULE, srcPath = self._src)
        sessionArgs['sessionType'] = "scene download"
        self.MODULE.View.startNewSession(sessionArgs)
        ##print( "\nScene '%s' loaded."%(os.path.basename(mrml.rsplit(".")[0])))  


        
        #-------------------------
        # Enable the View.
        #-------------------------
        self.MODULE.View.setEnabled(True)
        return True
