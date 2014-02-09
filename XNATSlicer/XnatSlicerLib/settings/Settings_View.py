# application
from __main__ import qt

# module
from Settings import *
from FontSetting import *
from MetadataEditorSetting import *
from XnatSlicerUtils import *



        
class Settings_View(FontSetting, MetadataEditorSetting, Settings):
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
  
    LABEL_FONT = qt.QFont('Arial', 10, 10, False) 
    LABEL_FONT_SIZE = 'View Font Size' 
    LABEL_METADATA = 'Info. Column Metadata'
    DEFAULT_METADATA = Xnat.metadata.DEFAULT_TAGS_LITE 
    EVENT_TYPES = [
        'FILTERTOGGLED',
    ]



    def setup(self):
        """
        As stated.
        """
        #--------------------
        # Add Sort Buttons section
        #--------------------
        self.__addSortAndFilterButtons()
        self.addSpacing()



        self.createFontSizeDropdown(Settings_View.LABEL_FONT_SIZE)
        self.addSpacing()


        #--------------------
        # Create the metadata manager type.
        #--------------------        
        self.createMetadataEditorSets(Settings_View.LABEL_METADATA, 
                                      itemType = 'checkbox', 
                                      editVisible = True,
                                      customEditVisible = False) 



    def __onFilterButtonClicked(self):
        """
        Callback for when a filter button is clicked.
        """
        MokaUtils.debug.lf("filter clicked!")
        self.Events.runEventCallbacks('FILTERTOGGLED')
        


            

    def __addSortAndFilterButtons(self):
        """  
        Adds the sort/filter buttons to the settings widgets and connects 
        their click events accordingly.
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
           font = Settings_View.LABEL_FONT,
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
