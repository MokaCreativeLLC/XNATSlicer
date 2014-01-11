from XnatSlicerGlobals import *
from __main__ import vtk, qt, ctk, slicer

import os
import glob
import sys


from Xnat import XnatGlobals
from Settings import *
from MetadataManager import *



    
class DetailsSettings(Settings):
    """ 
    DetailsSettings is the Settings pertaining to
    the 'NodeDetails' class.  This class specifically
    deals with toggling the visible metadata key-value pairs
    in the 'NodeDetails' window when a user clicks on a 
    note in the View, and the subsequent saving of these
    settings into the SettingsFile..
    
    All 'Settings' subclasses
    are to bge displaed in the 'SettingsWindow' class.
    """
  
    FONT_SIZE_TAG = "DetailsFontSize"



    def __init__(self, title, MODULE):
        """ Init function.
        """
        
        #--------------------
        # Call parent init
        #--------------------
        super(DetailsSettings, self).__init__(title, MODULE)



        #--------------------
        # Add the fontSizeDropdown
        #--------------------
        self.addFontSizeDropdown()
        self.addSpacing()


        
        #--------------------
        # Create the metadata managers and their labels.
        #--------------------
        self.createMetadataManagers('main') 
        self.addSection("Details View Metadata", self.MetadataManagers['main'])


        
        #--------------------
        # Set the default selected metadata.
        #--------------------
        self.setDefaultSelectedMetadata('main',  XnatGlobals.DEFAULT_METADATA)



        #--------------------
        # Hide the custom add-remove components within the 
        # metadata manager.  Set all of the metadata manager
        # iems to 'checkbox' as all the user can do is
        # toggle the metadata to be displayed.
        #--------------------
        for key, manager in self.MetadataManagers.iteritems():
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
        super(DetailsSettings, self).addFontSizeDropdown(title)


        
        #--------------------
        # See if there's a stored font in the 
        # settings file first.
        #-------------------- 
        xnatHost = self.MODULE.LoginMenu.hostDropdown.currentText
        font = self.MODULE.SettingsFile.getSetting(xnatHost, DetailsSettings.FONT_SIZE_TAG)



        #--------------------
        # If there are NO stored fonts, get the default font size
        # from XnatGlobals and save it to the settings file. 
        # This will be stored as 'currSize'.
        #--------------------
        if len(font) == 0:
            currSize = XnatSlicerGlobals.FONT_SIZE
            self.MODULE.SettingsFile.setSetting(xnatHost, {DetailsSettings.FONT_SIZE_TAG: [str(currSize)]})


            
        #--------------------
        # If there is a stored font, retrieve at
        # and set 'currSize' accordingly.
        #--------------------
        else:
            currSize = font[0]



        #--------------------
        # Define function that changes the font size
        # of the NodeDetails object when the dropdown
        # changes.
        #--------------------            
        def changeFontSize(size):
            try:
                self.MODULE.NodeDetails.changeFontSize(int(size))
                self.MODULE.SettingsFile.setSetting(xnatHost, {DetailsSettings.FONT_SIZE_TAG: [str(size)]})
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
