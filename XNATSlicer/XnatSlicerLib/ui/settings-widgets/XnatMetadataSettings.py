from __main__ import vtk, qt, ctk, slicer

import os
import glob
import sys

from XnatSettings import *
from XnatMetadataManager import *



comment = """
XnatMetadataSettings is the XnatSettings pertaining to
the adding and removing custom metadata within a given
XNAT instance.  While the other XnatSettings widgets
allow the user to toggle (check) the type of metadata 
viewable within the tools that display it, this settings
allows the viewer to add and remove specific metadata
pertaining to an xnat level (projects, subjects, 
experiments, files, slicer).

All 'XnatSettings' subclasses
are to be displaed in the 'XnatSettingsWindow' class.

TODO:
"""



        
class XnatMetadataSettings(XnatSettings):
    """ Descriptor above.
    """

  
    def __init__(self, title, MODULE):
        """ Init function.
        """
        
        #--------------------
        # Call parent init
        #--------------------
        super(XnatMetadataSettings, self).__init__(title, MODULE)

        
        #--------------------
        # Add the metadata manager.
        #--------------------
        self.createMetadataManagers('main')
        self.masterLayout.addWidget(self.XnatMetadataManagers['main'])
        
        #
        # We hide these because the edit buttons in the other
        # settings widgets will lead to the XnatMetadataSettings
        #
        self.XnatMetadataManagers['main'].setEditButtonsVisible(False)
        for key, manager in self.XnatMetadataManagers.iteritems():
            manager.setItemType('label')



        #--------------------
        # Call parent 'complete.'
        #--------------------
        self.complete()


            

            


        








     
