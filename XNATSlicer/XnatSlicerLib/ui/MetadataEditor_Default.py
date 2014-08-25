__author__ = "Sunil Kumar (kumar.sunil.p@gmail.com)"
__copyright__ = "Copyright 2014, Washington University in St. Louis"
__credits__ = ["Sunil Kumar", "Steve Pieper", "Dan Marcus"]
__license__ = "XNAT Software License Agreement " + \
              "(see: http://xnat.org/about/license.php)"
__version__ = "2.1.1"
__maintainer__ = "Rick Herrick"
__email__ = "herrickr@mir.wustl.edu"
__status__ = "Production"


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



