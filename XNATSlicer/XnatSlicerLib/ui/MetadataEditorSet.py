# application
from __main__ import qt

# external 
from Xnat import *

# module
from AnimatedCollapsible import *
from MetadataEditor_Custom import *
from MetadataEditor_Default import *
from XnatSlicerGlobals import *
from XnatSlicerUtils import *

        

class MetadataEditorSet(qt.QFrame):
    """
    MetadataEditorSet is a class that combines one
    XnatMetadtaEditors and AnimatedCollapsibles to 
    allow for editing of metadata for the XNAT Folder levels outlined
    in 'Xnat.path.DEFAULT_LEVELS' (usually 'projects', 
    'subjects', 'experiments','scans', etc.).
    
    Usually, there are two MetadataEditors for every
    AnimatedCollapsible: MetadataEditor_Default and an
    MetadataEditor_Custom.  Each editor can be tailored
    even further depending on the class that utilizes the
    MetadataEditor.
    """

    EVENT_TYPES = [
        'editCustomClicked'
    ]

    def __init__(self, SettingsFile):
        """ Init function.
        """

        #--------------------
        # Call parent init.
        #--------------------
        qt.QFrame.__init__(self)


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
        self.Events = MokaUtils.Events(self.EVENT_TYPES)


        
        #--------------------
        # The mainLayout eventually becomes 
        # the layout of the MetadataEditorSet via
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
        self.editCustomButtonGroup.connect('buttonClicked(QAbstractButton*)', \
                                           self.editCustomClicked)
        self.editButtonsVisible = True



        #--------------------
        # Construct the manager
        #--------------------
        self.construct()


        
        #--------------------
        # Set the default states of the 
        # collapsibles.
        #--------------------       
        for key, collapsible in self.collapsibles.iteritems():
            collapsible.suspendAnim(True)
            collapsible.show()
            collapsible.setChecked(True)
            collapsible.suspendAnim(False)


    @property
    def allEditors(self):
        """
        """
        return [e for l, e in self.defaultMetadataEditors.iteritems()] + \
        [e for l, e in self.customMetadataEditors.iteritems()] 
            
        


    def hasEditor(self, _editor):
        """
        """
        for editor in self.allEditors:
            if editor == _editor:
                return True
        return False



    def loopEditors(self, callback):
        """
        """
        for editor in self.allEditors:
            callback(editor)




            
        
    def construct(self):
        """ Constructs the MetadataEditorSet widget.
        """

        #--------------------
        # Loop through all folders as per 
        # Xnat.path.DEFAULT_LEVELS.  We create an AnimatedCollapsible
        # for every folder, one MetadataEditor_Custom and one 
        # MetadataEditor_Default, along with the relevant buttons for
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
            self.collapsibleLayouts[xnatLevel].\
                addWidget(self.labels[xnatLevel][0], 0, 0)


            #
            # Set the MetadataEditor_Default, 
            # add to layout.
            #
            self.defaultMetadataEditors[xnatLevel] = \
            MetadataEditor_Default(xnatLevel)
            self.collapsibleLayouts[xnatLevel].\
                addWidget(self.defaultMetadataEditors[xnatLevel], 1, 0)


            #
            # Set the MetadataEditor_Custom, 
            # add to layout.
            # 
            self.customMetadataEditors[xnatLevel] = \
                MetadataEditor_Custom(xnatLevel)
            self.collapsibleLayouts[xnatLevel].\
                addWidget(self.customMetadataEditors[xnatLevel], 1, 1, 1, 2)
            


   


            #
            # Set DEFAULT label per xnat level.
            #
            self.labels[xnatLevel].append(qt.QLabel('<b>CUSTOM<b>'))
            self.labels[xnatLevel][1].setFont(XnatSlicerGlobals.LABEL_FONT_BOLD)
            self.collapsibleLayouts[xnatLevel].\
                addWidget(self.labels[xnatLevel][1], 0, 1)

            
            #
            # Add the 'editCustom' button. 
            #
            # NOTE: The user can choose to hide/show these buttons,
            # based on what's needed.  For isntance, the Settings['METADATA']
            # class hides these buttons as they are not necessary for
            # its workflow.
            #
            self.editCustomButtons[xnatLevel] = \
                XnatSlicerUtils.generateButton(iconOrLabel = \
                    "Edit custom tags for '%s'"%(xnatLevel), 
                toolTip = "Adds a custom metadata tag to display in the" + 
                                               " 'Info' column.", 
                font = XnatSlicerGlobals.LABEL_FONT,
                size = qt.QSize(180, 20), 
                enabled = True)

            self.collapsibleLayouts[xnatLevel].\
                addWidget(self.editCustomButtons[xnatLevel], 0, 2)
            self.editCustomButtonGroup.\
                addButton(self.editCustomButtons[xnatLevel])
            

            #
            # Put all of the widgets into first, a contentsWidget.
            # Then set the widget of the AnimatedCollapsible to the
            # contentsWidget.
            #
            self.collapsibles[xnatLevel] = AnimatedCollapsible(self, \
                                                        xnatLevel.title())
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
                self.Events.runEventCallbacks('editCustomClicked', 
                                              button, xnatLevel)
                




        

                
    def setCustomEditVisible(self, visible):
        """ Sets the 'editLine' of every MetadataEditor 
            visible.
        """
        for key, metadataEditor in self.customMetadataEditors.iteritems():
            metadataEditor.setEditLineVisible(visible)


                
                   
    def update(self):
        """ 
        Updates the MetadataEditor's contents,
        namely through calling the 'update' function
        of every MetadataEditor contained in the 
        MetadataEditorSet.
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
                
                checkedItems = self.defaultMetadataEditors[key].\
                               checkedMetadataItems + \
                               self.customMetadataEditors[key].\
                               checkedMetadataItems

                tagDict = {self.defaultMetadataEditors[key].storageTagName : \
                           checkedItems}
                self.SettingsFile.setSetting(self.currXnatHost, tagDict)


            except Exception, e:
                MokaUtils.debug.lf(str(e))


                       
