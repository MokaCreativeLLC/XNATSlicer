
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
       
    VTK_EXT = '.vtk'

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
        saveDirectory = os.path.join(XnatSlicerGlobals.LOCAL_URIS['uploads'], \
                                     packageName)
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
        # Call the API command 'slicer.app.applicationLogic().\
        # SaveSceneToSlicerDataBundleDirectory'
        # which will save the scene and all of its nodes
        # into the provided directory.
        #-------------------
        imageData =  self.storeSceneView('MasterSceneView')
        slicer.app.applicationLogic().\
            SaveSceneToSlicerDataBundleDirectory(saveDirectory, imageData)      

        



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





    def convertAllBinaryVtksToAscii(self, projectDir):
        """
        @param projectDir: The vtk filename
        @type projectDir: string
         
        @return: Whether the file was converted (1 or 0) for every file.
        @rtype: array.<number>
        """

        #
        # Get the vtk files in the directory 
        #
        vtks = []
        for root, dirs, files in os.walk(projectDir):
            for relFileName in files:
                if relFileName.lower().endswith(ScenePackager.VTK_EXT):
                    vtks.append(os.path.join(root, relFileName))
        #
        # Convert the files
        #
        converteds = []
        for vtkFile in vtks:
            converteds.append(self.convertBinaryVtkToAscii(vtkFile))
        return converteds



    def storeSceneView(self, name, description=""):
        """  

        NOTE: Taken from here:
        https://github.com/Slicer/Slicer/blob/master/Applications/SlicerApp/
            Testing/Python/SlicerMRBTest.py#L273


        Store a scene view into the current scene.
        TODO: this might move to slicer.util


        @param name: TheSceneViewName
        @return: vtkImageData
        """
        viewport = slicer.app.layoutManager().viewport()
        qImage = qt.QPixmap().grabWidget(viewport).toImage()
        imageData = vtk.vtkImageData()

        slicer.qMRMLUtils().qImageToVtkImageData(qImage,imageData)

        sceneViewNode = slicer.vtkMRMLSceneViewNode()
        sceneViewNode.SetScreenShotType(4)
        sceneViewNode.SetScreenShot(imageData)
 
        return sceneViewNode.GetScreenShot()



    def convertBinaryVtkToAscii(self, vtkFile):
        """
        @param vtkFile: The vtk filename
        @type vtkFile: string
         
        @return: Whether the file was converted (1 or 0)
        @rtype: number
        """
        #
        # Generate a tempFilename
        #
        tempFilename = os.path.splitext(vtkFile)[0] + \
                MokaUtils.string.randomAlphaNumeric() + ScenePackager.VTK_EXT
        #
        # VTK reader
        #
        r = vtk.vtkDataSetReader()
        r.SetFileName(vtkFile)
 
        #
        # VTK writer
        #
        w = vtk.vtkDataSetWriter()
        w.SetInput(r.GetOutput())
        w.SetFileName(tempFilename)
        converted = w.Write()

        #
        # Remove the old file and replace with new
        #
        os.remove(vtkFile)
        os.rename(tempFilename, vtkFile)

        #
        # Return whether file was converted
        #
        return converted



    
    def convertDirectoryToZip(self, zipFileName, directoryToZip):
        """ Zips the bundled directory according to the
            native API methods.
        """
        slicer.app.applicationLogic().Zip(str(zipFileName), str(directoryToZip))
        #return
  
