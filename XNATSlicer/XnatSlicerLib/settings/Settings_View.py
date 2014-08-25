__author__ = "Sunil Kumar (kumar.sunil.p@gmail.com)"
__copyright__ = "Copyright 2014, Washington University in St. Louis"
__credits__ = ["Sunil Kumar", "Steve Pieper", "Dan Marcus"]
__license__ = "XNAT Software License Agreement " + \
              "(see: http://xnat.org/about/license.php)"
__version__ = "2.1.1"
__maintainer__ = "Rick Herrick"
__email__ = "herrickr@mir.wustl.edu"
__status__ = "Production"


# application
from __main__ import qt

# module
from Settings import *
from FontSetting import *
from MetadataEditorSetting import *
from CheckBoxSetting import *
from XnatSlicerUtils import *



        
class Settings_View(FontSetting, MetadataEditorSetting, CheckBoxSetting,
                    Settings):
    """ 
    Settings_View is the Settings pertaining to
    the 'View_Tree' class. 
    """
  
    LABEL_FONT = qt.QFont('Arial', 10, 10, False) 
    LABEL_FONT_SIZE = 'Font Size' 
    LABEL_METADATA = 'Info. Metadata'
    DEFAULT_METADATA = Xnat.metadata.DEFAULT_TAGS_LITE 
    CHECKBOXES = OrderedDict([
        ('lastAccessed', {
            'tag': 'showLastAccessedOnly',
            'desc': 'Show only accessed projects.',
            'checked': False,
            'event': 'FILTERTOGGLED'
        })
    ])



    def setup(self):
        """
        As stated.
        """
        self.addSection('Filters')
        self.createCheckBoxes()
        self.addSpacing()
        self.addSpacing()
        self.createFontSizeDropdown(Settings_View.LABEL_FONT_SIZE)
        self.addSpacing()      
        self.createMetadataEditorSets(Settings_View.LABEL_METADATA, 
                                      itemType = 'checkbox', 
                                      editVisible = True,
                                      customEditVisible = False) 




    
