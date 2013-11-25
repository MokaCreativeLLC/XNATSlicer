from __main__ import vtk, qt, ctk, slicer

import os
import glob
import sys

from AnimatedCollapsible import *
from VariableItemListWidget import *
from XnatMetadataManager import *




comment = """
XnatSettings is a parent class to the various 
component settings that exist within the XnatSettingsWindow: 
XnatTreeViewSettings, XnatDetailsSettings, XnatMetadataSettings,
XnatHostSettings, etc.  It contains a number of generic functions
for managing generic variables and creating generic interactors
(especially XnatMetadataSettings objects).

XnatSettings inherits from qt.QScrollArea.  

TODO:
"""



        
class XnatSettings(qt.QScrollArea):
    """ Descriptor above.
    """

    def __init__(self, title, MODULE):
        """ Init function.
        """
        
        #--------------------
        # Call parent init.
        #--------------------
        super(XnatSettings, self).__init__(self)


        
        #--------------------
        # Set class variables.
        #--------------------
        self.MODULE = MODULE
        self.sectionSpacing = 5
        self.ON_METADATA_CHECKED_TAGS = {}
        self.defaultSelectedMetadata = {}
        self.tabTitle = title
        self.sectionLabels = []


        
        #--------------------
        # Set stylesheet.
        #--------------------
        self.setObjectName('xnatSetting')
        self.setStyleSheet('#xnatSetting {height: 100%; width: 100%; border: 1px solid gray;}')


        
        #--------------------
        # NOTE: This fixes a scaling error that occurs with the scroll 
        # bar.  When we inherit from a QWidget.  
        #--------------------
        self.verticalScrollBar().setStyleSheet('width: 15px')


        
        #--------------------
        # The label
        #--------------------
        self.label = qt.QLabel(title)


        
        #--------------------
        # Layout for widget frame.
        #--------------------
        self.frame = qt.QFrame()
        self.frame.setObjectName('settingFrame')
        self.frame.setStyleSheet("#settingFrame {background: white;}")



        #--------------------
        # Layout for the entire widget.
        #--------------------
        self.masterLayout = qt.QVBoxLayout()
        self.masterLayout.setContentsMargins(10,10,10,10)



        #--------------------
        # Define the XnatMetadataManagers dictionary.
        # Subclasses will then call on 'createMetadataManagers'
        # to add to this dictionary.
        #--------------------
        self.XnatMetadataManagers = {}



        
    @property
    def title(self):
        """ The title of the XnatSetting.
        """
        return self.label.text
        

    
        
    def createMetadataManagers(self, *args):
        """ Creates any number of metadata managers as 
            specified by *args, which are string keys that 
            are used to identify the metadata managers in
            the XnatMetadataManagers dictionary.
        """
        for arg in args:
            self.XnatMetadataManagers[arg] = XnatMetadataManager(self.MODULE)

            #
            # This assigns the XnatSetting's class name (which will be 
            # a subclass of XnatSettings) to the metadataCheckedTags,
            # which are ultimately stored in the XnatSettingsFile.
            #
            self.ON_METADATA_CHECKED_TAGS[arg] = self.__class__.__name__ + "_%s_"%(arg) 
            self.XnatMetadataManagers[arg].setOnMetadataCheckedTag(self.ON_METADATA_CHECKED_TAGS[arg])
            self.defaultSelectedMetadata[arg] = None




            
    def setDefaultSelectedMetadata(self, label, *args):
        """ Per metadata manager that exists in every 
            XnatSetting, allows the arguments in *args to 
            specify the default contents and select
            states of the metadata within every XnatSetting.
        """

        #--------------------
        # If the argument is a dictionary, then apply it.
        # directly to the 'defaultSelectedMetadata' dictionary.
        #--------------------
        if type(args[0]) == dict:
            self.defaultSelectedMetadata[label] = args[0]


            
        #--------------------
        # Loop through all available XNAT hosts
        # and query the XnatSettingsFile for metadata
        # objects that are defined there.
        #--------------------
        xnatHosts = [self.MODULE.XnatLoginMenu.hostDropdown.itemText(ind) for ind in range(0, self.MODULE.XnatLoginMenu.hostDropdown.count)]
        for xnatHost in xnatHosts:

            #
            # Loop through all xnatLevels (projects, subjects, etc.)
            #
            for xnatLevel in self.MODULE.GLOBALS.XNAT_LEVELS:

                #
                # Loop through the metadatacheckedtags
                #
                for key in self.ON_METADATA_CHECKED_TAGS:

                    #
                    # Construct the metadatatag by 
                    # XNAT level (projects, subjects, etc...)
                    #
                    levelTag = self.ON_METADATA_CHECKED_TAGS[key] + xnatLevel
                    savedMetadataItems = self.MODULE.XnatSettingsFile.getTagValues(xnatHost, levelTag)
                    
                    #
                    # If there are no 'savedMetadataItems', from
                    # set settings file (perLevel), go ahead and save the
                    # defaults as per 'defaultSelectedMetadata'
                    #
                    if len(savedMetadataItems) == 0:
                        if self.defaultSelectedMetadata[key]:
                            defaultSelectedMetadata = self.defaultSelectedMetadata[key][xnatLevel] 
                            tagDict = {levelTag : defaultSelectedMetadata}
                            self.MODULE.XnatSettingsFile.setTagValues(xnatHost, tagDict)


                        
        
        

    def complete(self):
        """ A necessary function that's for
            to wrapping up every XnatSetting __init__ function.
            It makes the layout's contents display correctly.
            
            NOTE: Ideally this would not have to happen, but updating
            the widget's frame dynamically (after it has been 
            applied via setWidget) and then adding widgets, doesn't
            update at all.
        """
                
        #--------------------
        # Manipulate collapsibles and set
        # the widget to the frame.
        #--------------------
        self.masterLayout.addStretch()
        self.frame.setLayout(self.masterLayout)
        for key, manager in self.XnatMetadataManagers.iteritems():
            if manager.collapsibles:
                for key in manager.collapsibles:
                    manager.collapsibles[key].show() 
                    manager.collapsibles[key].setChecked(False) 
            self.setWidget(self.frame)

        




    def addSection(self, title, qobject):
        """ Adds a section to the XnatSettings by
            creating a label, the title of which is specified
            in the 'title' argument, and then adding the 
            relevant qobject to the masterLayout.
        """

        #--------------------
        # Add label title and spacing.
        #--------------------        
        self.sectionLabels.append(qt.QLabel('<b>%s</b>'%(title), self))
        self.masterLayout.addWidget(self.sectionLabels[-1])
        self.masterLayout.addSpacing(self.sectionSpacing)


        #--------------------
        # Add the qobject.
        #-------------------- 
        if 'layout' in qobject.className().lower():
            self.masterLayout.addLayout(qobject)
        else:
            self.masterLayout.addWidget(qobject)


        
        
    def addSpacing(self, spacing = 10):
        """ Adds a spacing element to the
            masterLayout.
        """
        self.masterLayout.addSpacing(spacing) 
        



    def addFontSizeDropdown(self, title = "Font Size:" ):
        """ Adds a fontSize dropdown to the layout
            of the XnatSetting.  The subclass then
            needs to specify how to connect the events
            of the dropdown.
        """
        try:
            self.fontDropdowns.append(qt.QComboBox())
            self.fontDropdowns[-1].addItems([str(i) for i in range(8, 21)])
            self.fontDropdowns[-1].setFixedWidth(100)
            self.addSection(title, self.fontDropdowns[-1])



        #--------------------
        # If there's no 'fontDropdowns' variable
        # then we create one and call the function again.
        #--------------------
        except Exception, e:
            self.fontDropdowns = []
            self.addFontSizeDropdown(title)
