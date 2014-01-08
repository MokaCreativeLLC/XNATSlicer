from XnatUtils import *
from __main__ import vtk, ctk, qt, slicer

import os
import sys
import shutil
import zipfile

from GLOB import *
from XnatFileInfo import *
from XnatScenePackager import *
from XnatTimer import *
from XnatSaveDialog import *
from MokaUtils import *




    
class XnatSaveWorkflow(object):
    """ 
    XnatSaveWorkflow manages all of the processes needed to upload
    a file to an XNAT.  Packaging scenes are conducted here.
    """

    def __init__(self, MODULE):
        """ 
        Init function.

   
        """
        
        self.MODULE = MODULE
        self.XnatScenePackager = XnatScenePackager(self.MODULE)
        
        #------------------------
        # Set wait window
        #------------------------
        self.waitWindow = qt.QMessageBox(1, "Uploading", "Please wait while file uploads...")


        
    def beginWorkflow(self):
        """ 
        Conducts some prelimiary 
        steps (i.e. origin identification) before uploading 
        the scene to the XNAT host.
        """

        #------------------------
        # If Scene originated from XNAT (i.e. the session manager is active), 
        # we can go right to the 'save' dialog.
        #------------------------
        if self.MODULE.XnatView.sessionManager.sessionArgs:
            self.MODULE.XnatView.setEnabled(False)

            #
            # Show the fileSaveDialog
            #
            fileSaveDialog = XnatFileSaveDialog(self.MODULE, self)
            fileSaveDialog.show()
            


        #------------------------
        # If scene is local, or of non-XNAT origin
        #------------------------
        elif (not self.MODULE.XnatView.sessionManager.sessionArgs):
            
            #
            # Construct new sessionArgs
            #
            fullPath = self.MODULE.XnatView.getXnatUri()
            remoteURI = self.MODULE.XnatSettingsFile.getAddress(self.MODULE.XnatLoginMenu.hostDropdown.currentText) + fullPath
            sessionArgs = XnatSessionArgs(MODULE = self.MODULE, srcPath = fullPath)
            sessionArgs['sessionType'] = "scene upload - unlinked"
            self.MODULE.XnatView.sessionManager.startNewSession(sessionArgs)
            self.MODULE.XnatView.setEnabled(False)

            #
            # Show the fileSaveDialog
            #
            fileSaveDialog = XnatFileSaveDialog(self.MODULE, self)
            fileSaveDialog.show()




        
    def saveScene(self):    
        """  
        Main function for saving/uploading a file
        to an XNAT host.
        """

        #------------------------
        # Show wait window
        #------------------------
        self.waitWindow.show()



        #------------------------
        # Disable the view widget
        #------------------------
        self.MODULE.XnatView.setEnabled(False)



        #------------------------
        # Save the scene locally via XnatScenePackager.saveSlicerScene
        #------------------------
        package = self.XnatScenePackager.saveSlicerScene(self.MODULE.XnatView.sessionManager.sessionArgs)


        
        #------------------------
        # Get the appropriate file paths from 
        # the locally saved scene above.
        #------------------------
        projectDir = package['path']
        mrmlFile =  package['mrml']  
        


        #------------------------
        # Using the file paths above, 
        # zip up the save directory...
        #------------------------ 

        #
        # Construct the .mrb uri.
        #
        srcMrb = projectDir + GLOB_DEFAULT_SLICER_EXTENSION
        
        #
        # Remove any mrb files with the same name, 
        # if they exist.
        #
        if os.path.exists(srcMrb): 
            os.remove(srcMrb) 

        #
        # Compress the save diectory to the mrb uri.
        #
        self.XnatScenePackager.convertDirectoryToZip(srcMrb, projectDir)

        #
        # Remove the uncompressed directory, as we
        # don't need it any more. 
        #       
        shutil.rmtree(projectDir)



        #------------------------
        # Upload the mrb to XNAT.
        #------------------------

        #
        # Construct the upload string.
        #
        dstMrb = self.MODULE.XnatView.sessionManager.sessionArgs['saveUri'] + "/" + os.path.basename(srcMrb)    

        #
        # Upload via XnatIo
        #
        self.MODULE.XnatIo.upload(srcMrb, dstMrb)

        #
        # Process events.
        #
        slicer.app.processEvents()
  


        #------------------------
        # Update viewer
        #------------------------
        baseName = os.path.basename(srcMrb)

        #
        # Create a new session
        #
        self.MODULE.XnatView.sessionManager.sessionArgs['sessionType'] = "scene upload"
        self.MODULE.XnatView.startNewSession(self.MODULE.XnatView.sessionManager.sessionArgs)

        #
        # Select the newly saved object as a node in the viewer.
        #
        treeUri = 'projects' + dstMrb.split('projects')[1]
        self.MODULE.XnatView.selectItem_byUri(treeUri)
        self.MODULE.XnatView.setEnabled(True)
        MokaUtils.debug.lf("\nUpload of '%s' complete."%(baseName))



        #------------------------
        # Hide wait window
        #------------------------
        self.waitWindow.hide()

                    
