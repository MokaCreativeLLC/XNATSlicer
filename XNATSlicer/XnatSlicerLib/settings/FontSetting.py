# application
from __main__ import qt

# external
from MokaUtils import *


    
class FontSetting(object):
    """ 
    FontSetting is a parent class that is inherited by any Setting class that
    aims to make use of a font dropdown.  It creates and manages the various
    events related to this widget.
    """
    FONT_SIZE = 10
    MAX_FONT_SIZE = 8
    MIN_FONT_SIZE = 21

    def createFontSizeDropdown(self, title = "Font Size:" ):
        """ 
        Adds a fontSize dropdown to the layout of the XnatSetting.  The 
        subclass then needs to specify how to connect the events of the 
        dropdown.

        @param title: The title of the dropdown.
        @type title: str
        """

        if not hasattr(self, 'fontDropdowns'):
            self.fontDropdowns = {}

        fontStorageTag = self.getFontStorageTag(title)

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
        Makes the FontStorage tag for retreiving data from the SettingsFile.

        @param string: The string to derive the tag from.
        @type string: str

        @return: The font storage tag constructed from the argument.
        @rtype: str
        """
        return MokaUtils.string.toCamelCase(self.__class__.__name__ + string)




    def __constructDefaults(self, section):
        """
        Assigns the DEFAULT value to the font dropdown pertaining to 'section'.

        @param section: The section for reference in the defaults dict.
        @type section: str
        """
        self.DEFAULTS[section] = {}
        self.DEFAULTS[section]= FontSetting.FONT_SIZE




    def getStoredFont(self, tag):
        """
        Gets the stored font based on the storage tag.

        @param tag: The tag to construct the storage tag from.
        @type tag: str

        @return: The stored setting for the font.
        @rtype: str
        """
        if not self.currXnatHost:
            return []
        return self.SettingsFile.getSetting(self.currXnatHost, 
                                            self.getFontStorageTag(tag))
        
        

          
    def __onFontSizeChanged(self, size):
        """
        Callback for the font dropdown change event.

        @param size: Dummy argument for the dropdown change event.
        @type size: str
        """
        #MokaUtils.debug.lf()
        # Store in settings file
        self.__syncFileTo()
        # Run callbacks.
        self.Events.runEventCallbacks('SETTINGS_FILE_MODIFIED', 
                                      'FONT_SIZE_CHANGED')
        



    def __syncFileTo(self):
        """
        Syncs the SettingsFile to the current value on the dropdown.
        """
        for key, dropdownList in self.fontDropdowns.iteritems():
            for dropdown in dropdownList:
                fontSize = self.SettingsFile.setSetting(self.currXnatHost, 
                                           {key : dropdown.currentText})

            

    def __syncToFile(self):
        """
        Syncs the dropdown to stored value in the SettingsFile.
        """
        for key, dropdownList in self.fontDropdowns.iteritems():
            fontSize = self.SettingsFile.getSetting(self.currXnatHost, 
                                                    key)
            for dropdown in dropdownList:
                dropdown.setCurrentIndex(dropdown.findText(str(fontSize[0])))
