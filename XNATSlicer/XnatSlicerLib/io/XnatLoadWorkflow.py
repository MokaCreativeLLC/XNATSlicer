from XnatUtils import *
from __main__ import vtk, ctk, qt, slicer

import os
import sys

from XnatLoader import *
from XnatLoader_Analyze import *
from XnatLoader_Dicom import *
from XnatLoader_File import *
from XnatLoader_Mrb import *
from XnatPopup import *
from SlicerUtils import *



class XnatLoadWorkflow(object):
    """ 
    XnatLoadWorkflow is effectively a factory for various loader classes.  
    Loader types are determined by the XnatView item being clicked in the 
    XnatLoadWorkflow function 'beginWorkflow'.  
    
    Parent Load workflow class to: XnatDicomLoadWorkflow, 
    XnatMrbLoadWorkflow, and XnatFileLoadWorkflow.
    """

    
    def __init__(self, MODULE):
        """ Parent init.
        """
        self.MODULE = MODULE       
        self.loadFile = None
        self.newMRMLFile = None
        self.currRemoteHost = None


        self.skipEmptySceneCheck = False
        self._src = None


        
        #--------------------------------
        # Popups
        #--------------------------------
        self.areYouSureDialog = qt.QMessageBox()
        self.areYouSureDialog.setIcon(4)
        self.areYouSureDialog.setText("You are about to load all readable scans from '**HERE**'.\n" +  
                                      "This may take several minutes.\n" +
                                      "Are you sure you want to continue?")
        self.areYouSureDialog.addButton(qt.QMessageBox.Yes)
        self.areYouSureDialog.addButton(qt.QMessageBox.No)
        self.areYouSureDialog.connect('buttonClicked(QAbstractButton*)', self.beginWorkflow)



        self.XnatDownloadPopup = XnatDownloadPopup()
        self.XnatDownloadPopup.setCancelCallback(self.MODULE.XnatIo.cancelDownload)
        
        self.clearScenePopup = XnatClearScenePopup()
        self.clearScenePopup.connect('buttonClicked(QAbstractButton*)', self.clearSceneButtonClicked) 

        self.preDownloadPopup = XnatTextPopup('<b>Checking files...</b>')
        self.postDownloadPopup = XnatTextPopup('<b>Processing.  Data will load automatically.</b>')



    def sortLoadablesByType(self, fileUris):
        """
        Sorts a list of file uris by XNATSlicer loadable types.  Generally used 
        when multi-folder downloading is in effect.

        @param fileUris: The list of iles to sort..
        @type: list(string)

        @return: A dictionary where each key specifies the loadable type.
        @rtype: dict
        """
        
        filesByType = {
            'analyze': [],
            'dicom': [],
            'misc': [],
            'unknown': []
        }

        for fileUri in fileUris:
            if XnatUtils.isAnalyze(fileUri):
                filesByType['analyze'].append(fileUri)
            elif XnatUtils.isDICOM(fileUri):
                filesByType['dicom'].append(fileUri)
            elif XnatUtils.isMiscLoadable(fileUri):
                filesByType['misc'].append(fileUri)
            else:
                filesByType['unknown'].append(fileUri)

        return filesByType




    def resetIOCallbacks(self):
        """ Clears and sets the IO callbacks for the MODULE.XnatIO.
            Callbacks labeleled accordingly.
        """

        #--------------------------------
        # Clear IO Download queue
        #--------------------------------
        self.MODULE.XnatIo.clearDownloadQueue()



        #--------------------------------
        # START
        #--------------------------------
        def downloadStarted(_xnatSrc, size = 0):
            #print "\n\nDOWNLOAD START", self.XnatDownloadPopup.downloadRows, "\n\n"
            #if size > 0:
            self.XnatDownloadPopup.setSize(_xnatSrc.split('?format=zip')[0], size)
            slicer.app.processEvents()
        self.MODULE.XnatIo.setCallback('downloadStarted', downloadStarted)

        

        #--------------------------------
        # Downloading
        #--------------------------------
        def downloading(_xnatSrc, size = 0):
            self.XnatDownloadPopup.updateDownload(_xnatSrc.split('?format=zip')[0], size)
            slicer.app.processEvents()
        self.MODULE.XnatIo.setCallback('downloading', downloading)

        

        #--------------------------------
        # FINISHED
        #--------------------------------
        def downloadFinished(_xnatSrc):
            self.XnatDownloadPopup.setComplete(_xnatSrc.split('?format=zip')[0])
            slicer.app.processEvents()
        self.MODULE.XnatIo.setCallback('downloadFinished', downloadFinished)



        #--------------------------------
        # CANCELLED
        #--------------------------------
        def downloadCancelled(_xnatSrc):
            if len(self.MODULE.XnatIo.downloadQueue) == 0:
                self.XnatDownloadPopup.hide()
                slicer.app.processEvents()
        self.MODULE.XnatIo.setCallback('downloadCancelled', downloadCancelled)

        
        
    
    def terminateLoad(self, warnStr):
        """ Notifies the user that they will terminate the load.
            Reenables the viewer UI.
        """
        qt.QMessageBox.warning( None, warnStr[0], warnStr[1])




    def clearSceneButtonClicked(self, button):
        """
        """
        if 'yes' in button.text.lower():
            self.MODULE.XnatView.sessionManager.clearCurrentSession()
            slicer.app.mrmlScene().Clear(0)
            self.skipEmptySceneCheck = True
            self.beginWorkflow()

            

    def beginWorkflow(self, src = None):
        """ This function is the first to be called
            when the user clicks on the "load" button (right arrow).
            The class that calls 'beginWorkflow' has no idea of the
            workflow subclass that will be used to load
            the given XNAT node.  Those classes (which inherit from
            XnatLoadWorkflow) will be called on in this function.
        """


        if not self._src:
            self._src = src


            
        #------------------------
        # Show clearSceneDialog
        #------------------------
        if '/scans/' in self._src:
            splitter = self._src.split('/scans/')
            self._src = splitter[0] + '/scans/' + splitter[1].split('/')[0] + '/files'


            
        #------------------------
        # Show clearSceneDialog
        #------------------------
        if not SlicerUtils.isCurrSceneEmpty() and not self.skipEmptySceneCheck:
            self.clearScenePopup.show()
            return


    
        #------------------------    
        # Clear download queue
        #------------------------
        self.resetIOCallbacks()

        

        #------------------------
        # Set Download finished callbacks
        #------------------------        
        downloadFinishedCallbacks = []
        def runDownloadFinishedCallbacks():
            self.XnatDownloadPopup.hide()
            self.postDownloadPopup.show()
            for callback in downloadFinishedCallbacks:
                #print "DOWNLOAD FINISHED!"
                callback()
                slicer.app.processEvents()
                self._src = None
            self.postDownloadPopup.hide()
            self.MODULE.XnatIo.clearDownloadQueue()

            
        
        #------------------------
        # Show download popup
        #------------------------  
        #print "Initializing download..."
        self.preDownloadPopup.show()


        
        #------------------------
        # Get loaders, add to queue
        #------------------------  
        for loader in self.loaderFactory(self._src):
            if not loader.useCached:
                self.MODULE.XnatIo.addToDownloadQueue(loader.loadArgs)
            downloadFinishedCallbacks.append(loader.load)             


            
        #------------------------
        # Run loaders
        #------------------------ 
        self.preDownloadPopup.hide()
        self.XnatDownloadPopup.show()
        self.MODULE.XnatIo.startDownloadQueue(onQueueFinished = runDownloadFinishedCallbacks)
      

        
        #------------------------
        # Enable XnatView
        #------------------------
        self.MODULE.XnatView.setEnabled(True)
        self.lastButtonClicked = None
    


        
    def loaderFactory(self, _src):
        """ Returns the appropriate set of loaders after analyzing the
            '_src' argument.

            Arguments:
            _src The URI to create loaders from.

            Returns:
            A loader list.
            
        """

        #print "\n\nLOADER FACTORY"
        loaders = []


        
        #------------------------
        # Open popup
        #------------------------
        if '/scans/' in _src or '/files/' in _src:
            #print "OPENING POPUP ROW", _src
            self.XnatDownloadPopup.addDownloadRow(_src)
            #print self.XnatDownloadPopup.downloadRows
            


            
            
        #------------------------
        # '/files/' LEVEL 
        #------------------------
        if '/files/' in _src:
            
            # MRB
            if '/Slicer/files/' in _src:
                #print "FOUND SLICER FILE"
                loaders.append(XnatLoader_Mrb(self.MODULE, _src))
                



        #------------------------
        # '/scans/' LEVEL 
        # 
        # Basically, look at the contents of the scan folder
        # and return the appropriate loader
        #------------------------
        elif '/scans/' in _src:

            # uri manipulation
            splitScan =  _src.split('/scans/')   
            scanSrc = splitScan[0] + '/scans/' + splitScan[1].split('/')[0] + '/files'
            #print "SPLIT SCAN:", splitScan, '\n\t',scanSrc
            # query xnat for folder contents
            contentUris = self.MODULE.XnatIo.getFolder(scanSrc, metadataTags = ['URI'])['URI']
            #print "CONTENT URIS", contentUris
            # get file uris and sort them by type
            loadables = self.sortLoadablesByType(contentUris)
            #print "LOADABLES", loadables
            # cycle through the loadables and
            # create the loader for each loadable list.
            for loadableType, loadableList in loadables.iteritems():
                if len(loadableList) > 0:
                    if loadableType == 'analyze':
                        loaders.append(XnatLoader_Analyze(self.MODULE, _src, loadables[loadableType]))
                    if loadableType == 'dicom':      
                        loaders.append(XnatLoader_Dicom(self.MODULE, _src, loadables[loadableType]))
                    if loadableType == 'misc':
                        loaders.append(XnatLoader_File(self.MODULE, _src, loadables[loadableType]))


                        
        #------------------------
        # '/experiments/' LEVEL 
        #
        # Basically, recurse this function after querying for the 
        # scans in it.
        #------------------------
        elif '/experiments/' in _src and not '/scans/' in _src and not '/resources/' in _src:

            # Uri manipulation
            splitExpt = _src.split('/experiments/')
            exptSrc = splitExpt[0] + '/experiments/' + splitExpt[1].split('/')[0] + '/scans'
            #print "SPLIT Expt:", splitExpt, '\n\t',exptSrc
            # Query for Scan IDs from XNAT.
            contents = self.MODULE.XnatIo.getFolder(exptSrc, metadataTags = ['ID'])
            #print "SCAN IDS", contents
            # Recurse this function for every scan.
            for scanId in contents['ID']:
                scanSrc = exptSrc + '/' + scanId + '/files'
                #print "\n\nLOADING SCAN SOURCE", scanSrc
                loaders += self.loaderFactory(scanSrc)

            # Return loaders
            return loaders
                
            
        return loaders
