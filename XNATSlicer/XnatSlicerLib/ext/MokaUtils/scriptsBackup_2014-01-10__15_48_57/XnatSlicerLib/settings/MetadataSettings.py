from __main__ import vtk, qt, ctk, slicer

import os
import glob
import sys

from Settings import *
from MetadataManager import *



        
class MetadataSettings(Settings):
    """
    MetadataSettings is the Settings pertaining to
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

  
    def __init__(self, title, MODULE):
        """ 
        Init function.
        """
        
        #--------------------
        # Call parent init
        #--------------------
        super(MetadataSettings, self).__init__(title, MODULE)

        
        #--------------------
        # Add the metadata manager.
        #--------------------
        self.createMetadataManagers('main')
        self.masterLayout.addWidget(self.MetadataManagers['main'])
        
        #
        # We hide these because the edit buttons in the other
        # settings widgets will lead to the MetadataSettings
        #
        self.MetadataManagers['main'].setEditButtonsVisible(False)
        for key, manager in self.MetadataManagers.iteritems():
            manager.setItemType('label')



        #--------------------
        # Call parent 'complete.'
        #--------------------
        self.complete()


            

            


        








     
