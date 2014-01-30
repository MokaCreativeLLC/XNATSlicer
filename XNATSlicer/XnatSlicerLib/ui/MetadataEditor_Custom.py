# application
from __main__ import qt

# external
from Xnat import *

# module 
from MetadataEditor import *
from XnatSlicerUtils import *


class MetadataEditor_Custom(MetadataEditor):
    """ 
    MetadataEditor_Custom presents and manages custom metadata
    for the user to add/remove and toggle when traversing an XNAT 
    tree in a given View.  It is in constant communication with
    the SettingsFile, storing the changes accordingly.  This is 
    in contrast with the XnatMetadataEditor_Default, which 
    refers to the XnatGlobals to populate its contents.
    """


    
    def setup(self):
        """ Init function.
        """

        #--------------------
        # The interactor button dimensions:
        #
        # For add and remove.
        #--------------------
        buttonHeight = 25
        buttonWidth = 50
        lineWidth = 150



        #--------------------
        # The 'lineEdit' for adding custom metadata
        #--------------------        
        self.lineEdit = qt.QLineEdit()
        self.lineEdit.setFixedHeight(buttonHeight)
        self.lineEdit.setFixedWidth(lineWidth)

        #
        # Install an event filter on the line
        # edit for tighter UX control.
        #
        self.lineEdit.installEventFilter(self)
        self.lineEdit.connect('textChanged(const QString)', self.onLineEditFocused)
        

        
        #--------------------
        # The addButton
        #--------------------          
        self.addButton = qt.QPushButton('Add')
        self.addButton.setFixedHeight(buttonHeight)
        self.addButton.setFixedWidth(buttonWidth)
        self.addButton.connect('clicked()', self.onAddButtonClicked)


        
        #--------------------
        # The deleteButton
        #--------------------        
        self.deleteButton = qt.QPushButton('Remove')
        self.deleteButton.setFixedHeight(buttonHeight)
        self.deleteButton.setFixedWidth(buttonWidth)
        self.deleteButton.connect('clicked()', self.onDeleteButtonClicked)
        self.deleteButton.setEnabled(False)



        #--------------------
        # The custom add/edit line.
        #--------------------  
        self.lineLayout = qt.QHBoxLayout()
        self.lineLayout.addWidget(self.lineEdit)
        self.lineLayout.addWidget(self.addButton)
        self.lineLayout.addWidget(self.deleteButton)
        self.mainLayout.addLayout(self.lineLayout)

        

        

    def eventFilter(self, widget, event):
        """ 
        Tracks whether the lineEdit was focused
        and runs the relevant callback.

        @deprecated
        """
        #print widget, event.type()
        if widget == self.lineEdit:
            if event.type() == qt.QEvent.FocusIn:
                self.onLineEditFocused()
        



    def onDeleteButtonClicked(self):
        """ 
        Deletes a custom metadata item from the listWidget,
        communicating with the SettingsFile accordingly.
        """
        

        currItem = self.listWidget.currentItem()
        currItemText = currItem.text().lower().strip()

        #--------------------
        # Retrieve the custom metadata elements
        # stored in the SettingsFile.
        #--------------------  
        customMetadataItems = self.SettingsFile.getSetting(self.currXnatHost, 
                                                           self.storageTagName)



        #--------------------
        # STEP 1: Remove the selected item 
        # from the custom tags. For all other
        # selected items, track in a list.
        #--------------------        
        updatedMetadataItems = []
        for item in customMetadataItems:
            if item.lower().strip() == currItemText:
                self.listWidget.removeItemWidget(
                    self.listWidget.currentItem())
            else:
                updatedMetadataItems.append(item)

        #
        # Write all selected items to the 
        # SettingsFile.
        #     
        tagDict = {XnatSlicerUtils.makeCustomMetadataTag(self.xnatLevel) : \
                   updatedMetadataItems}
        self.SettingsFile.setSetting(self.currXnatHost, tagDict)


        
        #--------------------
        # Refer to the settings window to update
        # ALL of the other XnatMetadataEdtiors.
        #--------------------
        self.Events.runEventCallbacks('DELETECLICKED')
        self.MODULE.SettingsWindow.updateSettingWidgets()


        
            

            
            
    def onAddButtonClicked(self):
        """ 
        Callback when the addButton is clicked.
        Communicates with XnatSettingFile accordingly.
        """

        #--------------------
        # Return out of there's no
        # text in the lineEdit.
        #--------------------        
        lineText = self.lineEdit.text
        if len(lineText.strip()) == 0:
            return


        
        #--------------------
        # Merge the lineEdit text with the saved
        # metadata IF it's not there in both the default and custom tags.
        #-------------------- 
        defaultMetadataItems = Xnat.metadata.DEFAULT_TAGS[self.xnatLevel]
        customMetadataItems = self.SettingsFile.getSetting(self.currXnatHost, 
                        XnatSlicerUtils.makeCustomMetadataTag(self.xnatLevel))

        inDefault = lineText in defaultMetadataItems
        inCustom = lineText in customMetadataItems

        if not inDefault and not inCustom:
            tagDict = {XnatSlicerUtils.makeCustomMetadataTag(self.xnatLevel) : \
                       [lineText] + customMetadataItems}
            self.SettingsFile.setSetting(self.currXnatHost, tagDict)

            #
            # Clear the lineEdit.
            #
            self.lineEdit.clear()
        
            #
            # Update all the settingsWidgets.
            #
            self.Events.runEventCallbacks('ADDCLICKED')
            self.MODULE.SettingsWindow.updateSettingWidgets()
        else:
            tagType = 'Custom' if inCustom else 'Default'
            msg = "'%s' already exists in %s tags."%(lineText, tagType)
            self.takenBox = qt.QMessageBox(1, "Add Metadata", msg)
            self.takenBox.show()
            self.lineEdit.selectAll()


        

    def setEditLineVisible(self, visible):
        """ 
        Allows the editline to be displayed
        or not depending on the 'visible'
        argument.
        """

        try:
            self.mainLayout.removeItem(self.lineLayout)
            self.lineEdit.hide()
            self.addButton.hide()
            self.deleteButton.hide()
            self.mainLayout.update()
        except Exception, e:
            pass
            
        if visible:
            self.mainLayout.addLayout(self.lineLayout)
            self.lineEdit.show()
            self.addButton.show()
            self.deleteButton.show()
            self.mainLayout.update()            


            

    @property
    def storageTagName(self):
        """
        @return: The tag pertaining to the checked metadata level.
        @rtype: string
        """
        return XnatSlicerUtils.makeCustomMetadataTag(self.xnatLevel)




    def onItemClicked(self, listWidgetItem):
        """ 
        Runs class-specific callbacks for
        when an item in the listWidget is clicked.
        Also refers to the parent 'onItemClicked'
        function.
        """

        #--------------------
        # Call parent 'onItemClicked'
        #-------------------- 
        super(MetadataEditor_Custom, self).onItemClicked(listWidgetItem)


        
        #--------------------
        # Update the edit widgets.
        #-------------------- 
        self.deleteButton.setEnabled(True)
        self.addButton.setEnabled(False)
        self.lineEdit.clear()


        

    def onLineEditFocused(self, *args):
        """ 
        Callback for when the user
        focuses on the lineEdit.
        Toggles the edit buttons accordingly.
        """
        if self.listWidget.currentItem():
            self.listWidget.currentItem().setSelected(False)
        self.addButton.setEnabled(True)
        self.deleteButton.setEnabled(False)
        


