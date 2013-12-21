from XnatLoadWorkflow import *



comment = """
XnatAnalyzeLoadWorkflow contains the specific load methods for analyze 
filetypes (.hdr and .img pairings) to be downloaded from an XNAT host into Slicer.  

TODO:
"""



class XnatAnalyzeLoadWorkflow(XnatLoadWorkflow):
    """ Class description above.  Inherits from XnatLoadWorkflow.
    """


    def initLoad(self, args):
        """ As stated.
        """
        self.load(args)

        
        
    def load(self, args):
        """ Downloads an analyze file pair (.hdr and .img) from XNAT, 
            then attempts to load it via the Slicer API's 'loadNodeFromFile' 
            method, which returns True or False if the load was successful.
        """

        #--------------------    
        # Call parent 'load' method.
        #-------------------- 
        super(XnatAnalyzeLoadWorkflow, self).load(args)


        
        #-------------------- 
        # Construct the analyze file pair dictionary.
        #-------------------- 
        downloadFiles = {'hdr': {'src': None, 'dst': None} , 'img': {'src': None, 'dst': None}}


        #-------------------- 
        # Construct the src-dst values in the dictionary.
        #-------------------- 
        for key in downloadFiles:
            for _file in self.uris:
                if _file.lower().endswith(key):
                    downloadFiles[key]['src'] = self.xnatSrc.split('/data/')[0] + _file

                    fileBasename = os.path.basename(_file)
                    if not fileBasename[:-3] in self.localDst:
                        downloadFiles[key]['dst'] = self.localDst + '/' + fileBasename
                    else:
                        downloadFiles[key]['dst'] = self.localDst
                        if not downloadFiles[key]['src'].endswith(downloadFiles[key]['dst'][-3:]):
                            downloadFiles[key]['dst'] = os.path.dirname(downloadFiles[key]['dst']) + '/' + os.path.basename(downloadFiles[key]['src'])
                            
              

        #-------------------- 
        # Update the download popup
        #-------------------- 
        if self.MODULE.XnatLoadWorkflow.currentDownloadState == 'single':
            #print '\n\nSINGLE!'
            totalDownloadFiles = 0
            for key, item in downloadFiles.iteritems():
                if item['src'] != None:
                    totalDownloadFiles +=1
            self.MODULE.XnatDownloadPopup.setTotalDownloads(totalDownloadFiles)
        else:
            self.MODULE.XnatDownloadPopup.setCheckFileNameNotExtension(True)
        
        #-------------------- 
        # Get the files from XNAT.  
        #
        # NOTE: If one of the file pairs is missing,
        # it will still proceed to load without error.
        #-------------------- 
        for key in downloadFiles:
            self.MODULE.XnatIo.getFile({downloadFiles[key]['src']: downloadFiles[key]['dst']})



        #-------------------- 
        # Create the coreIoManager
        #-------------------- 
        coreIoManager = slicer.app.coreIOManager()


        #print("ASDF", downloadFiles)
        #-------------------- 
        # Try to load the header file first, if it exists.
        #-------------------- 
        if downloadFiles['hdr']['dst'] != None:
            t = coreIoManager.fileType(downloadFiles['hdr']['dst'])
            fileSuccessfullyLoaded = slicer.util.loadNodeFromFile(downloadFiles['hdr']['dst'], t)



            
        #-------------------- 
        # Try to load the img file second, if it exists.
        #-------------------- 
        else:
            t = coreIoManager.fileType(downloadFiles['img']['dst'])
            fileSuccessfullyLoaded = slicer.util.loadNodeFromFile(downloadFiles['img']['dst'], t)

            

        #-------------------- 
        # If the load was successful, update the
        # session args...
        #-------------------- 
        if fileSuccessfullyLoaded: 
            sessionArgs = XnatSessionArgs(MODULE = self.MODULE, srcPath = self.xnatSrc)
            sessionArgs['sessionType'] = "scene download"
            self.MODULE.XnatView.startNewSession(sessionArgs)
            print ("'%s' successfully loaded."%(os.path.basename(self.localDst))) 



        #-------------------- 
        # Otherwise kick back error.
        #-------------------- 
        else: 
            errStr = "Could not load '%s'!"%(os.path.basename(self.localDst))
            print (errStr)
            #qt.QMessageBox.warning( None, "Load Failed", errStr) 


            
        #-------------------- 
        # Return the load success.
        #-------------------- 
        return fileSuccessfullyLoaded
