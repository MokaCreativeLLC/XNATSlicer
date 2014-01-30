# external
from Xnat import *

# module 
from MetadataEditor import *

class MetadataEditor_Default(MetadataEditor):
    """ Metadata edtior for default XnatMetadata as
        defined in XnatGlobals.  
    """
    
    def setup(self):
        """ Add metadata items to the list widget of default
            (label) type.
        """
        self.listWidget.addItemsByType(
            [tag for tag in Xnat.metadata.DEFAULT_TAGS[self.xnatLevel]])



