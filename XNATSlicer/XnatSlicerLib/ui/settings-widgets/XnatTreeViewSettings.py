from __main__ import vtk, qt, ctk, slicer

import os
import glob
import sys

from XnatSettings import *
from XnatMetadataManager import *




comment = """
XnatTreeViewSettings is the XnatSettings pertaining to
the 'XnatTreeView' class.  This class specifically
deals with the following:

1) Toggling the visible metadata key-value pairs
in the 'Info' column of the TreeView and saving this
in the XnatSettingsFile.

2) Setting the font size of the tree view.

3) Filtering the tree view nodes by column values
(LastAccessed).


All 'XnatSettings' subclasses
are to be displaed in the 'XnatSettingsWindow' class.

TODO:
"""




#--------------------
# Define the info metadata tags for storing into 
# the settings file
#--------------------
infoMetadataTags = {'projects': '', 'subjects' : '', 'experiments' : '', 'scans' :'', 'files' : '', 'slicer': ''}
for key in infoMetadataTags:
    infoMetadataTags[key] = 'infoMetadataTags_' + key


    
        
class XnatTreeViewSettings(XnatSettings):
    """ Descriptor above.
    """
  
    def __init__(self, title, MODULE):
        """ Init function.
        """
        
        #--------------------
        # Call parent init
        #--------------------
        super(XnatTreeViewSettings, self).__init__(title, MODULE)

            
        
        #--------------------
        # Add Sort Buttons section
        #--------------------
        self.addSortAndFilterButtons()
        self.addSpacing()


        
        #--------------------
        # Add font dropdown
        #--------------------
        self.addFontSizeDropdown("Tree View Font Size:")
        self.addSpacing()

        

        #--------------------
        # Add the metadata Manager
        #--------------------        
        self.addMetadataManager()
        self.complete()


        
        
      
    def setButtonDown(self, category = None, name = None, isDown = True, callSignals = True):
          """ Programmatically sets a button down based on
              the arguments.  The user has the option to allow for
              the 'clicked()' signals to be called or not.  
              This is used primarily for default programmatic 
              manipulation of the buttons, such as loadProjects() in 
              XNATTreeView, where default filters are applied, but
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
        super(XnatTreeViewSettings, self).addFontSizeDropdown(title)


        
        #--------------------
        # Try to retrieve any saved fronts from
        # the settings file that pertains to the current host.
        #-------------------- 
        self.fontSizeTag = "TreeViewFontSize"
        xnatHost = self.MODULE.XnatLoginMenu.hostDropdown.currentText
        font = self.MODULE.XnatSettingsFile.getTagValues(xnatHost, self.fontSizeTag)



        #--------------------
        # If there are no saved fonts,
        # refer to XnatGlobals to set and save 
        # the font back to the XnatSettingsFile.
        #-------------------- 
        if len(font) == 0:
            currSize = self.MODULE.GLOBALS.FONT_SIZE
            self.MODULE.XnatSettingsFile.setTagValues(xnatHost, {self.fontSizeTag: [str(currSize)]})


            
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
                self.MODULE.XnatView.changeFontSize(int(size))
                self.MODULE.XnatSettingsFile.setTagValues(xnatHost, {self.fontSizeTag: [str(size)]})
            except Exception, e:
                #print self.MODULE.utils.lf(), str(e)
                pass


            
        #--------------------
        # Tie the dropdown change event
        # to the callback function above.
        #-------------------- 
        currDropdown = self.fontDropdowns[-1]
        currDropdown.connect('currentIndexChanged(const QString&)', changeFontSize)
        currDropdown.setCurrentIndex(currDropdown.findText(currSize))

        


    def addMetadataManager(self):
        """ Add metadata manager function specific to 
            the XnatTreeViewSettings.  This refers to the
            'createMetadataManagers' function for the purpose
            and then adjusts it accordingly.  This basically 
            exists to reduce clutter in the __init__ function.
        """
        
        #--------------------
        # Create the metadata manager type.
        #--------------------        
        self.createMetadataManagers('info')        
        self.addSection("Info. Column Metadata", self.XnatMetadataManagers['info'])



        #--------------------
        # Set the default selected metadata.
        #--------------------  
        self.setDefaultSelectedMetadata('info',  {
            'projects' : [
                'last_accessed_497',
                ],
                
            'subjects' : [
                'label',
                ],
                    
            'experiments' : [
                'date',
                ],
                        
            'scans' : [
                'series_description',
                'type',
                'quality',
                ],
                                                                          
            'resources' : [
                'element_name',
                ],
                                                                                              
            'files' : [
                'Size',
                ],
                                                                                                    
            'slicer' : [
                'Size',
                ]
                
        })



        #--------------------
        # Hide metadataManager's custom edit
        # widgets and make sure it's a checkbox.
        #--------------------  
        for key, manager in self.XnatMetadataManagers.iteritems():
            manager.setCustomEditVisible(False)
            manager.setItemType('checkbox')


            


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
        self.buttons['sort'] = {'accessed': self.MODULE.utils.generateButton(iconOrLabel = 'Last Accessed', 
                                                                               toolTip = "Sort projects, prioritizing those accessed by current user.", 
                                                                               font = self.MODULE.GLOBALS.LABEL_FONT,
                                                                               size = qt.QSize(90, 20), 
                                                                               enabled = True)}
      
        self.buttons['sort']['accessed'].setCheckable(True)
        self.buttons['sort']['accessed'].setChecked(False)


        
        #--------------------
        # Callback for when the filter
        # button is clicked.
        #--------------------
        def accessedToggled(toggled):
            if toggled:
                self.MODULE.XnatView.filter_accessed()
            else:
                self.MODULE.XnatView.filter_all()



        #--------------------
        # Connect the filter button to
        # the button click.
        #--------------------
        self.buttons['sort']['accessed'].connect('toggled(bool)', accessedToggled)



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
