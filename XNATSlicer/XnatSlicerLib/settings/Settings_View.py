# application
from __main__ import qt

# module
from Settings import *
from FontSetting import *
from MetadataEditorSetting import *
from XnatSlicerGlobals import *
from XnatSlicerUtils import *



        
class Settings_View(FontSetting, 
                    MetadataEditorSetting, Settings):
    """ 
    Descriptor above.
    Settings_View is the Settings pertaining to
    the 'View_Tree' class.  This class specifically
    deals with the following:
    
    1) Toggling the visible metadata key-value pairs
    in the 'Info' column of the View and saving this
    in the SettingsFile.

    2) Setting the font size of the tree view.
    
    3) Filtering the tree view nodes by column values
    (LastAccessed).
    
    
    All 'Settings' subclasses
    are to be displaed in the 'SettingsWindow' class.
    """
  
    LABEL_FONT_SIZE = 'View Font Size' 
    LABEL_METADATA = 'Info. Column Metadata'
    DEFAULT_METADATA = Xnat.metadata.DEFAULT_TAGS_LITE 
    EVENT_TYPES = [
        'FILTERTOGGLED',
    ]



    def setup(self):
        """
        """
        #--------------------
        # Add Sort Buttons section
        #--------------------
        self.addSortAndFilterButtons()
        self.addSpacing()



        self.createFontSizeDropdown(self.LABEL_FONT_SIZE)
        self.addSpacing()


        #--------------------
        # Create the metadata manager type.
        #--------------------        
        self.createMetadataEditorSets(self.LABEL_METADATA, 
                                      itemType = 'checkbox', 
                                      editVisible = True,
                                      customEditVisible = False) 


 
        
      
    def setButtonDown(self, category = None, name = None, 
                      isDown = True, callSignals = True):
        """ 
        Programmatically sets a button down based on
        the arguments.  The user has the option to allow for
        the 'clicked()' signals to be called or not.  
        This is used primarily for default programmatic 
        manipulation of the buttons, such as loadProjects() in 
        XNATView, where default filters are applied, but
        the signals of clicking are not desired, but 
        self.currentlyToggledFilterButton is still tracked.
        """
        if isDown and category == 'sort':
            self.buttons[category][name].setChecked(True)
            self.currentlyToggledFilterButton = self.buttons['sort'][name]   

            


    def __onFilterButtonClicked(self):
        """
        """
        MokaUtils.debug.lf("filter clicked!")
        self.Events.runEventCallbacks('FILTERTOGGLED')
        


            

    def addSortAndFilterButtons(self):
        """  Adds the sort/filter buttons
             to the settings widgets and
             connects their click events accordingly.
        """
        
        #--------------------
        # Create buttons
        #--------------------
        self.buttons = {}
        self.buttons['sort'] = {}
        self.buttons['sort'] = {'accessed': \
           XnatSlicerUtils.generateButton(iconOrLabel = 'Last Accessed', 
           toolTip = "Sort projects, prioritizing those " + 
                                          "accessed by current user.", 
           font = XnatSlicerGlobals.LABEL_FONT,
           size = qt.QSize(90, 20), 
           enabled = True)}
      
        self.buttons['sort']['accessed'].setCheckable(True)
        self.buttons['sort']['accessed'].setChecked(False)


        



        #--------------------
        # Connect the filter button to
        # the button click.
        #--------------------
        self.buttons['sort']['accessed'].connect('toggled(bool)', 
                                                 self.__onFilterButtonClicked)



        #--------------------
        # Make the button layout
        #--------------------
        self.sortButtonLayout = qt.QHBoxLayout()
        for key, value in self.buttons['sort'].iteritems():
            self.sortButtonLayout.addWidget(value)
        self.sortButtonLayout.addStretch()


        #--------------------
        # Create a "Filter Projects By" section.
        #--------------------
        self.addSection("Filter Projects By:", self.sortButtonLayout)
