from XnatUtils import *
from XnatLoader import *



comment = """
XnatLoader_File contains the specific load method for single-file
(non-Slicer scene) downloads from an XNAT host into Slicer.

TODO:
"""



class XnatLoader_File(XnatLoader):
        
    def __init__(self, MODULE, _src, fileUris):
        super(XnatLoader_File, self).__init__(MODULE, _src, fileUris)
        self.setFileSrcDst()


        
    
    def load(self):
        """ 
        """
        if not XnatLoader.load(self): return 
        XnatUtils.loadNodeFromFile(self._dst)

