from XnatSlicerUtils import *
from XnatSlicerUtils import *
from Loader import *



comment = """
Loader_File contains the specific load method for single-file
(non-Slicer scene) downloads from an XNAT host into Slicer.

TODO:
"""



class Loader_File(Loader):
        
    def __init__(self, MODULE, _src, fileUris):
        super(Loader_File, self).__init__(MODULE, _src, fileUris)
        self.setFileSrcDst()


        
    
    def load(self):
        """ 
        """
        if not Loader.load(self): return 
        SlicerUtils.loadNodeFromFile(self._dst)

