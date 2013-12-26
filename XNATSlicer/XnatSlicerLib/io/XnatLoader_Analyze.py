from XnatUtils import *
from XnatLoader import *



comment = """
XnatLoader_Analyze contains the specific load methods for analyze 
filetypes (.hdr and .img pairings) to be downloaded from an XNAT host into Slicer.  

TODO:
"""



class XnatLoader_Analyze(XnatLoader):
    """ Class description above.  Inherits from XnatLoader.
    """

    

    def __init__(self, MODULE, _src, fileUris):
        super(XnatLoader_Analyze, self).__init__(MODULE, _src, fileUris)
        self.setZipSrcDst()
    

        
        
    def load(self):
        """ Downloads an analyze file pair (.hdr and .img) from XNAT, 
            then attempts to load it via the Slicer API's 'loadNodeFromFile' 
            method, which returns True or False if the load was successful.
        """
        self.extractDst()
        for fileName in self.extractedFiles:
            XnatUtils.loadNodeFromFile(fileName)



