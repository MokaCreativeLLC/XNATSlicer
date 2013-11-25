from __main__ import vtk, ctk, qt, slicer

import os
import sys
import shutil
import zipfile
import urllib2
from datetime import datetime


from XnatFileInfo import *
from XnatUtils import *
from XnatScenePackager import *
from XnatTimer import *
from XnatSessionManager import *
from XnatMrmlParser import *
from XnatPopup import *




comment = """
XnatLoadWorkflow is a parent class to various loader classes:
XnatSceneLoadWorkflow, XnatDicomLoadWorkflow, XnatFileLoadWorkflow.  
Loader types are determined by the treeViewItem being clicked in the 
XnatLoadWorkflow function 'beginWorkflow'.  Functions of XnatLoadWorkflow
are generic in nature and pertain to string construction for querying
and downloading files.

TODO:
"""




class XnatLoadWorkflow(object):
    """ Parent Load workflow class to: XnatDicomLoadWorkflow, 
        XnatSceneLoadWorkflow, and XnatFileLoadWorkflow.
    """

    
    def __init__(self, MODULE):
        """ Parent init.
        """
        self.MODULE = MODULE       
        self.loadFile = None
        self.newMRMLFile = None
        self.currRemoteHost = None


        
    def initLoad(self):
        """ As stated.
        """


        
    def load(self, args):
        """ Sets needed variables.
        """
        self.xnatSrc = args["xnatSrc"]
        self.localDst = args["localDst"]



        
    def setup(self):
        """ As stated.
        """
        pass



     
    def loadFinish(self):
        """ As stated.
        """
        pass



    
    def terminateLoad(self, warnStr):
        """ Notifies the user that they will terminate the load.
            Reenables the viewer UI.
        """
        qt.QMessageBox.warning( None, warnStr[0], warnStr[1])
        self.MODULE.XnatView.setEnabled(True)



        
    def getLoadables_byDir(self, rootDir):
        """ Returns the loadable filenames (determined by filetype) 
            by walking through a directory provided in the 'rootDir'
            argument.
        """
        allImages = []
        mrmls = []
        dicoms = []   
        for folder, subs, files in os.walk(rootDir):
            for file in files:
                extension =  os.path.splitext(file)[1].lower() 
                
                #
                # Check for DICOM extensions
                #
                if self.MODULE.utils.isDICOM(ext = extension):
                    dicoms.append(os.path.join(folder,file))   

                #
                # Check for mrml extension
                #
                if self.MODULE.utils.isMRML(ext = extension): 
                    mrmls.append(os.path.join(folder,file))  

        #
        # Returns loadables.
        #
        return {'MRMLS':mrmls, 'ALLIMAGES': allImages, 'DICOMS': dicoms}



    
    def getLoadables_byList(self, fileList):
        """ Returns the loadable filenames (determined by filetype) 
            in filename list.
        """
        allImages = []
        mrmls = []
        dicoms = []
        others = []    


        
        #------------------------
        # Cycle through list to determine loadability.
        #------------------------
        for file in fileList:
            file = str(file)
            extension =  os.path.splitext(file)[1].lower() 
            if extension or (extension != ""):
                if self.MODULE.utils.isDICOM(ext = extension):
                    dicoms.append(file)                   
                if self.MODULE.utils.isMRML(ext = extension): 
                    mrmls.append(file)
                else:
                    others.append(file)
        return {'MRMLS':mrmls, 'ALLIMAGES': allImages, 'DICOMS': dicoms, 'OTHERS': others, 'ALLNONMRML': allImages + dicoms + others}
   

    

    def beginWorkflow(self, button = None):
        """ This function is the first to be called
            when the user clicks on the "load" button (right arrow).
            The class that calls 'beginWorkflow' has no idea of the
            workflow subclass that will be used to load
            the given XNAT node.  Those classes (which inherit from
            XnatLoadWorkflow) will be called on in this function.
        """

        #------------------------
        # Show clearSceneDialog
        #------------------------
        if not button and not self.MODULE.utils.isCurrSceneEmpty():           
            self.MODULE.XnatView.initClearDialog()
            self.MODULE.XnatView.clearSceneDialog.connect('buttonClicked(QAbstractButton*)', self.beginWorkflow) 
            self.MODULE.XnatView.clearSceneDialog.show()
            return
        

        
        #------------------------
        # Clear the scene and current session if button was 'yes'.
        #
        # NOTE: The user doesn't have to clear the scene at all in
        # order to proceed with the workflow.
        #------------------------
        if (button and 'yes' in button.text.lower()):
            self.MODULE.XnatView.sessionManager.clearCurrentSession()
            slicer.app.mrmlScene().Clear(0)


            
        #------------------------  
        # Acquire vars: current treeItem, the XnatPath, and the remote URI for 
        # getting the file.
        #------------------------
        currItem = self.MODULE.XnatView.currentItem()
        pathObj = self.MODULE.XnatView.getXnatUriObject(currItem)
        remoteUri = self.MODULE.XnatSettingsFile.getAddress(self.MODULE.XnatLoginMenu.hostDropdown.currentText) + '/data' + pathObj['childQueryUris'][0]



        #------------------------    
        # If the 'remoteUri' is at the scan level, we have to 
        # adjust it a little bit: it needs a '/files' prefix.
        #------------------------
        if '/scans/' in remoteUri and os.path.dirname(remoteUri).endswith('scans'):
            remoteUri += '/files'


            
        #------------------------
        # Construct the local 'dst' string 
        # (the local file to be downloaded).
        #------------------------
        dst = os.path.join(self.MODULE.GLOBALS.LOCAL_URIS['downloads'],  currItem.text(self.MODULE.XnatView.getColumn('MERGED_LABEL')))



        #------------------------
        # Determine the type of LoadWorkflow subclass
        # based on the XnatView's currItem
        #------------------------
        
        #
        # Create an 'XnatSceneLoadWorkflow' for Slicer files
        #
        if remoteUri.endswith(self.MODULE.utils.defaultPackageExtension): 
            loader = self.MODULE.XnatSceneLoadWorkflow


        #
        # Create an 'XnatAnalyzeLoadWorkflow' for Analyze files
        #
        elif self.MODULE.utils.isAnalyze(pathObj['currUri']):
            
            remoteUri = pathObj['currUri']
            print "ANALYze", remoteUri, dst
            loader =  self.MODULE.XnatAnalyzeLoadWorkflow

            
        #    
        # Create an 'XnatFileLoadWorkflow' for other files.
        #
        elif ('files' in remoteUri and '/resources/' in remoteUri):

            loader =  self.MODULE.XnatFileLoadWorkflow
            
        #    
        # Create an 'XnatDicomLoadWorkflow' for DICOM files.
        #
        else:      
            loader =  self.MODULE.XnatDicomLoadWorkflow
                    
                    
                
        #------------------------
        # Call the 'loader's 'initLoad' function.
        #
        # NOTE: Again, the 'loader' is a subclass of this one.
        #------------------------
        args = {"xnatSrc": remoteUri, 
                "localDst":dst, 
                "folderContents": None}


        #--------------------
        # Open the download popup immediately for better UX.
        #--------------------
        self.MODULE.XnatDownloadPopup.reset(animated = False)
        fileDisplayName = self.MODULE.utils.makeDisplayableFileName(remoteUri)
        self.MODULE.XnatDownloadPopup.setText("Initializing download for: '%s'"%(fileDisplayName), '')
        self.MODULE.XnatDownloadPopup.show()



        #--------------------
        # Begin the LOAD process!!!!!!
        #--------------------
        loadSuccessful = loader.initLoad(args)  
            
            
            
        #------------------------
        # Enable XnatView
        #------------------------
        self.MODULE.XnatView.setEnabled(True)
        self.lastButtonClicked = None
    
        
