from __main__ import vtk, qt, ctk, slicer

import os
import glob
import sys

from XnatSettings import *
from XnatMetadataManager import *




comment = """
XnatDetailsSettings is the XnatSettings pertaining to
the 'XnatNodeDetails' class.  This class specifically
deals with toggling the visible metadata key-value pairs
in the 'XnatNodeDetails' window when a user clicks on a 
note in the XnatView, and the subsequent saving of these
settings into the XnatSettingsFile..

All 'XnatSettings' subclasses
are to be displaed in the 'XnatSettingsWindow' class.

TODO:
"""




#--------------------
# Define the visible metadata tags for storing info 
# the settings file.
#--------------------
visibleMetadataTags = {'projects': '', 'subjects' : '', 'experiments' : '', 'scans' :'', 'files' : '', 'slicer': ''}
for key in visibleMetadataTags:
    visibleMetadataTags[key] = 'visibleMetadataTags_' + key



    
class XnatDetailsSettings(XnatSettings):
    """ Descriptor above.
    """
  
    def __init__(self, title, MODULE):
        """ Init function.
        """
        
        #--------------------
        # Call parent init
        #--------------------
        super(XnatDetailsSettings, self).__init__(title, MODULE)



        #--------------------
        # Add the fontSizeDropdown
        #--------------------
        self.addFontSizeDropdown()
        self.addSpacing()


        
        #--------------------
        # Create the metadata managers and their labels.
        #--------------------
        self.createMetadataManagers('main') 
        self.addSection("Details View Metadata", self.XnatMetadataManagers['main'])


        
        #--------------------
        # Set the default selected metadata.
        #--------------------
        self.setDefaultSelectedMetadata('main',  self.MODULE.GLOBALS.DEFAULT_XNAT_METADATA)



        #--------------------
        # Hide the custom add-remove components within the 
        # metadata manager.  Set all of the metadata manager
        # iems to 'checkbox' as all the user can do is
        # toggle the metadata to be displayed.
        #--------------------
        for key, manager in self.XnatMetadataManagers.iteritems():
            manager.setCustomEditVisible(False)
            manager.setItemType('checkbox')




        #--------------------
        # Call the 'complete' function.  Necessary
        # for the layout to update to the content.
        #--------------------           
        self.complete()


        

    def addFontSizeDropdown(self, title = "Font Size:" ):
        """ As staed.
        """

        #--------------------
        # Call parent 'addFontSizeDropdown'
        #--------------------
        super(XnatDetailsSettings, self).addFontSizeDropdown(title)


        
        #--------------------
        # Define the 'fontSizeTag'.
        #--------------------
        self.fontSizeTag = "DetailsFontSize"


        
        #--------------------
        # See if there's a stored font in the 
        # settings file first.
        #-------------------- 
        xnatHost = self.MODULE.XnatLoginMenu.hostDropdown.currentText
        font = self.MODULE.XnatSettingsFile.getTagValues(xnatHost, self.fontSizeTag)



        #--------------------
        # If there are NO stored fonts, get the default font size
        # from XnatGlobals and save it to the settings file. 
        # This will be stored as 'currSize'.
        #--------------------
        if len(font) == 0:
            currSize = self.MODULE.GLOBALS.FONT_SIZE
            self.MODULE.XnatSettingsFile.setTagValues(xnatHost, {self.fontSizeTag: [str(currSize)]})


            
        #--------------------
        # If there is a stored font, retrieve at
        # and set 'currSize' accordingly.
        #--------------------
        else:
            currSize = font[0]



        #--------------------
        # Define function that changes the font size
        # of the XnatNodeDetails object when the dropdown
        # changes.
        #--------------------            
        def changeFontSize(size):
            try:
                self.MODULE.XnatNodeDetails.changeFontSize(int(size))
                self.MODULE.XnatSettingsFile.setTagValues(xnatHost, {self.fontSizeTag: [str(size)]})
            except Exception, e:
                pass


            
        #--------------------
        # Connect dropdown change event to the above function.
        #--------------------        
        currDropdown = self.fontDropdowns[-1]
        currDropdown.connect('currentIndexChanged(const QString&)', changeFontSize)

        

        #--------------------
        # Set dropdown's index to the 'currSize'
        #--------------------         
        currDropdown.setCurrentIndex(currDropdown.findText(currSize))
