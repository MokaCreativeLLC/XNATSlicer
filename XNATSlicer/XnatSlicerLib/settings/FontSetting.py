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
    EVENT_TYPES = ['FONTSIZECHANGED']

    def createFontSizeDropdown(self, title = "Font Size:" ):
        """ 
        Adds a fontSize dropdown to the layout
        of the XnatSetting.  The subclass then
        needs to specify how to connect the events
        of the dropdown.

        @param title: The title of the dropdown.
        @type title: str
        """
        
        self.EVENT_TYPES = list(set(FontSetting.EVENT_TYPES + 
                                    self.EVENT_TYPES))


        if not hasattr(self, 'fontDropdowns'):
            self.fontDropdowns = {}


        #--------------------
        # Derive the title.
        #--------------------
        ccTitle = MokaUtils.string.toCamelCase(title)


        #--------------------
        # Derive the storage.
        #--------------------
        if not ccTitle in self.fontDropdowns:
            self.fontDropdowns[ccTitle] = []
        

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
        self.addSyncMethod_ToFile(ccTitle, self.__syncToFile)
        self.addSyncMethod_FileTo(ccTitle, self.__syncFileTo)


        #--------------------
        # Defaults
        #--------------------
        self.__constructDefaults(ccTitle)


        #--------------------
        # Add to UI and store
        #--------------------
        self.addSection(title, comboBox)
        self.fontDropdowns[ccTitle].append(comboBox)




    def __constructDefaults(self, section):
        """
        @param section: The section for reference in the defaults dict.
        @type section: str
        """
        self.DEFAULTS[section] = {}
        self.DEFAULTS[section]= XnatSlicerGlobals.FONT_SIZE



          
    def __onFontSizeChanged(size):
        """
        """
        try:
            self.Events.runEventCallbacks('FONTSIZECHANGED', size)
            self.__syncFileTo()
        except Exception, e:
            pass




    def __syncFileTo(self):
        """
        """
        for key, dropdown in self.fontDropdowns.iteritems():
            fontSize = self.SettingsFile.setSetting(self.currXnatHost, 
                                    {key : dropdown.currentText()})

            

    def __syncToFile(self):
        """
        """
        for key, dropdownList in self.fontDropdowns.iteritems():
            fontSize = self.SettingsFile.getSetting(self.currXnatHost, 
                                                    key)
            for dropdown in dropdownList:
                dropdown.setCurrentIndex(dropdown.findText(str(fontSize[0])))
