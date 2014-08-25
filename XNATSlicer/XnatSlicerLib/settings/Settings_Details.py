__author__ = "Sunil Kumar (kumar.sunil.p@gmail.com)"
__copyright__ = "Copyright 2014, Washington University in St. Louis"
__credits__ = ["Sunil Kumar", "Steve Pieper", "Dan Marcus"]
__license__ = "XNAT Software License Agreement " + \
              "(see: http://xnat.org/about/license.php)"
__version__ = "2.1.1"
__maintainer__ = "Rick Herrick"
__email__ = "herrickr@mir.wustl.edu"
__status__ = "Production"


# python
from collections import OrderedDict

# external
from Xnat import *

# module
from Settings import *
from FontSetting import *
from MetadataEditorSetting import *
from CheckBoxSetting import *


    
class Settings_Details(FontSetting, MetadataEditorSetting, CheckBoxSetting, 
                       Settings):
    """ 
    Settings_Details is the Settings pertaining to the 'NodeDetails' class. 
    """

    LABEL_FONT_SIZE = 'Font Size' 
    LABEL_METADATA = 'Metadata' 
    CHECKBOXES = OrderedDict([
        ('empty', {
            'tag': 'showEmptyMetadata',
            'desc': 'Display metadata with empty values.',
            'checked': True,
            'event': 'SHOWEMPTY'
        })
    ])



    def setup(self):
        """
        Method inherited from parent function.
        """
        self.addSection('Display')
        self.createCheckBoxes()
        self.addSpacing()
        self.addSpacing()
        self.createFontSizeDropdown(self.LABEL_FONT_SIZE)
        self.addSpacing()
        self.createMetadataEditorSets(self.LABEL_METADATA, 
                                      itemType = 'checkbox', 
                                      editVisible = True,
                                      customEditVisible = False) 








        
