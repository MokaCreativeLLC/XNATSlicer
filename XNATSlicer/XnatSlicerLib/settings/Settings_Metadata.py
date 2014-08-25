__author__ = "Sunil Kumar (kumar.sunil.p@gmail.com)"
__copyright__ = "Copyright 2014, Washington University in St. Louis"
__credits__ = ["Sunil Kumar", "Steve Pieper", "Dan Marcus"]
__license__ = "XNAT Software License Agreement " + \
              "(see: http://xnat.org/about/license.php)"
__version__ = "2.1.1"
__maintainer__ = "Rick Herrick"
__email__ = "herrickr@mir.wustl.edu"
__status__ = "Production"


# module
from Settings import *
from MetadataEditorSetting import *


        
class Settings_Metadata(MetadataEditorSetting, Settings):
    """
    Settings_Metadata is the Settings pertaining to
    the adding and removing custom metadata within a given
    XNAT instance.  While the other Settings widgets
    allow the user to toggle (check) the type of metadata 
    viewable within the tools that display it, this settings
    allows the viewer to add and remove specific metadata
    pertaining to an xnat level (projects, subjects, 
    experiments, files, slicer).
    
    All 'Settings' subclasses
    are to be displaed in the 'SettingsWindow' class.
    """

  
    def setup(self):
        """
        Adds the metadata editor sets.
        """
        self.createMetadataEditorSets('XNAT Metadata', 
                                      itemType = 'label', 
                                      editVisible = False,
                                      customEditVisible = True) 
        





            

            


        








     
