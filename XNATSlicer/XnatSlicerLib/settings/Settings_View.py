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




    
