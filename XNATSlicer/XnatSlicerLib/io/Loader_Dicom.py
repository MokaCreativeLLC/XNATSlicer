# python
import os

# application
import slicer
import DICOMScalarVolumePlugin 

# module
from Loader import *
from XnatSlicerUtils import *




class Loader_Dicom(Loader_Images):
    """ 
    Loader_Dicom conducts the necessary steps
    to load DICOM files into Slicer.

    NOTE: DICOMLoader makes use of Slicer's DICOM database and 
    for parsing.
    """
    

    def checkCache(self, fileUris):
        """ 
        Checks the fileUris against the dicom database.  If there's
        a 100% match, immediately defaults to using the cache.

        @param fileUris: The fileUris to check the cache against.
        @type fileUris: list(str)
        """



        splitter = '/experiments/'
        #--------------------
        # Get the abbreviated file URIs
        # and their directories.
        #--------------------
        abbrevUris = [ fileUri.split(splitter)[1] for fileUri in fileUris if XnatSlicerUtils.isDICOM(fileUri) ]
        #print "abbrevUris", abbrevUris
                


                    
        #--------------------
        # Get database files, abbreviate as necessary
        #--------------------
        fullDbFiles = [fullDbFile for fullDbFile in slicer.dicomDatabase.allFiles() if splitter in fullDbFile ]
        abbrevDbFiles = [fullDbFile.split(splitter)[1] for fullDbFile in fullDbFiles]     
        fullToAbbrev = dict(zip(abbrevDbFiles, fullDbFiles))
   


                
        #--------------------
        # Check for string matches between the folder URI
        # and the database files 
        #--------------------
        self.cachedFiles = [fullToAbbrev[dbFile] for dbFile in abbrevDbFiles for abbrevUri in abbrevUris if abbrevUri in dbFile]

                    
        #--------------------   
        # If all URIs are in the database, use cache, exit.
        #--------------------    
        if len(self.cachedFiles) == len(abbrevUris):
            return True
          
        return False
       

                


                
    def load(self): 
        """ 
        Main load function for downloading DICOM files
        from an XNAT server and loading them into Slicer. 
        """

        if self.useCached:
            return self.loadDicomsFromDatabase(self.extractedFiles)


        if not os.path.exists(self._dst):
            return 
        

        
        #--------------------
        # Make sure Slicer's DICOMdatabase is set up.
        # Show a popup informing the user if it's not.
        # The user has to restart the process if it's not.
        #--------------------
        m = slicer.util.mainWindow()
        if not slicer.dicomDatabase:
            msg =  """It doesn\'t look like your DICOM database directory is setup. Please set it up in the DICOM module.  You can load your downloaded files here: '***HERE***'."""
            msg = msg.replace('***HERE***', self._dst)
            self.terminateLoad(['DICOM load', msg ])
            m.moduleSelector().selectModule('DICOM')    



        #--------------------
        # UNZIP dst
        #--------------------
        self.extractDst()

        

        #--------------------
        # Add DICOM files to slicer.dicomDataase
        #--------------------
        dicomIndexer = ctk.ctkDICOMIndexer()
        try:
            dicomIndexer.addListOfFiles(slicer.dicomDatabase, self.extractedFiles)
        except Exception, e:
            
            #
            # If the database is uninitialized, then initialize it.
            #
            errorString = str(e)
            if 'uninitialized ctkDICOMItem' in errorString:
                #print (MokaUtils.debug.lf(), "The slicer.dicomDabase is unitialized (%s).  Initializing it."%(errorString))
                slicer.dicomDatabase.initialize()
                dicomIndexer.addListOfFiles(slicer.dicomDatabase, self.extractedFiles)



        #--------------------
        # Load the 'downloaded' DICOMS from Slicer's database.
        #--------------------
        return self.loadDicomsFromDatabase(self.extractedFiles)



    
    def loadDicomsFromDatabase(self, dicomFiles):
        """ 
        Loads a set of dicom database files from the slicer.dicomDatabase
        into Slicer without prompting the user to input anything.  
        The 'loadable' with the hightest priority has the highest 
        file count.

        @param dicomFiles: The local dicomFiles to load.
        @type dicomFiles: list(str)
        """

        #--------------------
        # Create dictionary of downloaded DICOMS
        # for quick retrieval when comparing with files
        # in the slicer.dicomDatabase.  Speed preferred over
        # memory consumption here.
        #--------------------      
        dlDicomObj = {}
        for dlFile in dicomFiles:
            dlDicomObj[os.path.basename(dlFile)] = dlFile


            
        #--------------------
        # Parse through the slicer.dicomDatabase
        # to get all of the files, as determined by series.
        #--------------------
        matchedDatabaseFiles = []
        for patient in slicer.dicomDatabase.patients():
            for study in slicer.dicomDatabase.studiesForPatient(patient):
                for series in slicer.dicomDatabase.seriesForStudy(study):
                    seriesFiles = slicer.dicomDatabase.filesForSeries(series)
                    #
                    # Compare files in series with what was just downloaded.
                    # If there's a match, append to 'matchedDatabaseFiles'.
                    #
                    for sFile in seriesFiles:
                       if os.path.basename(sFile) in dlDicomObj: 
                           matchedDatabaseFiles.append(sFile)


                           
        #--------------------
        # Acquire loadabes as determined by
        # the 'DICOMScalarVolumePlugin' class, by feeding in 
        # 'matchedDatabaseFiles' as a nested array.
        #--------------------
        dicomScalarVolumePlugin = slicer.modules.dicomPlugins['DICOMScalarVolumePlugin']()
        loadables = dicomScalarVolumePlugin.examine([matchedDatabaseFiles])


        
        #--------------------
        # Determine loadable with the highest file count. 
        # This is usually all DICOM files collated as one volume.
        #--------------------
        highestFileCount = 0
        highestFileCountIndex = 0
        for i in range(0, len(loadables)):
            if len(loadables[i].files) > highestFileCount:
                highestFileCount = len(loadables[i].files)
                highestFileCountIndex = i


                
        #--------------------
        # Load loadable with the highest file count.
        # This is assumed to be the volume file that contains
        # the majority of the downloaded DICOMS.
        #--------------------
        dicomScalarVolumePlugin.load(loadables[highestFileCountIndex])
                    


        
        #--------------------
        # Return true if login successful.
        #--------------------        
        return True



            
    def beginDICOMSession(self):
        """ 
        @deprecated: Once a DICOM folder has been downloaded, 
        track the origins of the files for Save/upload
        routines.
        """
        ##print(MokaUtils.debug.lf(), "DICOMS successfully loaded.")
        sessionArgs = XnatSessionArgs(MODULE = self.MODULE, srcPath = self.xnatSrc)
        sessionArgs['sessionType'] = "dicom download"
        self.MODULE.View.startNewSession(sessionArgs)


