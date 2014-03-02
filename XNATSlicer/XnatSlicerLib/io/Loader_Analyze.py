# application
from __main__ import slicer

# external
from MokaUtils import *

# module
from SlicerUtils import *
from XnatSlicerUtils import *
from Loader import *




class Loader_Analyze(Loader_Images):
    """ 
    Class description above.  Inherits from Loader_Images.
    Loader_Analyze contains the specific load methods for analyze 
    filetypes (.hdr and .img pairings) to be downloaded from an XNAT host into 
    Slicer.  
    """

        
    def checkCache(self, *args):
        """
        Checks the XNATSlicer cache for the existence of the to-be downloaded
        files.

        @params args: The dummy arguments needed for checking the cache.
        @types: None
        """
        splitter = '/projects/'
     
        abbreviatedUris = [self._src.split(splitter)[1].replace('?format=zip', 
                '') + '/' + 
                    os.path.basename(fileUri) for fileUri in self.fileUris]
        #print "ABBREVIATED URIS", abbreviatedUris
        
        foundCount = 0
        self.cachedFiles = []
        for root, dirs, files in os.walk(self._dst.replace('.zip', '')):
            for f in files:
                if XnatSlicerUtils.isAnalyze(f):
                    #print "\n\nCACHED ANALYZE", os.path.join(root, f), "\n\n",
                    #root, f
                    uri = os.path.join(root, f).replace('\\', '/')
                    #print uri
                    #print uri.split(splitter)[1] in abbreviatedUris
                    if uri.split(splitter)[1] in abbreviatedUris:
                        foundCount +=1
                        self.cachedFiles.append(uri)

        #print "FOUND", foundCount, "URS", len(abbreviatedUris)
        
        if foundCount == len(abbreviatedUris):
            return True

            
        
    def load(self):
        """ 
        Downloads an analyze file pair (.hdr and .img) from XNAT, 
        then attempts to load it via the Slicer API's 'loadNodeFromFile' 
        method, which returns True or False if the load was successful.
        """

        if self.useCached:
            MokaUtils.debug.lf( "\n\nUsing cached analyze files:", 
                                self.extractedFiles, "\n\n")
            
            
        else:
            if not os.path.exists(self._dst): return 
            self.extractDst()
            
        headersFound = 0
        for fileName in self.extractedFiles:
            if fileName.lower().endswith('hdr'):
                SlicerUtils.loadNodeFromFile(fileName)
                #slicer.util.loadVolume(fileName)
                slicer.app.processEvents()
                headersFound += 1

        if headersFound == 0:
            SlicerUtils.loadNodeFromFile(fileName)
            slicer.app.processEvents()   

        



