# application
from __main__ import qt

# module
from XnatSlicerGlobals import *
from XnatSlicerUtils import *
from Settings import *
from MetadataEditorSet import *



        
class Settings_Cache(Settings):
    """
    Manages settings related to cached images.
    """

    USE_CACHED_IMAGES_TAG = 'useCachedImages'
    EVENT_TYPES = [
        'USECACHECHECKED'
    ]
    
    def getStorageTag(self):
        """
        Returns the storage tag pertaining to the settings/

        @return: The storage tag
        @rtype: str
        """
        return super(Settings_Cache, self).\
                  getStorageTag(self.USE_CACHED_IMAGES_TAG)




    def setup(self):
        """
        Setup function inherited from parent class.
            -Adds a checkbox and its relevant callbacks to the widget.
        """        
        self.checkBox = \
            qt.QCheckBox("Use cached images (DICOM, Analyze, etc.)")

        self.checkBox.connect('clicked()', self.__syncFileTo)

        self.__constructDefaults()

        self.addSyncCallback_ToFile(self.getStorageTag(), self.__syncToFile)
        self.addSyncCallback_FileTo(self.getStorageTag(), self.__syncFileTo)

        self.masterLayout.addWidget(self.checkBox)
        self.masterLayout.addStretch()




    def __constructDefaults(self):
        """
        Applies the default structure for the 'Use Cache' checkbox (default
        is true).
        """
        self.DEFAULTS[self.getStorageTag()] = True




    def __syncToFile(self):
        """
        Method specific to syncing the Setting to the SettingsFile.
        """
    
        useCachedSetting = self.SettingsFile.getSetting(self.currXnatHost, 
                                                        self.getStorageTag())
        self.checkBox.setCheckState(2 if 'True' in \
                                           useCachedSetting[0] else 0)
        self.updateUI()
    




    def __syncFileTo(self):
        """
        Method specific to syncing the SettingsFile to the Setting.
        """
        self.SettingsFile.setSetting(self.currXnatHost, 
        {self.getStorageTag(): str(self.checkBox.isChecked())})
