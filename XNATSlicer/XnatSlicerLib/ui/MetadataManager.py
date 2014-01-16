# python
import os
import glob
import sys

# application
from __main__ import qt

# external
from Xnat import *

# module
from AnimatedCollapsible import *
from MetadataEditor import *
from XnatSlicerGlobals import *
from XnatSlicerUtils import *


        

class MetadataManager(qt.QFrame):
    """
    MetadataManager is a class that combines several 
    XnatMetadtaEditors and AnimatedCollapsibles to 
    allow for editing of metadata for the XNAT Folder levels outlined
    in 'Xnat.path.DEFAULT_LEVELS' (usually 'projects', 
    'subjects', 'experiments','scans', etc.).
    
    Usually, there are two MetadataEditors for every
    AnimatedCollapsible: XnatDefaultMetadataEditor and an
    XnatCustomMetadataEditor.  Each editor can be tailored
    even further depending on the class that utilizes the
    MetadataEditor.

    @param MODULE: The XNATSlicer widget.
    @type MODULE: XnatSlicerWidget
    """

    def __init__(self, MODULE):
        """ Init function.
        """

        #--------------------
        # Call parent init.
        #--------------------
        super(MetadataManager, self).__init__(self)


        
        #--------------------
        # Track the MODULE.
        #--------------------
        self.MODULE = MODULE



        #--------------------
        # Track all widgets.
        #--------------------
        self.collapsibles = {}
        self.metadataWidgets = {}
        self.defaultMetadataEditors = {}
        self.customMetadataEditors = {}
        self.buttons = {}
        self.labels = {}
        self.collapsibleLayouts = {}
        self.editCustomButtons = {}
        self.currItemType = ''


        
        #--------------------
        # The mainLayout eventually becomes 
        # the layout of the MetadataManager via
        # the '.setLayout' function
        #--------------------       
        self.mainLayout = qt.QVBoxLayout()



        #--------------------
        # The Edit Button group.
        #
        # NOTE: A button group is created because
        # normal qt.QPushButton.connect events do not
        # send the button 'name' to the even method.  A
        # button group allows you to send the actual 
        # button to the vent method.
        #--------------------
        self.editCustomButtonGroup = qt.QButtonGroup()
        self.editCustomButtonGroup.connect('buttonClicked(QAbstractButton*)', self.editCustomClicked)
        self.editButtonsVisible = True



        #--------------------
        # Construct the manager
        #--------------------
        self.constructManager()


        
        #--------------------
        # Set the default states of the 
        # collapsibles.
        #--------------------       
        for key, collapsible in self.collapsibles.iteritems():
            collapsible.suspendAnim(True)
            collapsible.show()
            collapsible.setChecked(True)
            collapsible.suspendAnim(False)


            
        
    def constructManager(self):
        """ Constructs the MetadataManager widget.
        """

        #--------------------
        # Loop through all folders as per 
        # Xnat.path.DEFAULT_LEVELS.  We create an AnimatedCollapsible
        # for every folder, one XnatCustomMetadataEditor and one 
        # XnatDefaultMetadataEditor, along with the relevant buttons for
        # very folder in XNAT_LEVELS.
        #--------------------
        for xnatLevel in Xnat.path.DEFAULT_LEVELS:

            #
            # Set DEFAULT label per xnat level.
            #
            self.labels[xnatLevel] = []
            self.labels[xnatLevel].append(qt.QLabel('<b>DEFAULT<b>'))
            self.labels[xnatLevel][0].setFont(XnatSlicerGlobals.LABEL_FONT_BOLD)

            
            #
            # Set the collapsible's internal layout 
            # (a qt.QGridLayout) per folder.
            #
            self.collapsibleLayouts[xnatLevel] = qt.QGridLayout()
            self.collapsibleLayouts[xnatLevel].addWidget(self.labels[xnatLevel][0], 0, 0)


            #
            # Set the XnatDefaultMetadataEditor, 
            # add to layout.
            #
            self.defaultMetadataEditors[xnatLevel] = XnatDefaultMetadataEditor(self.MODULE, xnatLevel)
            self.collapsibleLayouts[xnatLevel].addWidget(self.defaultMetadataEditors[xnatLevel], 1, 0)


            #
            # Set the XnatCustomMetadataEditor, 
            # add to layout.
            # 
            self.customMetadataEditors[xnatLevel] = XnatCustomMetadataEditor(self.MODULE, xnatLevel)
            self.collapsibleLayouts[xnatLevel].addWidget(self.customMetadataEditors[xnatLevel], 1, 1, 1, 2)
            

            #
            # Set DEFAULT label per xnat level.
            #
            self.labels[xnatLevel].append(qt.QLabel('<b>CUSTOM<b>'))
            self.labels[xnatLevel][1].setFont(XnatSlicerGlobals.LABEL_FONT_BOLD)
            self.collapsibleLayouts[xnatLevel].addWidget(self.labels[xnatLevel][1], 0, 1)

            
            #
            # Add the 'editCustom' button. 
            #
            # NOTE: The user can choose to hide/show these buttons,
            # based on what's needed.  For isntance, the MetadataSettings
            # class hides these buttons as they are not necessary for
            # its workflow.
            #
            self.editCustomButtons[xnatLevel] = XnatSlicerUtils.generateButton(iconOrLabel = "Edit custom tags for '%s'"%(xnatLevel), 
                                                                               toolTip = "Adds a custom metadata tag to display in the 'Info' column.", 
                                                                               font = XnatSlicerGlobals.LABEL_FONT,
                                                                               size = qt.QSize(180, 20), 
                                                                               enabled = True)
            self.collapsibleLayouts[xnatLevel].addWidget(self.editCustomButtons[xnatLevel], 0, 2)
            self.editCustomButtonGroup.addButton(self.editCustomButtons[xnatLevel])
            

            #
            # Put all of the widgets into first, a contentsWidget.
            # Then set the widget of the AnimatedCollapsible to the
            # contentsWidget.
            #
            self.collapsibles[xnatLevel] = AnimatedCollapsible(self, xnatLevel.title())
            self.collapsibles[xnatLevel].setMaxExpandedHeight(250)
            self.collapsibles[xnatLevel].setMinExpandedHeight(250)
            
            contentsWidget = qt.QWidget()
            contentsWidget.setLayout(self.collapsibleLayouts[xnatLevel])
            self.collapsibles[xnatLevel].setContents(contentsWidget)
            self.collapsibles[xnatLevel].setFixedWidth(550)


            #
            # Add collapsible to self.mainLayout.
            #
            self.mainLayout.addWidget(self.collapsibles[xnatLevel])
            self.mainLayout.addSpacing(10)



        #--------------------
        # Set callback to Update XNATSlicer's 
        # layout when animating.
        #--------------------
        for key, collapsible in self.collapsibles.iteritems():
            collapsible.onEvent('animate', self.updateLayout)


            
        #--------------------
        # Set mainLayout to the master layout.
        #--------------------
        self.mainLayout.addStretch()
        self.setLayout(self.mainLayout)



        #--------------------
        # Set the current item tyype to label.
        # The user can change it to 'checkbox' 
        # later.
        #--------------------
        self.setItemType('label')

            


    def updateLayout(self):
        """ As stated.
        """

        self.layout().update()



                        
    def setItemType(self, itemType):
        """ Sets the item type provided by the 'itemType'
            argument within the MetadataEditors.
        """
        ##print "\t (Metadata Manager) METADATA SET ITEM TYPE", itemType
        self.currItemType = itemType
        for key, metadataEditor in self.defaultMetadataEditors.iteritems():
            metadataEditor.setItemType(itemType)
        for key, metadataEditor in self.customMetadataEditors.iteritems():
            metadataEditor.setItemType(itemType)






    def setEditButtonsVisible(self, visible = None):
        """ Hides or shows the 'edit' metadata buttons
            that reside at the top of every collapsible
            content widge.
        """

        if visible != None:
            self.editButtonsVisible = visible

        for key, button in self.editCustomButtons.iteritems():
            if button:
                button.setVisible(self.editButtonsVisible)


            


    def editCustomClicked(self, button):
        """ Callback when any of the 'editCustomButtons'
            are clicked.  Descriptors below.
        """
        for xnatLevel, _button in self.editCustomButtons.iteritems():
            if button == _button:

                #--------------------
                # Show the MetadataEditor settings window.
                #--------------------
                self.MODULE.SettingsWindow.showSettingWidget(self.MODULE.MetadataSettings.title) 

                #--------------------
                # Expand the collapsible that had the same
                # XnatLevel as the button that called this function.
                #--------------------
                self.MODULE.MetadataSettings.MetadataManagers['main'].collapsibles[xnatLevel].setChecked(True)
            else:
                self.MODULE.MetadataSettings.MetadataManagers['main'].collapsibles[xnatLevel].setChecked(False)

        

                
    def setCustomEditVisible(self, visible):
        """ Sets the 'editLine' of every MetadataEditor 
            visible.
        """
        for key, metadataEditor in self.customMetadataEditors.iteritems():
            metadataEditor.setEditLineVisible(visible)


                
                   
    def update(self):
        """ Updates the MetadataEditor's contents,
            namely through calling the 'update' function
            of every MetadataEditor contained in the 
            MetadataManager.
        """

        #--------------------
        # Updates the layout.
        #--------------------
        self.updateLayout()


        #--------------------
        # Clear the customMetadataEdtiors and
        # then update them, which will reload the
        # stored metadata values.
        #
        # Run a simple 'update' on the default
        # metadata edtiors.
        #--------------------
        for key in self.customMetadataEditors:
            self.customMetadataEditors[key].clear() 

            try:
                self.defaultMetadataEditors[key].update()
                self.customMetadataEditors[key].update()

                #
                # Sync the tags with the settings file
                #  
                xnatHost = self.MODULE.LoginMenu.hostDropdown.currentText
                checkedItems = self.defaultMetadataEditors[key].checkedMetadataItems + self.customMetadataEditors[key].checkedMetadataItems
                tagDict = {self.defaultMetadataEditors[key].checkedLevelTag : checkedItems}
                self.MODULE.SettingsFile.setSetting(xnatHost, tagDict)
                #print "\n\nCHECKED LEVEL TAG", checkedItems
                #print "\nREF", self.defaultMetadataEditors[key].checkedLevelTag
                    
            except Exception, e:
                MokaUtils.debug.lf(str(e))


                

    def setOnMetadataCheckedTag(self, tag):
        """ Sets the 'onMetadataCheckedTag' for the contained
            MetadataEditors.  The 'onMetadataCheckedTag' is referred
            to when an item (checkbox) in the MetadataEditor is checked, 
            referring to the XnatSetting class name so the module knows
            what widgets to adjust when the 'check' or 'uncheck' event 
            occurs.
        """

        for key in self.defaultMetadataEditors:
            self.defaultMetadataEditors[key].onMetadataCheckedTag = tag
        for key in self.customMetadataEditors:
            self.customMetadataEditors[key].onMetadataCheckedTag = tag            
