from XnatSlicerGlobals import *
from MokaUtils import *
from XnatSlicerUtils import *
from Loader import *
from MrmlParser import *



class Loader_Mrb(Loader):
    """
    Loader_Mrb is a subclass of the Loader class.
    It contains specific functions for downloadloading scenes from an XNAT server, 
    and loading them into Slicer.  This is in contrast with loading DICOM sets, 
    individual files or analyze files.

    One of the unique aspects of loading scenes is the necessity to parse
    the scene MRML in order to convert all absolute paths to local paths. 
    """


    def __init__(self, MODULE, _src):
        super(Loader_Mrb, self).__init__(MODULE, _src)
        self.setFileSrcDst()
        


        
    def load(self):
        """ Main load function for downloading Slicer scenes
            and loading them into Slicer.  

            Refers to a number of functions below (updateAbsoluteMrmlUrisToRelative, 
            deconstructMrb, etc.) to load the mrml.
        """


        
        if not os.path.exists(self._dst): return     

        
        #-------------------------
        # To track relevant 'FileInfo' object remote and local
        # filepaths associated with the scene.
        #-------------------------
        fileInfo = FileInfo(remoteURI = self._src, localURI = self._dst)


        
        #-------------------------
        # Acquire the 'packageInfo' by calling on the 
        # function 'deconstructMrb'
        #-------------------------
        packageInfo = self.deconstructMrb(fileInfo) 



        #-------------------------
        # Cache the scene. 
        #-------------------------    
        self.storeSceneLocally(packageInfo, False)   

        
        
        #-------------------------
        # Acquire the updated sceneMrml by calling on the function
        # 'updateAbsoluteMrmlUrisToRelative'
        #-------------------------        
        newMRMLFile = self.updateAbsoluteMrmlUrisToRelative(packageInfo)


        
        #-------------------------
        # Load is good if MRML file is found in the package.
        #-------------------------
        if newMRMLFile: 
            return self.loadFinish(newMRMLFile)    
        
        return False



    
    def unzipMrb(self, packageFileName, destDir):
        """ As stated.  Unzips the '.zip' or '.mrb' Slicer file to 
            the destination provided in the arguments.
        """
        fileURLs = []



        #-------------------------
        # Unzip scenes with a .zip extension
        #-------------------------
        if packageFileName.endswith('zip'):
            z = zipfile.ZipFile(packageFileName)
            try:               
                z.extractall(destDir)
                for root, subFolders, files in os.walk(destDir):
                    for file in files:
                        fileURLs.append(MokaUtils.path.adjustPathSlashes(os.path.join(root,file)))
            except Exception, e:
                MokaUtils.debug.lf("Extraction error: %s"%(str(e)))


                
        #-------------------------
        # Unzip scenes with a .mrb extension
        #-------------------------
        elif packageFileName.endswith('mrb'):          
            logic = slicer.app.applicationLogic()
            if not os.path.exists(destDir):
                os.makedirs(destDir)
            logic.Unzip(packageFileName, destDir)
            mrbDir = os.path.join(destDir, os.path.basename(packageFileName).split(".")[0])
            
            #
            # MRB files decompress to a folder of the same name.  
            # Need to move all the files back to destDir.
            #
            fileURLs = MokaUtils.path.moveDir(mrbDir, destDir) 
        return fileURLs



    
    def deconstructMrb(self, currFileInfo):
        """ Checks downloaded scene file for its contents.  
            Delegates how to handle it accordingly.
        """
        
        #-------------------------
        # Unzip scene, get files
        #-------------------------
        extractDir = XnatSlicerGlobals.LOCAL_URIS['downloads']
        tempUnpackDir = os.path.join(extractDir, currFileInfo.basenameNoExtension)
        fileList = self.unzipMrb(currFileInfo.localURI, tempUnpackDir)



        #-------------------------
        # Return dictionary of useful params
        #-------------------------
        return {'basename': currFileInfo.basename, 
                'unpackDir': tempUnpackDir, 
                'nameOnly': currFileInfo.basenameNoExtension, 
                'remoteURI': currFileInfo.remoteURI, 
                'localURI': currFileInfo.localURI}



    
    def updateAbsoluteMrmlUrisToRelative(self, packageInfo):
        """ Converts any absolute file paths in 
            the .mrml to relative file paths.  
        """
        
        #-------------------------
        # Init params.
        #-------------------------
        scenePackageBasename = packageInfo['basename']
        extractDir = packageInfo['unpackDir']
        sceneName = packageInfo['nameOnly']
        remoteURI = packageInfo['remoteURI']
        localURI = packageInfo['localURI']



        #-------------------------
        # Get MRMLs and nodes within package.
        #-------------------------
        fileList = []
        rootdir = self.cachePathDict['localFiles']
        for root, subFolders, files in os.walk(rootdir):
            for file in files:
                fileList.append(os.path.join(root,file))


        #-------------------------
        # Define relevant paths.
        #-------------------------
        newRemoteDir = MokaUtils.path.getAncestorUri(remoteURI, "resources")
        filePathsToChange = {}



        #-------------------------
        # Look at the files within the bundle.  Create a key-value
        # pair of the absolute URIs to relative URIs.
        #-------------------------
        mrmlFiles = []
        for fileUri in fileList:
            if XnatSlicerUtils.isMRML(fileUri): 
                mrmlFiles.append(fileUri)
                mrmlBase = os.path.basename(fileUri)
                if os.path.basename(os.path.dirname(fileUri)) == "Data":
                    #
                    # Special case for url encoding
                    #
                    filePathsToChange[os.path.basename(urllib2.quote(mrmlBase))] = "./Data/" + urllib2.quote(mrmlBase)

                

        #-------------------------
        # Parse MRML, converting the absolute URIs to local URIs
        #
        # NOTE: this step is necessary because the absolute paths
        # for files fails when the same scene is loaded on a different
        # machine that would potentially have a different file structure.
        # Therefore it's necessary to parse the MRML and convert
        # all absolute URIs to relative.
        #-------------------------
        if len(mrmlFiles) > 0:
            newMRMLFile = MokaUtils.path.addSuffixToFileName(mrmlFiles[0], "-LOCALIZED")       
            #
            # NOTE: Parsing of the MRML is needed because node filePaths are absolute, not relative.
            # TODO: Submit a change request for absolute path values to Slicer
            #
            mrmlParser = MrmlParser(self.MODULE)
            mrmlParser.changeValues(mrmlFiles[0], newMRMLFile,  {},  None, True)
            return newMRMLFile



    
    
    def storeSceneLocally(self, packageInfo, cacheOriginalPackage = True):
        """ Creates a project cache (different from an image cache) 
            based on parameters specified in the packageInfo argument.
        """  

        
        #-------------------------
        # Init params         
        #-------------------------
        scenePackageBasename = packageInfo['basename']
        extractDir = packageInfo['unpackDir']
        sceneName = packageInfo['nameOnly']
        remoteURI = packageInfo['remoteURI']
        localURI = packageInfo['localURI']

        

        #-------------------------
        # Establish caching directories
        #-------------------------
        sceneDir = os.path.join(XnatSlicerGlobals.LOCAL_URIS['projects'], sceneName)
        if not os.path.exists(sceneDir): os.mkdir(sceneDir)       
        self.cachePathDict = {'localFiles': os.path.join(sceneDir, 'localFiles'),
                              'cacheManager': os.path.join(sceneDir, 'cacheManagement'),
                              'originalPackage': os.path.join(sceneDir, 'originalPackage')}

        

        #-------------------------
        # Create relevant paths locally
        #-------------------------
        for value in self.cachePathDict.itervalues(): 
            if not os.path.exists(value):
                try: os.makedirs(value)
                except Exception, e: 
                    MokaUtils.debug.lf("Couldn't make the following directory: %s\nRef. Error: %s"%(value, str(e)))# {} for some strange reason!").format(str(value))
            else:
                #MokaUtils.debug.lf( "REMOVING EXISTING FILES IN '%s'"%(value))
                shutil.rmtree(value)
                os.mkdir(value)


                
        #-------------------------
        # Move unpacked contents to new directory
        #-------------------------
        MokaUtils.path.moveDir(extractDir, self.cachePathDict['localFiles'])

        

        #-------------------------
        # Move package as well to cache, if desired 
        #-------------------------
        if cacheOriginalPackage:
            qFile = qt.QFile(localURI)
            qFile.copy(os.path.join(self.cachePathDict['originalPackage'], scenePackageBasename))
            qFile.close()



        #-------------------------
        # Delete original package as it should be moved.
        #-------------------------
        try:
            os.remove(localURI)
        except Exception, e:
            MokaUtils.debug.lf("Can't remove the moved file -- a thread issue.")



            
    def loadFinish(self, fileName, specialCaseFiles = None):
        """Loads a scene from a MRML file int Slicer.
           Creates a new XNATSession to be tracked by XNATSlicer.
        """

        #-------------------------
        # Call slicer's native 'loadscene' function.
        #-------------------------
        ##print( "Loading '" + os.path.basename(self._src) + "'")
        slicer.util.loadScene(fileName) 


        
        #-------------------------
        # Create new XNAT session.
        #-------------------------
        sessionArgs = XnatSessionArgs(MODULE = self.MODULE, srcPath = self._src)
        sessionArgs['sessionType'] = "scene download"
        self.MODULE.View.startNewSession(sessionArgs)
        ##print( "\nScene '%s' loaded."%(os.path.basename(fileName.rsplit(".")[0])))  


        
        #-------------------------
        # Enable the View.
        #-------------------------
        self.MODULE.View.setEnabled(True)
        return True
