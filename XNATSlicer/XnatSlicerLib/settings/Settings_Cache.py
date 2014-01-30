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
    EVENT_TYPES = [
        'USECACHECHECKED'
    ]
    

    def getStorageTag(self):
        """
        """
        return super(Settings_Cache, self).\
                  getStorageTag(self.USE_CACHED_IMAGES_TAG)



    def setup(self):
        """
        """        
        self.checkBox = \
            qt.QCheckBox("Use cached images (DICOM, Analyze, etc.)")

        self.checkBox.connect('clicked()', self.__syncFileTo)

        self.__constructDefaults()

        self.addSyncMethod_ToFile(self.getStorageTag(), self.__syncToFile)
        self.addSyncMethod_FileTo(self.getStorageTag(), self.__syncFileTo)

        self.masterLayout.addWidget(self.checkBox)




    def __constructDefaults(self):
        """
        @param section: The section for referring to the default.
        @type section: str
        """
        self.DEFAULTS[self.getStorageTag()] = True




    def __syncToFile(self):
        """
        """
    

        useCachedSetting = self.SettingsFile.getSetting(self.currXnatHost, 
                                                        self.getStorageTag())
          
        
        self.checkBox.setCheckState(2 if 'True' in \
                                           useCachedSetting[0] else 0)

        
        self.updateUI()
    




    def __syncFileTo(self):
        """
        """
        self.SettingsFile.setSetting(self.currXnatHost, 
        {self.getStorageTag(): str(self.checkBox.isChecked())})
