from XnatLoadWorkflow import *



comment = """
XnatFileLoadWorkflow contains the specific load method for single-file
(non-Slicer scene) downloads from an XNAT host into Slicer.

TODO:
"""



class XnatFileLoadWorkflow(XnatLoadWorkflow):
        
    def setup(self):
        pass



    
    def load(self, args):
        """ Downloads a file from an XNAT host, then attempts to load it
            via the Slicer API's 'loadNodeFromFile' method, which returns
            True or False if the load was successful.
        """

        #--------------------    
        # Call parent 'load' method.
        #-------------------- 
        super(XnatFileLoadWorkflow, self).load(args)


        
        #-------------------- 
        # Get the file from XNAT host.
        #-------------------- 
        self.MODULE.XnatIo.getFile({self.xnatSrc: self.localDst})
        


        #-------------------- 
        # Attempt to open file
        #-------------------- 
        a = slicer.app.coreIOManager()
        t = a.fileType(self.localDst)
        fileSuccessfullyLoaded = slicer.util.loadNodeFromFile(self.localDst, t)



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
            qt.QMessageBox.warning( None, "Load Failed", errStr) 


            
        #-------------------- 
        # Return the load success
        #-------------------- 
        return fileSuccessfullyLoaded
