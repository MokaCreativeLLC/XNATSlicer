# external
from Xnat import *

# module 
from MetadataEditor import *



class MetadataEditor_Default(MetadataEditor):
    """ 
    Metadata edtior for default XNAT Metadata.  
    """
    
    def setup(self):
        """ 
        Add metadata items to the list widget.
        """
        self.listWidget.addItemsByType(
            [tag for tag in Xnat.metadata.DEFAULT_TAGS[self.xnatLevel]])



