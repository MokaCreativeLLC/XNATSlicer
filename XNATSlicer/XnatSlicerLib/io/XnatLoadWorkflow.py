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
XnatWorkflow is a parent class to various loader classes:
XnatSceneLoadWorkflow, XnatLoadWorkflow, XnatFileLoadWorkflow.  
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


        self.areYouSureDialog = qt.QMessageBox()
        self.areYouSureDialog.setIcon(4)
        
        self.areYouSureDialog.setText("You are about to load all readable scans from '**HERE**'.\n" +  
                                      "This may take several minutes.\n" +
                                      "Are you sure you want to continue?")
        self.areYouSureDialog.addButton(qt.QMessageBox.Yes)
        self.areYouSureDialog.addButton(qt.QMessageBox.No)
        self.areYouSureDialog.connect('buttonClicked(QAbstractButton*)', self.loadMultipleScans)


        self._dstBase = self.MODULE.GLOBALS.LOCAL_URIS['downloads']

        self._src = ''
        self._dst = ''

        


        
    def initLoad(self):
        """ As stated.
        """



        
    def setup(self):
        """ As stated.
        """
        pass



     
    def loadFinish(self):
        """ As stated.
        """
        pass


    
    @property
    def loadArgs(self):
        return {'src': self._src, 'dst': self._dst}


    
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
        # Cycle through lit to determine loadability.
        #------------------------
        for file in fileList:
            file = str(file)
            if self.MODULE.utils.isDICOM(file):
                dicoms.append(file)                   
            if self.MODULE.utils.isMRML(file): 
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
        _src = self.MODULE.XnatSettingsFile.getAddress(self.MODULE.XnatLoginMenu.hostDropdown.currentText) + '/data' + pathObj['childQueryUris'][0]


        
        #------------------------    
        # If the '_src' is at the scan level, we have to 
        # adjust it a little bit: it needs a '/files' prefix.
        #------------------------
        if '/scans/' in _src and os.path.dirname(_src).endswith('scans'):
            _src += '/files'


            
        #------------------------    
        # Clear download queue
        #------------------------
        self.MODULE.XnatIo.clearDownloadQueue()

        ########################################################
        #
        #
        # DOWNLOAD TYPES
        #
        #
        ########################################################



        
        downloadFinishedCallbacks = []
        def runDownloadFinishedCallbacks():
            for callback in downloadFinishedCallbacks:
                print "DOWNLOAD FINISHED!"
                callback()
                slicer.app.processEvents()



        print "Initializing download..."
        
        self.MODULE.XnatDownloadPopup.show()
        
        #------------------------
        # '/files/' LEVEL 
        #------------------------
        if '/files/' in _src:

            #
            # SLICER .MRB
            #
            if '/Slicer/files/' in _src:
                self.MODULE.XnatDownloadPopup.addDownloadRow(_src)
                loader =  self.MODULE.XnatSceneLoadWorkflow
                slicer.app.processEvents()
                loader.setLoadArgs(_src)
                self.MODULE.XnatIo.addToDownloadQueue(loader.loadArgs)
                downloadFinishedCallbacks.append(loader.load) 

        elif '/scans/' in _src:
            #loader =  self.MODULE.XnatDicomLoadWorkflow
            self.MODULE.XnatDownloadPopup.addDownloadRow(_src)   
            slicer.app.processEvents()     
            splitScan =  _src.split('/scans/')   
            scanSrc = splitScan[0] + '/scans/' + splitScan[1].split('/')[0] + '/files'
            print scanSrc
            contents = self.MODULE.XnatIo.getFolderContents(scanSrc, metadataTags = ['URI'])
            print contents
            return


        self.MODULE.XnatIo.startDownloadQueue(runDownloadFinishedCallbacks)
      

    
            
        #------------------------
        # SCAN FILE (NOT THE FOLDER)
        #------------------------
        if '/files/' in _src and '/scans/' in _src:
            currScan = _src.split('/scans/')[1].split('/files/')[0]
            self.loadScan(os.path.dirname(_src), dst.split('downloads/')[0] + 'downloads/' + currScan)
            #return

            
        
        #------------------------
        # SCAN-folder download
        #------------------------
        elif '/scans/' in _src:
            if not '/files/' in _src:

                scanSrc = _src.split('/scans/')[0] + '/scans/files'
                contents = self.MODULE.XnatIo.getFolderContents(scanSrc, metadataTags = ['URI'])
                print contents
                return
                self.MODULE.XnatDownloadPopup.setTotalDownloads(1)
                self.currentDownloadState = 'single'
                self.loadScan(_src, dst)
 


        #------------------------
        # EXPERIMENT-level download
        #------------------------
        elif not '/scans/' in _src and '/experiments/' in _src and _src.endswith('scans'): 
            self.currentDownloadState = 'multiple'
            self._src = _src
            self.dst = dst
            self.areYouSureDialog.setText(self.areYouSureDialog.text.replace('**HERE**', self._src.replace('/scans','').split('data/')[1])) 
            #
            # Hitting yes in this dialog will send you to 'loadMultipleScans'
            #
            self.areYouSureDialog.show()
            


                
            
        #------------------------
        # Enable XnatView
        #------------------------
        self.MODULE.XnatView.setEnabled(True)
        self.lastButtonClicked = None
    


        
    def loadMultipleScans(self, button):
        """
        """
 
        if not 'yes' in button.text.lower(): 
            return
        exptContents =  self.MODULE.XnatIo.getFolderContents(self._src, self.MODULE.utils.XnatMetadataTags_experiments) 

        self.MODULE.XnatDownloadPopup.setTotalDownloads(len(exptContents['ID']))
        
        for _id in exptContents['ID']:
            appender = '/' + _id + '/files'
            src = self._src + appender
            dst = self.dst + appender
            self.MODULE.XnatDownloadPopup.setCheckFileNameNotExtension(False)
            self.loadScan(src, dst)        


        
    def loadScan(self, src, dst):
        """
        """

        #
        # Open the download popup immediately for better UX.
        #
        self.MODULE.XnatDownloadPopup.reset(animated = False)
        fileDisplayName = self.MODULE.utils.makeDisplayableFileName(src)
        self.MODULE.XnatDownloadPopup.setText("Initializing download for:", "'%s'"%(fileDisplayName))
        self.MODULE.XnatDownloadPopup.show()

        if '/files/' in src:
            if '/scans/' in src:
                src = os.path.dirname(src)
            
        contents = self.MODULE.XnatIo.getFolderContents(src, metadataTags = ['URI'])
        print "\n\nCONTETNS", contents
        contentNames = contents['URI']
        analyzeCount = 0
        dicomCount = 0
        loadableFileCount = 0

        for fileName in contentNames:
            if self.MODULE.utils.isAnalyze(fileName):
                analyzeCount += 1
            elif self.MODULE.utils.isDICOM(fileName):
                print "IS DICOM"
                dicomCount += 1
            elif self.MODULE.utils.isRecognizedFileExt(fileName):
                loadableFileCount += 1

                
        print "DICOM count", dicomCount, src, dst
        # 'XnatSceneLoadWorkflow' for Slicer files
        if src.endswith(self.MODULE.utils.defaultPackageExtension): 
            loader = self.MODULE.XnatSceneLoadWorkflow

        # 'XnatAnalyzeWorkflow' for Analyze files
        elif analyzeCount > 0:
            loader =  self.MODULE.XnatAnalyzeLoadWorkflow

        # 'XnatDicomLoadWorkflow' for DICOM files
        elif dicomCount > 0:      
            loader =  self.MODULE.XnatDicomLoadWorkflow

        # 'XxnatFileLoadWorkflow' for other files
        else:
            loader =  self.MODULE.XnatFileLoadWorkflow


        #
        # Call the 'loader's 'initLoad' function.
        #
        # NOTE: Again, the 'loader' is a subclass of this one.
        #
        args = {"xnatSrc": src, 
                "localDst": dst, 
                "uris": contents['URI'],
                "folderContents": None}

        #
        # Begin the LOAD process!
        #
        loadSuccessful = loader.initLoad(args) 
        
