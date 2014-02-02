# external
from Xnat import *
from MokaUtils import *

# module
from XnatSlicerGlobals import *
from MetadataEditorSet import *



    
class FontSetting(object):
    """ 
    """

    MAX_FONT_SIZE = 8
    MIN_FONT_SIZE = 21

    def createFontSizeDropdown(self, title = "Font Size:" ):
        """ 
        Adds a fontSize dropdown to the layout
        of the XnatSetting.  The subclass then
        needs to specify how to connect the events
        of the dropdown.

        @param title: The title of the dropdown.
        @type title: str
        """
        

        fontStorageTag = self.getFontStorageTag(title)


        if not hasattr(self, 'fontDropdowns'):
            self.fontDropdowns = {}


        #--------------------
        # Derive the storage.
        #--------------------
        if not fontStorageTag in self.fontDropdowns:
            self.fontDropdowns[fontStorageTag] = []
        

        #--------------------
        # Create the object
        #--------------------
        comboBox = qt.QComboBox()
        comboBox.addItems([str(i) \
                        for i in range(self.MAX_FONT_SIZE, \
                                       self.MIN_FONT_SIZE)])
        comboBox.setFixedWidth(100)
            


        #--------------------
        # Callbacks
        #--------------------
        comboBox.connect('currentIndexChanged(const QString&)', 
                         self.__onFontSizeChanged)


        #--------------------
        # Add sync methods
        #--------------------
        self.addSyncCallback_ToFile(fontStorageTag, self.__syncToFile)
        self.addSyncCallback_FileTo(fontStorageTag, self.__syncFileTo)


        #--------------------
        # Defaults
        #--------------------
        self.__constructDefaults(fontStorageTag)


        #--------------------
        # Add to UI and store
        #--------------------
        self.addSection(title, comboBox)
        self.fontDropdowns[fontStorageTag].append(comboBox)




    def getFontStorageTag(self, string):
        """
        """
        return MokaUtils.string.toCamelCase(string)




    def __constructDefaults(self, section):
        """
        @param section: The section for reference in the defaults dict.
        @type section: str
        """
        self.DEFAULTS[section] = {}
        self.DEFAULTS[section]= XnatSlicerGlobals.FONT_SIZE




    def getStoredFont(self, key):
        """
        """
        return self.SettingsFile.getSetting(self.currXnatHost, 
                                            self.getFontStorageTag(key))
        
        
          
    def __onFontSizeChanged(self, size):
        """
        """
        #print " FONT SIZE CHANGED!"
        self.__syncFileTo()
        #MokaUtils.debug.lf()
        self.Events.runEventCallbacks('SETTINGS_FILE_MODIFIED', 
                                      'FONT_SIZE_CHANGED')
        



    def __syncFileTo(self):
        """
        """
        for key, dropdownList in self.fontDropdowns.iteritems():
            for dropdown in dropdownList:
                fontSize = self.SettingsFile.setSetting(self.currXnatHost, 
                                           {key : dropdown.currentText})

            

    def __syncToFile(self):
        """
        """
        for key, dropdownList in self.fontDropdowns.iteritems():
            fontSize = self.SettingsFile.getSetting(self.currXnatHost, 
                                                    key)
            for dropdown in dropdownList:
                dropdown.setCurrentIndex(dropdown.findText(str(fontSize[0])))
