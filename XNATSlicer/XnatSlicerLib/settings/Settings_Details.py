# external
from Xnat import *

# module
from Settings import *
from XnatSlicerGlobals import *



    
class Settings_Details(Settings):
    """ 
    Settings_Details is the Settings pertaining to
    the 'NodeDetails' class.  This class specifically
    deals with toggling the visible metadata key-value pairs
    in the 'NodeDetails' window when a user clicks on a 
    note in the View, and the subsequent saving of these
    settings into the SettingsFile..
    
    All 'Settings' subclasses
    are to bge displaed in the 'SettingsWindow' class.
    """
  
    FONT_SIZE_TAG = "DetailsFontSize"

    EVENT_TYPES = [
        'FONTSIZECHANGED',
    ]

    DEFAULT_SELECTED_METADATA = {}
    DEFAULT_SELECTED_METADATA['main'] = Xnat.metadata.DEFAULT_TAGS

    def syncWithSettingsFile(self):
        """
        """

        #--------------------
        # Add the fontSizeDropdown
        #--------------------
        self.addFontSizeDropdown()
        self.addSpacing()


        
        #--------------------
        # Create the metadata managers and their labels.
        #--------------------
        self.createMetadataEditorSets('main') 
        self.addSection("Details View Metadata", self.MetadataEditorSets['main'])



        #--------------------
        # Set the default selected metadata.
        #--------------------
        self.applyDefaultsIfNeeded(self.DEFAULT_SELECTED_METADATA)



        #--------------------
        # Hide the custom add-remove components within the 
        # metadata manager.  Set all of the metadata manager
        # iems to 'checkbox' as all the user can do is
        # toggle the metadata to be displayed.
        #--------------------
        for key, manager in self.MetadataEditorSets.iteritems():
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
        super(Settings_Details, self).addFontSizeDropdown(title)


        
        #--------------------
        # See if there's a stored font in the 
        # settings file first.
        #-------------------- 
        font = self.SettingsFile.getSetting(self.currXnatHost, Settings_Details.FONT_SIZE_TAG)



        #--------------------
        # If there are NO stored fonts, get the default font size
        # from XnatGlobals and save it to the settings file. 
        # This will be stored as 'currSize'.
        #--------------------
        if len(font) == 0:
            currSize = XnatSlicerGlobals.FONT_SIZE
            self.SettingsFile.setSetting(self.currXnatHost, {Settings_Details.FONT_SIZE_TAG: [str(currSize)]})


            
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
                self.Events.runEventCallbacks('FONTSIZECHANGED', size)
                self.SettingsFile.setSetting(self.currXnatHost, {Settings_Details.FONT_SIZE_TAG: [str(size)]})
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
