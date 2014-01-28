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

        
        #--------------------
        # Add the metadata manager.
        #--------------------
        self.createMetadataEditorSets('main')
        self.masterLayout.addWidget(self.MetadataEditorSets['main'])
        
        #
        # We hide these because the edit buttons in the other
        # settings widgets will lead to the Settings_Metadata
        #
        self.MetadataEditorSets['main'].setEditButtonsVisible(False)
        for key, manager in self.MetadataEditorSets.iteritems():
            manager.setItemType('label')



        #--------------------
        # Call parent 'complete.'
        #--------------------
        self.complete()


            

            


        








     
