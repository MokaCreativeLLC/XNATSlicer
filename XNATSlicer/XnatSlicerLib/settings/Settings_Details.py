# external
from Xnat import *

# module
from Settings import *
from FontSetting import *
from MetadataEditorSetting import *
from XnatSlicerGlobals import *
from XnatSlicerGlobals import *



    
class Settings_Details(FontSetting, 
                       MetadataEditorSetting, Settings):
    """ 
    Settings_Details is the Settings pertaining to
    the 'NodeDetails' class.  This class specifically
    deals with toggling the visible metadata key-value pairs
    in the 'NodeDetails' window when a user clicks on a 
    note in the View, and the subsequent saving of these
    settings into the SettingsFile..
    
    All 'Settings' subclasses
    are to bge displaed in the 'SettingsWindow' class.
    """

    
    def setup(self):
        """
        """
        #--------------------
        # Add the fontSizeDropdown
        #--------------------
        self.createFontSizeDropdown('Details Font Size')
        
        self.addSpacing()

        #--------------------
        # Create the metadata managers and their labels.
        #--------------------
        self.createMetadataEditorSets('Details Metadata', 
                                      itemType = 'checkbox', 
                                      editVisible = True,
                                      customEditVisible = False) 
