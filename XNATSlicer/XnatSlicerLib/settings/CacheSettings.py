from __main__ import vtk, qt, ctk, slicer

import os
import glob
import sys

from XnatSlicerGlobals import *
from XnatSlicerUtils import *
from Settings import *
from MetadataManager import *


        
class CacheSettings(Settings):
    """
    """
  
    USE_CACHED_IMAGES_TAG = 'useCachedImages'
    def __init__(self, title, MODULE):
        """
        """
        
        
        #--------------------
        # Call parent init
        #--------------------
        super(CacheSettings, self).__init__(title, MODULE)


        #--------------------
        # Add the metadata Manager
        #--------------------        
        self.addUsedCachedImages()
        self.complete()


        xnatHost = self.MODULE.LoginMenu.hostDropdown.currentText
        useCachedSetting = self.MODULE.SettingsFile.getSetting(xnatHost, 
                                                              CacheSettings.USE_CACHED_IMAGES_TAG)


        #--------------------
        # Add the metadata Manager
        #--------------------            
        if len(useCachedSetting) > 0:
            self.useCachedImages.setCheckState(2 if 'True' in useCachedSetting[0] else 0)

        else:
            self.useCachedImages.setCheckState(2)
            self.useCachedImagesToggled()

    
        


    def addUsedCachedImages(self):
        """ 
        As stated.
        """ 

        #self.useCachedImagesLayout = qt.QHBoxLayout()

        self.useCachedImages = qt.QCheckBox("Use cached images (DICOM, Analyze, etc.)")
        self.masterLayout.addWidget(self.useCachedImages)
        self.useCachedImages.connect('clicked()', self.useCachedImagesToggled)




    def useCachedImagesToggled(self):
        """
        """
        #print "USE CHACED TOGGLED", str(self.useCachedImages.isChecked())
        xnatHost = self.MODULE.LoginMenu.hostDropdown.currentText
        self.MODULE.SettingsFile.setSetting(xnatHost, {CacheSettings.USE_CACHED_IMAGES_TAG: str(self.useCachedImages.isChecked())})
