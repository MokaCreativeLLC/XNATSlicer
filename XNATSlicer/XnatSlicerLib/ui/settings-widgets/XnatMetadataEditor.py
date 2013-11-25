from __main__ import vtk, qt, ctk, slicer

import os
import glob
import sys


from VariableItemListWidget import *




comment = """ 
XnatMetadataEditor is the editor widget that resides
twice in every XnatMetadaManager section, or XnatLevel.
Like the "XnatSettings" widgets, it is also in 
communication with the XnatSettingsFile as the 
metadata that exists within its lists are loaded, synced
and stored within the XnatSettingsFile.  It is also 
in touch with XnatGlobals to refer to any default
metadata that may exist within all XNAT hosts.

The user must specifiy the XnatLevel that the 
XnatMetadataEditor belongs to as an argument
in the __init__ function.

XnatMetadataEdtior is a
parent class of the specific metadata editors:
XnatDefaultMetadataEditors, XnatCustomMetadataEditor.
It contains functions shared between the two.

Each subclass of XnatMetadataEdtior resides in one 
section of the XnatMetadataManager.For example, there are 
two XnatMetadataEditors in the 'projects' section,
(XnatDefaultMetadataEditors, XnatCustomMetadataEditor)
two in the 'subjects' section (XnatDefaultMetadataEditors, 
XnatCustomMetadataEditor), etc.  

With respect to the child classes of the XnatMetadataEditor,
the user can further customize each edtior.  For instance,
if the list items are to be checkboxes, or if the "Add" and
"Remove" buttons are visible.


TODO:
"""



        
class XnatMetadataEditor(qt.QFrame):
    """ Descriptor above. 
    """
    
    def __init__(self, MODULE, xnatLevel):
        """ Init function.  In addtion to the
            MODULE, the user must also provide
            the xnatLevel that the editor applies to.
        """

        #--------------------
        # Parent init.
        #--------------------
        super(XnatMetadataEditor, self).__init__(self)


        
        #--------------------
        # Class variables.
        #--------------------       
        self.MODULE = MODULE
        self.xnatLevel = xnatLevel
        self.onMetadataCheckedTag = "ON_METADATA_CHECKED"


        
        #--------------------
        # The list widget.
        #--------------------         
        self.listWidget = VariableItemListWidget()
        self.listWidget.setStyleSheet('margin-top: 0px; margin-bottom: 0px')


        
        #--------------------
        # The main layout of the widget.
        #--------------------         
        self.mainLayout = qt.QVBoxLayout()
        self.mainLayout.addWidget(self.listWidget)
        self.setLayout(self.mainLayout)


        
        #--------------------
        # Widget item size.
        #--------------------
        self.itemSize = qt.QSize(20,20)



        #--------------------
        # Call setup function:
        # this is a to be inherited
        # by child classes.
        #--------------------          
        self.setup()


        
        #--------------------
        # List items are defaulted to 
        # 'label'.  The user can change
        # the item type after initialization.
        #--------------------        
        self.setItemType('label')

        

        #--------------------
        # Sync list contents with the
        # the metadata stored in the
        # XnatSettingsFile.
        #--------------------          
        self.update()


        
        
    @property
    def count(self):
        """ Returns the listWidget's count.
        """
        return self.listWidget.count


    

    def clear(self):
        """ Clears the listWidget.
        """
        self.listWidget.clear()
    

        
        
    def item(self, index):
        """ Returns the item allocated
            by 'index'
        """
        return self.listWidget.item(index)



    
    def addItems(self, items):
        """ Adds qListWidgetItems to the
            listWidget.
        """
        self.listWidget.addItems(items)



        
    def setItemType(self, itemType):
        """ Allows the user to set the kind of QListWidgetItems to be displayed: 
            either a label or a checkbox, as provided by the 'itemType' argument.

            Refer to here for more information about the flags for setting the
            item type: 
            http://harmattan-dev.nokia.com/docs/library/html/qt4/qt.html#ItemFlag-enum
        """
        
        #--------------------
        # Record the item type for reference.
        #
        # NOTE: XnatMetadataEdtiors can only
        # have one itemType (checkbox or label)
        # for now.
        #--------------------
        #print "\t\t(Meadata Editor) EDITOR SET ITEM TYPE", self.__class__.__name__
        self.currItemType = itemType


        
        #--------------------
        # Set the flags based on the 'self.currItemType' 
        # argument:
        # either a 'checkbox' or a 'label'
        #--------------------
        if self.currItemType == 'checkbox':
            self.itemFlags = 16 | 32          
        elif self.currItemType == 'label':
            self.itemFlags = 1



        #--------------------
        # Loop through all the listWidget's items
        # and set their flags accordingly.
        #--------------------
        if self.listWidget:    
            for i in range(0, self.listWidget.count):
                self.listWidget.item(i).setSizeHint(self.itemSize)
                self.listWidget.item(i).setFlags(self.itemFlags)
                
                #
                # If the item type is a checkbox, 
                # we set it unchecked at first.
                #
                if self.currItemType == 'checkbox':
                    self.listWidget.item(i).setCheckState(0)
               

                

    def update(self):
        """ Refreshes the contents of the listWidget
            to match the stored contents within the
            XnatSettingsFile.  Also reconnects the event
            callbacks when the items are clicked.
        """

        #--------------------
        # Loop through all the listWidget's items
        # and set their flags accordingly.
        #--------------------
        #print "EDITOR SUPER UPDATE"
        self.setItemType(self.currItemType)



        #--------------------
        # Connect item click event.
        #--------------------
        self.listWidget.connect('itemClicked(QListWidgetItem *)', self.onItemClicked)


        
        #--------------------
        # Refer to items in the settings file
        # if the items are a checkbox.  
        #
        # NOTE: If the items are labels, we 
        # refer to the XnatGlobal files because
        # those metadata points will be shared
        # by all XNAT hosts.
        #--------------------
        if self.currItemType == 'checkbox':
            try:

                #
                # Get the current host from the hostDropdown
                # as part of the login menu.
                #
                xnatHost = self.MODULE.XnatLoginMenu.hostDropdown.currentText

                #
                # Query the XnatSettings file for any stored value, by host.
                #
                savedMetadataItems = self.MODULE.XnatSettingsFile.getTagValues(xnatHost, self.onMetadataCheckedTag + self.xnatLevel)

                #
                # Loop through the items and check accordingly.
                #
                for i in range(0, self.listWidget.count):
                    item = self.listWidget.item(i)
                    if item.flags() == 48 and item.text() in savedMetadataItems:
                        item.setCheckState(2)                
            except Exception, e:
                return



            
    def onItemClicked(self, item):
        """ Callback for when an item in the listWidget
            is clicked.
        """
        
        #--------------------
        # Get the current host from the hostDropdown
        # as part of the login menu. This is for the
        # purpose of calling the appropriate XnatSettingsFile
        # section metadata.
        #--------------------
        #print "item clicked", item.text(), item.flags()
        xnatHost = self.MODULE.XnatLoginMenu.hostDropdown.currentText


        
        #--------------------
        # If the item is a checkbox
        #--------------------
        if item.flags() == 48:

            #
            # Query the settings file for the saved 'checked'
            # metadata values.
            #
            savedMetadataItems = self.MODULE.XnatSettingsFile.getTagValues(xnatHost, self.onMetadataCheckedTag + self.xnatLevel)

            #
            # If the item was CHECKED
            # then we modify the saved metadata
            # accordingly...
            #
            if item.checkState() == 2:

                #
                # Get all checked metadata items from
                # the list.
                #
                #print item.text(), "Checked!"
                checkedMetadataItems = []
                for i in range(0, self.listWidget.count):
                    currItem = self.listWidget.item(i)
                    if currItem.flags() == 48 and currItem.checkState() == 2:
                        checkedMetadataItems.append(currItem.text())
                
                #
                # Union the 'checkedMetadataItems' list with the 
                # 'savedMetadataItems' list.
                #
                mergedItems = list(set(savedMetadataItems) | set(checkedMetadataItems))
            
                #
                # Save the unioned list back to the XnatSettingsFile.
                #
                tagDict = {self.onMetadataCheckedTag + self.xnatLevel : mergedItems}
                self.MODULE.XnatSettingsFile.setTagValues(xnatHost, tagDict)



            #
            # If the item was UNCHECKED
            # then we modify the saved metadata
            # accordingly...
            #
            if item.checkState() == 0:
                
                #
                # Difference the checked items in the listWidget
                # with the saved checked items in the XnatSettingsFile.
                #
                differenceItems = list(set(savedMetadataItems) - set([item.text()]))                
                tagDict = {self.onMetadataCheckedTag + self.xnatLevel : differenceItems}
                self.MODULE.XnatSettingsFile.setTagValues(xnatHost, tagDict)  

                

        #--------------------
        # Refresh the XnatView to match any
        # changes.
        #--------------------
        self.MODULE.XnatView.refreshColumns()



        

        
class XnatDefaultMetadataEditor(XnatMetadataEditor):
    """ Metadata edtior for default XnatMetadata as
        defined in XnatGlobals.  
    """
    
    def __init__(self, MODULE, xnatLevel):
        """ Init function.
        """

        super(XnatDefaultMetadataEditor, self).__init__(MODULE, xnatLevel)


        
    
    def setup(self):
        """ Add metadata items to the list widget of default
            (label) type.
        """
        self.listWidget.addItemsByType([tag for tag in self.MODULE.GLOBALS.DEFAULT_XNAT_METADATA[self.xnatLevel]])



        
    def update(self):
        """ Placeholder function if needed: simply calls
            on parent 'update'.
        """

        #--------------------
        # Call parent update.
        #--------------------
        super(XnatDefaultMetadataEditor, self).update()





        
class XnatCustomMetadataEditor(XnatMetadataEditor):
    """ XnatCustomMetadataEditor presents and manages custom metadata
        for the user to add/remove and toggle when traversing an XNAT 
        tree in a given XnatView.  It is in constant communication with
        the XnatSettingsFile, storing the changes accordingly.  This is 
        in contrast with the XnatDefaultMetadataEditor, which 
        refers to the XnatGlobals to populate its contents.
    """
    
    def __init__(self, MODULE, xnatLevel):
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

        

        #--------------------
        # Call parent __init__
        #--------------------  
        super(XnatCustomMetadataEditor, self).__init__(MODULE, xnatLevel)


        

    def eventFilter(self, widget, event):
        """ Tracks whether the lineEdit was focused
            and runs the relevant callback.
        """
        if widget == self.lineEdit:
            if event.type() == qt.QEvent.FocusIn:
                self.onLineEditFocused()
        

        

    def setup(self):
        """ Constructs the lineLayout and the
            mainLayout.
        """
        self.lineLayout.addWidget(self.lineEdit)
        self.lineLayout.addWidget(self.addButton)
        self.lineLayout.addWidget(self.deleteButton)
        self.mainLayout.addLayout(self.lineLayout)

        
        

    def onDeleteButtonClicked(self):
        """ Deletes a custom metadata item from the listWidget,
            communicating with the XnatSettingsFile accordingly.
        """
        
        #--------------------
        # Retrieve the custom metadata elements
        # stored in the XnatSettingsFile.
        #--------------------  
        xnatHost = self.MODULE.XnatLoginMenu.hostDropdown.currentText
        customMetadataItems = self.MODULE.XnatSettingsFile.getTagValues(xnatHost, self.MODULE.GLOBALS.makeCustomMetadataTag(self.xnatLevel))



        #--------------------
        # Remove the selected item 
        # from the list widget. For all other
        # selected items, track in a list.
        #--------------------        
        updatedMetadataItems = []
        for item in customMetadataItems:
            currItem = self.listWidget.currentItem()

            if item.lower().strip() == currItem.text().lower().strip():
                self.listWidget.removeItemWidget(self.listWidget.currentItem())
            else:
                updatedMetadataItems.append(item)


                
        #--------------------
        # Write all selected items to the 
        # XnatSettingsFile.
        #--------------------        
        tagDict = {self.MODULE.GLOBALS.makeCustomMetadataTag(self.xnatLevel) : updatedMetadataItems}
        self.MODULE.XnatSettingsFile.setTagValues(xnatHost, tagDict)


        
        #--------------------
        # Refer to the settings window to update
        # ALL of the other XnatMetadataEdtiors.
        #--------------------
        self.MODULE.XnatSettingsWindow.updateSettingWidgets()


        
        
    def update(self):
        """ Updates the contents of the listWidget
            by referring to the XnatSettingsFile.
        """

        #--------------------
        # Get all of the saved items from the XnatSettingsFile
        # then reset the listWidget, adding the saved items.
        #--------------------
        try:
            xnatHost = self.MODULE.XnatLoginMenu.hostDropdown.currentText
            customMetadataItems = self.MODULE.XnatSettingsFile.getTagValues(xnatHost, self.MODULE.GLOBALS.makeCustomMetadataTag(self.xnatLevel))
            self.listWidget.clear()
            self.listWidget.addItems(customMetadataItems)
            
        except Exception, e:
            pass
            


        #--------------------
        # Call parent 'update'
        #--------------------
        super(XnatCustomMetadataEditor, self).update()



        #--------------------
        # Adjust item flags depending
        # on the 'currItemType'.
        #--------------------
        if self.currItemType == 'label':
            self.itemFlags = 1 | 32
        for i in range(0, self.listWidget.count):
            self.listWidget.item(i).setFlags(self.itemFlags)
            

            
            
    def onAddButtonClicked(self):
        """ Callback when the addButton is clicked.
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
        # metadata.
        #-------------------- 
        xnatHost = self.MODULE.XnatLoginMenu.hostDropdown.currentText
        customMetadataItems = self.MODULE.XnatSettingsFile.getTagValues(xnatHost, self.MODULE.GLOBALS.makeCustomMetadataTag(self.xnatLevel))

        tagDict = {self.MODULE.GLOBALS.makeCustomMetadataTag(self.xnatLevel) : [lineText] + customMetadataItems}
        self.MODULE.XnatSettingsFile.setTagValues(xnatHost, tagDict)


        
        #--------------------
        # Clear the lineEdit.
        #-------------------- 
        self.lineEdit.clear()


        
        #--------------------
        # Update all the settingsWidgets.
        #-------------------- 
        self.MODULE.XnatSettingsWindow.updateSettingWidgets()


        

    def setEditLineVisible(self, visible):
        """ Allows the editline to be displayed
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


            

    def onItemClicked(self, listWidgetItem):
        """ Runs class-specific callbacks for
            when an item in the listWidget is clicked.
            Also refers to the parent 'onItemClicked'
            function.
        """

        #--------------------
        # Call parent 'onItemClicked'
        #-------------------- 
        super(XnatCustomMetadataEditor, self).onItemClicked(listWidgetItem)


        
        #--------------------
        # Update the edit widgets.
        #-------------------- 
        self.deleteButton.setEnabled(True)
        self.addButton.setEnabled(False)
        self.lineEdit.clear()


        

    def onLineEditFocused(self, *args):
        """ Callback for when the user
            focuses on the lineEdit.
            Toggles the edit buttons accordingly.
        """
        if self.listWidget.currentItem():
            self.listWidget.currentItem().setSelected(False)
        self.addButton.setEnabled(True)
        self.deleteButton.setEnabled(False)
        


