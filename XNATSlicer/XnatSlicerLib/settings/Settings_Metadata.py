# module
from Settings import *
from MetadataEditorSet import *



        
class Settings_Metadata(Settings):
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
        """
        self.createMetadataEditorSets('main', 'label', False)
        self.masterLayout.addWidget(self.MetadataEditorSets['main'])
        





            

            


        








     
