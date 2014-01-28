# application
from __main__ import qt

# module
from XnatSlicerGlobals import *
from XnatSlicerUtils import *
from Settings import *
from MetadataEditorSet import *


        
class Settings_Cache(Settings):
    """
    """
  
    USE_CACHED_IMAGES_TAG = 'useCachedImages'

    def __init__(self, SettingsFile):
        """
        """
        super(Settings_Cache, self).__init__(SettingsFile)


        #--------------------
        # Add the metadata Manager
        #--------------------        
        self.addUsedCachedImages()
        self.complete()







    def syncWithSettingsFile(self):
        """
        """
        
        useCachedSetting = self.SettingsFile.getSetting(self.currXnatHost, \
           Settings_Cache.USE_CACHED_IMAGES_TAG)

        #--------------------
        # Add the metadata Manager
        #--------------------            
        if len(useCachedSetting) > 0:
            self.useCachedImages.setCheckState(2 if 'True' in \
                useCachedSetting[0] else 0)

        else:
            self.useCachedImages.setCheckState(2)
            self.useCachedImagesToggled()

    
        


    def addUsedCachedImages(self):
        """ 
        As stated.
        """ 

        #self.useCachedImagesLayout = qt.QHBoxLayout()

        self.useCachedImages = \
        qt.QCheckBox("Use cached images (DICOM, Analyze, etc.)")
        self.masterLayout.addWidget(self.useCachedImages)
        self.useCachedImages.connect('clicked()', \
                    self.useCachedImagesToggled)




    def useCachedImagesToggled(self):
        """
        """
        self.SettingsFile.setSetting(self.currXnatHost, 
        {Settings_Cache.USE_CACHED_IMAGES_TAG: \
         str(self.useCachedImages.isChecked())})
