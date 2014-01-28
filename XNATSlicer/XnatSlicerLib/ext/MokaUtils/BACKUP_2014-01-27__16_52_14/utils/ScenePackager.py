
from __future__ import with_statement
from __main__ import vtk, ctk, qt, slicer
import datetime, time

import os
import sys
import shutil
from contextlib import closing
from zipfile import ZipFile, ZIP_DEFLATED


from XnatSlicerGlobals import *
from XnatSlicerUtils import *
from MokaUtils import *
from Timer import *
from FileInfo import *




class ScenePackager(object):
    """
    Class containing methods for packaging scenes pertinent to the 
    XNATSlicer workflow.
    
    ScenePackager is used for the Save / upload process.  When 
    sending a scene to XNAT, the class calls the necessary slicer.app API 
    functions to get all of the scene's files into a .zip (or .mrb).  
    
    TODO : 
    """
       
    def __init__(self, MODULE = None):
        """ Init function.
        """
        self.MODULE = MODULE

        

    
    def saveSlicerScene(self, args):
        """ Main function for bundling a Slicer scene.
        """

        #-------------------
        # Init variables.
        #-------------------
        xnatDir = args['saveUri']
        sceneName = args['fileName'] 
        metadata = args['metadata']      
        packageName = os.path.basename(sceneName.split(".")[0])  



        #-------------------
        # Create a directory for saving locally.
        #-------------------
        saveDirectory = os.path.join(XnatSlicerGlobals.LOCAL_URIS['uploads'], packageName)
        ##print MokaUtils.debug.lf() +  "CREATE PACKAGE DIRECTORY: %s"%(saveDirectory)



        #-------------------
        # Try to remove the existing local directory 
        # with the same name if it exists
        #-------------------
        try:
            ##print MokaUtils.debug.lf() + ("%s does not exist. Making it."%(saveDirectory)) 
            if os.path.exists(saveDirectory): 
                shutil.rmtree(saveDirectory)
        except Exception, e: 
            pass



        #-------------------
        # Make the local save directory.
        #-------------------        
        try: 
            os.mkdir(saveDirectory)
        except Exception, e: 
            pass



        #-------------------
        # Make the local 'data' directory.
        #-------------------
        try: 
            os.makedirs(saveDirectory + "/Data")
        except Exception, e: 
            MokaUtils.debug.lf( "Likely the dir already exists: " + str(e))



        #-------------------
        # Call the API command 'slicer.app.applicationLogic().SaveSceneToSlicerDataBundleDirectory'
        # which will save the scene and all of its nodes
        # into the provided directory.
        #-------------------
        slicer.app.applicationLogic().SaveSceneToSlicerDataBundleDirectory(saveDirectory, None)          



        #-------------------
        # Acqure .mrml filename within the saved dir
        #-------------------
        mrml = None
        for root, dirs, files in os.walk(saveDirectory):
            for relFileName in files:
                if relFileName.endswith("mrml"):
                    mrml = os.path.join(root, relFileName)
                    break


                
        #-------------------
        # Return appropriate dictionary with the mrml file
        # and the save directory.
        #-------------------
        return {'path':MokaUtils.path.adjustPathSlashes(saveDirectory), 
                'mrml': MokaUtils.path.adjustPathSlashes(mrml)}




    
    def convertDirectoryToZip(self, zipFileName, directoryToZip):
        """ Zips the bundled directory according to the
            native API methods.
        """
        slicer.app.applicationLogic().Zip(str(zipFileName), str(directoryToZip))
        #return
  
