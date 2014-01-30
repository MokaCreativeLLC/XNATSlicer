# application
from __main__ import qt

# module
from Settings import *
from XnatSlicerGlobals import *
from XnatSlicerUtils import *



        
class Settings_View_Tree(Settings):
    """ 
    Descriptor above.
    Settings_View_Tree is the Settings pertaining to
    the 'View_Tree' class.  This class specifically
    deals with the following:
    
    1) Toggling the visible metadata key-value pairs
    in the 'Info' column of the View_Tree and saving this
    in the SettingsFile.

    2) Setting the font size of the tree view.
    
    3) Filtering the tree view nodes by column values
    (LastAccessed).
    
    
    All 'Settings' subclasses
    are to be displaed in the 'SettingsWindow' class.
    """

    FONT_SIZE_TAG = "View_TreeFontSize"
  
    EVENT_TYPES = [
        'FONTSIZECHANGED',
        'FILTERTOGGLED',
    ]


    DEFAULT_SETTINGS = {}
    DEFAULT_SETTINGS['info'] = Xnat.metadata.DEFAULT_TAGS_LITE 
        


    def setup(self):
        #--------------------
        # Add Sort Buttons section
        #--------------------
        self.addSortAndFilterButtons()
        self.addSpacing()



        self.addFontSizeDropdown("Tree View Font Size:")
        self.addSpacing()

        #--------------------
        # Create the metadata manager type.
        #--------------------        
        self.createMetadataEditorSets('info')        
        self.addSection("Info. Column Metadata", 
                        self.MetadataEditorSets['info'])

        #--------------------
        # Hide metadataManager's custom edit
        # widgets and make sure it's a checkbox.
        #--------------------  
        for key, manager in self.MetadataEditorSets.iteritems():
            manager.setCustomEditVisible(False)
            manager.setItemType('checkbox')

 
        
      
    def setButtonDown(self, category = None, name = None, 
                      isDown = True, callSignals = True):
          """ Programmatically sets a button down based on
              the arguments.  The user has the option to allow for
              the 'clicked()' signals to be called or not.  
              This is used primarily for default programmatic 
              manipulation of the buttons, such as loadProjects() in 
              XNATView_Tree, where default filters are applied, but
              the signals of clicking are not desired, but 
              self.currentlyToggledFilterButton is still tracked.
          """
          if isDown and category == 'sort':
              self.buttons[category][name].setChecked(True)
              self.currentlyToggledFilterButton = self.buttons['sort'][name]   




    def addFontSizeDropdown(self, title = "Font Size:" ):
        """ As stated.  Creates the fontSizeDropdown by referring
            to the parent class function of the same name.  After
            the dropdown is created, it allocates the change events
            of the dropdown to update the treeView node's fonts.
        """

        #--------------------
        # Call parent class function of same name
        # to create the dropdown.
        #--------------------  
        super(Settings_View_Tree, self).addFontSizeDropdown(title)


        
        #--------------------
        # Try to retrieve any saved fronts from
        # the settings file that pertains to the current host.
        #-------------------- 
        if self.currXnatHost:
            font = self.SettingsFile.getSetting(self.currXnatHost, 
                                Settings_View_Tree.FONT_SIZE_TAG)



        #--------------------
        # If there are no saved fonts,
        # refer to XnatGlobals to set and save 
        # the font back to the SettingsFile.
        #-------------------- 
        if len(font) == 0:
            currSize = XnatSlicerGlobals.FONT_SIZE
            self.SettingsFile.setSetting(self.currXnatHost, 
            {Settings_View_Tree.FONT_SIZE_TAG: [str(currSize)]})


            
        #--------------------
        # Otherwise, just refer to the
        # saved font.
        #-------------------- 
        else:
            currSize = font[0]



        #--------------------
        # Callback function for when the dropdown
        # is changed.
        #-------------------- 
        def changeFontSize(size):
            try:
                self.Events.runEventCallbacks('FONTSIZECHANGED', size)
                self.SettingsFile.setSetting(self.currXnatHost, 
                    {Settings_View_Tree.FONT_SIZE_TAG: [str(size)]})
            except Exception, e:
                ##print MokaUtils.debug.lf(), str(e)
                pass


            
        #--------------------
        # Tie the dropdown change event
        # to the callback function above.
        #-------------------- 
        currDropdown = self.fontDropdowns[-1]
        currDropdown.connect('currentIndexChanged(const QString&)', 
                             changeFontSize)
        currDropdown.setCurrentIndex(currDropdown.findText(currSize))

        
    


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
        self.buttons['sort'] = {'accessed': XnatSlicerUtils.generateButton(iconOrLabel = 'Last Accessed', 
                                                                               toolTip = "Sort projects, prioritizing those accessed by current user.", 
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
                   self.Events.runEventCallbacks('FILTERTOGGLED'))



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
