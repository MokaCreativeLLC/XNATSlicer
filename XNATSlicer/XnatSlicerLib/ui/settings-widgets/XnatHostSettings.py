from __main__ import vtk, qt, ctk, slicer

import os
import glob
import sys

from XnatSettings import *




comment = """
XnatHostSettings is the XnatSettings pertaining to
tracking and saving the various XnatHosts, and also
saving these settings to the XnatSlicerFile.  


All 'XnatSettings' subclasses
are to be displaed in the 'XnatSettingsWindow' class.


TODO:
"""



        
class XnatHostSettings(XnatSettings):
    """ Descriptor above.
    """

  
    def __init__(self, title, MODULE):
        """ Init function.
        """
        
        #--------------------
        # Call parent init
        #--------------------
        super(XnatHostSettings, self).__init__(title, MODULE)
        


        #--------------------
        # Add section Label
        #--------------------
        bLabel = qt.QLabel('Manage Hosts')
        self.masterLayout.addWidget(bLabel)
        self.masterLayout.addSpacing(8)

        
        
        #--------------------
        # The currModal variable 
        # tracks the various input modals related
        # to entering and deleting hosts.
        #--------------------
        self.currModal = None
        
        
        
        #--------------------
        # Add Host table (class below)
        #--------------------      
        self.hostTable = HostTable(self.MODULE, clickCallback = self.hostRowClicked)

        
        
        #--------------------
        # Shared popup objects.
        # The function that creates them
        # are outside of the scope of the class
        # and are made by a UI-making function below.
        #--------------------
        self.urlLine, self.nameLine, self.setDefault, self.usernameLine = makeSharedHostModalObjects(self)
        
        
        
        #--------------------
        # Add Buttons and connect their events.
        # Like the variables above, they are created in a 
        # separate UI function.
        #--------------------
        self.addButton, self.editButton, self.deleteButton = makeButtons(self)
        self.addButton.connect('clicked()', self.showAddHostModal)     
        self.editButton.connect('clicked()', self.showEditHostModal) 
        self.deleteButton.connect('clicked()', self.showDeleteHostModal)  
        

        
        #--------------------
        # Make frame for setup window
        #--------------------
        self.makeFrame()
        
        

    
        #--------------------
        # Set layout for entire frame and
        # its aesthetics.
        #--------------------
        self.frame.setLayout(self.masterLayout)
        self.setWidget(self.frame)
        self.frame.setMinimumWidth(600)
        self.frame.setMaximumWidth(10000)
        
        
        #--------------------
        # Load hosts into host list
        #--------------------
        self.loadHosts()

        
        
        
    def hostRowClicked(self):
        """ Callback for when a user clicks on a given item
            within the host editor.
        """
        self.setButtonStates(self.hostTable.currentRowItems['name'])
        
        
        
        
    def setButtonStates(self, hostName):   
        """ Enables / Disables button based upon the editable
            quality of the host (provided by the 'hostName'
            argument).  Some hosts cannot be modified.
        """
        #print hostName, self.MODULE.XnatSettingsFile.isModifiable(hostName) 
        if self.MODULE.XnatSettingsFile.isModifiable(hostName):
            self.deleteButton.setEnabled(True)
            self.editButton.setEnabled(True)
        else:
            self.deleteButton.setEnabled(False)
            self.editButton.setEnabled(True)



        
    def loadHosts(self):     
        """ Communicates with XnatSettings to load the stored hosts.
        """

        #--------------------
        # Empty host table in the editor.
        #--------------------
        self.hostTable.clear()


        
        #--------------------
        # Get host dictionary from XnatSettings
        #--------------------
        hostDictionary = self.MODULE.XnatSettingsFile.getHostNameAddressDictionary()  
        
        
        
        #--------------------
        # Iterate through dictionary and apply text to the host table.
        #--------------------
        for name in hostDictionary:
            
            #
            # Apply style if default
            #
            setModfiable = [True, True]
            if not self.MODULE.XnatSettingsFile.isModifiable(name):
                setModfiable = [False, False]
                
            #
            # Add name and URL to host table.
            #
            self.hostTable.addNameAndUrl(name, hostDictionary[name], setModfiable)

            #
            # Get curr username
            #
            currName = self.MODULE.XnatSettingsFile.getCurrUsername(name)
            
            #
            # If there's a username, add it to the hostTable
            #
            if len(currName) > 0:
                self.hostTable.addUsername(currName) 




    
    def rewriteHost(self):
        """ As stated.  Deletes the host then 
            calls on the internal "writeHost" function.
        """
        self.MODULE.XnatSettingsFile.deleteHost(self.prevName)
        self.prevName = None
        self.writeHost()


    
    
    def deleteHost(self):
        """ Removes the host from the settings file
            and then reloads the HostTable, which
            refers to the XnatSettingsFile.
        """
        
        #--------------------
        # Delete the selected host by
        # removing it from the settings.
        #--------------------
        hostStr = self.hostTable.currentRowItems
        deleted = self.MODULE.XnatSettingsFile.deleteHost(hostStr['name'])
        

        
        #--------------------
        # Reload all hosts back into the table
        # from the XnatSettingsFile.
        #--------------------
        if deleted: 
            self.loadHosts()
            self.MODULE.XnatLoginMenu.loadDefaultHost()


            
        #--------------------
        # Close popup
        #--------------------
        self.currModal.close()
        self.currModal = None


    
    
    def writeHost(self):
        """ Writes the host both to the XnatSettingsFile,
            then reloads the hosts from the file.
        """

        #--------------------
        # Check if the nameLine's name is
        # is modifiable as per the XnatSettingsFile.
        #--------------------
        modifiable = self.MODULE.XnatSettingsFile.isModifiable(self.nameLine.text.strip(""))



        #--------------------
        # Determine if enetered host was set to default,
        # which means it will be loaded up on startup.
        #--------------------
        modStr = str(modifiable)
        checkStr = str(self.setDefault.isChecked())
        
        
        
        #--------------------
        # Save Host to XnatSettingsFile.
        #--------------------
        self.MODULE.XnatSettingsFile.saveHost(self.nameLine.text, 
                                              self.urlLine.text, 
                                              isModifiable = modifiable, 
                                              isDefault = self.setDefault.isChecked())

        

        #--------------------
        # Set host to default if checkbox is checked.
        # 'Default' means it will be the host that is
        # selected automatically on loadup.
        #--------------------
        if self.setDefault.isChecked():
            self.MODULE.XnatSettingsFile.setDefault(self.nameLine.text)   



        #--------------------
        # Set hosts associated username accordingly.
        #--------------------
        if self.usernameLine.text != "":
            self.MODULE.XnatSettingsFile.setCurrUsername(self.nameLine.text, self.usernameLine.text)



        #--------------------
        # Reload hosts from the XnatSettingsFile.
        #--------------------
        self.MODULE.XnatLoginMenu.loadDefaultHost()
        self.loadHosts() 



        #--------------------
        # Close popup
        #--------------------
        self.currModal.close()
        self.currModal = None




    
    def showEditHostModal(self):
        """ As described.
        """
        self.currModal = makeEditHostModal(self)
        self.currModal.setWindowModality(2)
        self.currModal.show()  
        
        
        
        
    def showDeleteHostModal(self, message=None):
        """ As described.
        """
        self.currModal = makeDeleteHostModal(self)
        self.currModal.show()   
            
            
            
            
    def showAddHostModal(self):  
        """ As described.
        """ 
        self.currModal = makeAddHostModal(self)
        self.currModal.show()


    

    def makeFrame(self):
        """ Makes the widget frame.
        """

        #--------------------
        # Layout for top part of frame (host list)
        #--------------------
        self.masterLayout.addWidget(self.hostTable)
        
        
        
        #--------------------
        # Layout for bottom part of frame (buttons)
        #--------------------
        buttonLayout = qt.QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.addButton)
        buttonLayout.addWidget(self.editButton)
        buttonLayout.addWidget(self.deleteButton)   
        self.masterLayout.addLayout(buttonLayout)


        

                  
class HostTable(qt.QTableWidget):
    """ Inherits qt.QTableWidget to list the hosts in the 
        SettingsModal in a table format.  QTableWidgets are
        a bit quirky compared to other QListWidgets, some of 
        those quirks are accommodated for below.
    """

    def __init__(self, MODULE, clickCallback = None): 
        """ Init function.
        """
        super(HostTable, self).__init__(self)
        self.MODULE = MODULE
        self.clickCallback = clickCallback
        self.setup()
        



        
    def setup(self):
        """ Setup function on __init__.
        """
        
        #--------------------
        # Setup columns.
        #--------------------
        self.columnNames = ['Name', 'Url', 'Stored Login']
        self.setSelectionBehavior(1)
        self.setColumnCount(len(self.columnNames))
        self.setHorizontalHeaderLabels(self.columnNames)     
        self.setColumnWidth(0, 150)
        self.setColumnWidth(1, 200)
        self.setColumnWidth(2, 150)


        
        #--------------------
        # Set aesthetics.
        #--------------------       
        self.setShowGrid(False)
        self.verticalHeader().hide()
        self.currentRowNumber = None
        self.currentRowItems = None      



        #--------------------
        # Tracked items tracks all of the contents
        # within the table.  
        #
        # NOTE: The reason this exists is because QTableWidget
        # takes ownership of the items that are fed into it, 
        # making the items disappear afterwards.  As a result,
        # the items need to be tracked and stored within the class
        # that utilizes the QTableWidget.
        #
        # See here for more information:
        # http://www.qtcentre.org/threads/12499-QTableWidget-set-items-disappear-after-new-insertion
        #--------------------     
        self.trackedItems = {}


        
        #--------------------
        # Connect interaction event.
        #--------------------   
        self.connect('currentCellChanged(int, int, int, int)', self.onCurrentCellChanged)

        


    def printAll(self):
        """ Prints the row/column count of the hostTable.
        """
        print self.MODULE.utils.lf(), "PRINT ALL:", self.rowCount, self.columnCount 


        

    def getRowItems(self, rowNumber = None):
        """ Returns a dictionary of the row items
            with a key-value pairing of column name
            to value.
        """

        #--------------------
        # Determine the current row number.
        #--------------------
        if not rowNumber:
            rowNumber = self.currentRowNumber


            
        #--------------------
        # This happens after a clear and 
        # reinstantiation of rows.
        #--------------------
        if rowNumber == -1:
            rowNumber = 0



        #--------------------
        # If the row number's items are tracked (they should be)
        # then construct and return the row dictionary.
        #
        # For more information on why 'trackedItems' exists,
        # see __init__ function.
        #--------------------
        if self.trackedItems[rowNumber]:
            returner = {}
            for key, item in self.trackedItems[rowNumber].iteritems():
                returner[key] = item.text()
                
            return returner


        

    def clear(self):
        """ Clears the table of all values, then reapplies
            then reapplies the column headers.
        """
        #--------------------
        # We have to delete self.trackedItems
        # because of a very bizarre memory management
        # polciy set forth by QTableWidget
        #--------------------
        del self.trackedItems
        self.trackedItems = {}
        self.setRowCount(0)

            
    

            
    def onCurrentCellChanged(self, rowNum, colNum, oldRow, oldCol):
        """  Callback when the cell changes.
        """

        #--------------------
        # Set the current row number and
        # currentRowItems accordingly.
        #--------------------
        self.currentRowNumber = rowNum
        self.currentRowItems = self.getRowItems()
        self.clickCallback()


        

        
    def getColumn(self, colName):
        """ Returns the column index if it's name matches the
            'colName' argument.
        """
        for i in range(0, self.columnCount):
            if self.horizontalHeaderItem(i).text().lower() == colName.lower():
                return i


            

    def addNameAndUrl(self, name, url, setModfiable = [True, True]):
        """ Adds a name and url to the table by adding a 
            new row.
        """

        #--------------------
        # Create the modifiable flags corresponding with
        # the 'setModifiable' argument for
        # feeding into the XnatSettingsFile.
        #--------------------
        flags = []
        for state in setModfiable:
            if state:
                flags.append(None)
            else:
                flags.append(1)

                

        #--------------------
        # Add the hostName and hostUrl items
        # accordingly.
        #--------------------                
        hostNameItem = qt.QTableWidgetItem(name)
        if flags[0]:
            hostNameItem.setFlags(flags[0])
        
        hostUrlItem = qt.QTableWidgetItem(url)
        if flags[1]:
            hostUrlItem.setFlags(flags[1])


            
        #--------------------
        # Add the username item.
        #--------------------    
        usernameItem = qt.QTableWidgetItem('No username stored.')


        
        #--------------------
        # Turn sorting off.
        #--------------------         
        self.setSortingEnabled(False)


        
        #--------------------
        # NOTE: QTableWiget quirk: we have to 
        # set the rowcount of the table beforehand.
        #--------------------     
        self.setRowCount(self.rowCount + 1)
    


        #--------------------
        # Add the new items to the 'trackedItems'
        # variable otherwise the table will destroy them
        # and the items will disappear immediately on
        # add.
        #--------------------
        self.trackedItems[self.rowCount-1] = {}
        self.trackedItems[self.rowCount-1]['name'] = hostNameItem
        self.trackedItems[self.rowCount-1]['url'] = hostUrlItem
        self.trackedItems[self.rowCount-1]['stored login'] = usernameItem



        #--------------------
        # Set the added items' aeshetics.
        #--------------------
        for key, item in self.trackedItems[self.rowCount-1].iteritems():
            item.setFont(self.MODULE.GLOBALS.LABEL_FONT)



        #--------------------
        # Call on the QTableWidget 'setItem' function.
        #--------------------
        self.setItem(self.rowCount-1, self.getColumn('name'), hostNameItem)
        self.setItem(self.rowCount-1, self.getColumn('url'), hostUrlItem)
        self.setItem(self.rowCount-1, self.getColumn('stored login'), usernameItem)
 


        #--------------------
        # Again, turn sorting off.
        #--------------------  
        self.setSortingEnabled(False)
        


        
        
    def addUsername(self, username):
        """ Adds username to row, storing within the class
            'trackedItems' and adding it to the table.
            
            For more information on 'trackedItems' please
            see its declaration in the __init__ function.
        """
        self.trackedItems[self.rowCount-1]['stored login'].setText(username)
        self.setItem(self.rowCount-1, self.getColumn('stored login'), self.trackedItems[self.rowCount-1]['stored login'])





        
###########################################################################################################
#
#                UI FUNCTIONS
#
# These exist because the tend to clutter up
# __init__ functions.  They deal primarily with 
# setting up, aesthetics of various QWidgets and modals needed
# for adding hosts.
#
###########################################################################################################

def makeAddHostModal(hostEditor):
    """ As stated. 
    """
    
    #--------------------
    # Clear shared object lines
    #--------------------
    hostEditor.nameLine.clear()
    hostEditor.urlLine.clear()



    #--------------------    
    # Buttons
    #--------------------
    saveButton = qt.QPushButton("OK")
    cancelButton = qt.QPushButton("Cancel")



    #--------------------
    # Create for line editors
    #--------------------
    currLayout = qt.QFormLayout()
    currLayout.addRow("Name:", hostEditor.nameLine)
    currLayout.addRow("URL:", hostEditor.urlLine)
    currLayout.addRow(hostEditor.setDefault)



    #--------------------
    # Create layout for buttons
    #--------------------
    buttonLayout = qt.QHBoxLayout()
    buttonLayout.addStretch(1)
    buttonLayout.addWidget(cancelButton)
    buttonLayout.addWidget(saveButton)



    #--------------------
    # Combine both layouts
    #--------------------
    masterForm = qt.QFormLayout()    
    masterForm.addRow(currLayout)
    masterForm.addRow(buttonLayout)



    #--------------------
    # Make window
    #--------------------
    addHostModal = qt.QDialog(hostEditor.addButton)
    addHostModal.setWindowTitle("Add Host")
    addHostModal.setFixedWidth(300)
    addHostModal.setLayout(masterForm)
    addHostModal.setWindowModality(2)



    #--------------------
    # Clear previous host
    #--------------------
    hostEditor.prevName = None

    

    #--------------------
    # Button Connectors
    #--------------------
    cancelButton.connect("clicked()", addHostModal.close)
    saveButton.connect("clicked()", hostEditor.writeHost)   

    
    return addHostModal




def makeEditHostModal(hostEditor):
    """ As stated.
    """

    #--------------------
    # Get selected strings from host list.
    #--------------------
    selHost = hostEditor.hostTable.currentRowItems


    
    #--------------------
    # Populate the line edits from selecting strings.
    #--------------------
    hostEditor.nameLine.setText(selHost['name'])
    hostEditor.urlLine.setText(selHost['url'])



    #--------------------
    # Prevent editing of default host. 
    #--------------------
    if not hostEditor.MODULE.XnatSettingsFile.isModifiable(selHost['name']):
        hostEditor.nameLine.setReadOnly(True)
        hostEditor.nameLine.setFont(hostEditor.MODULE.GLOBALS.LABEL_FONT_ITALIC)
        hostEditor.nameLine.setEnabled(False)
        hostEditor.urlLine.setReadOnly(True)
        hostEditor.urlLine.setFont(hostEditor.MODULE.GLOBALS.LABEL_FONT_ITALIC)
        hostEditor.urlLine.setEnabled(False)


        
    #--------------------
    # Otherwise, go ahead.
    #--------------------
    else:
        hostEditor.nameLine.setEnabled(True)
        hostEditor.urlLine.setEnabled(True)



    #--------------------
    # Buttons.
    #--------------------
    cancelButton = qt.QPushButton("Cancel")   
    saveButton = qt.QPushButton("OK")



    #--------------------
    # Layouts.
    #--------------------
    currLayout = qt.QFormLayout()
    hostEditor.prevName = hostEditor.nameLine.text
    currLayout.addRow("Edit Name:", hostEditor.nameLine)
    currLayout.addRow("Edit URL:", hostEditor.urlLine)



    #--------------------
    # Default checkbox if default.
    #--------------------
    if hostEditor.MODULE.XnatSettingsFile.isDefault(hostEditor.nameLine.text):
        hostEditor.setDefault.setCheckState(2)



    #--------------------
    # Labels.
    #--------------------
    spaceLabel = qt.QLabel("")
    unmLabel = qt.QLabel("Stored Username:")


    
    #--------------------
    # Layouts.
    #--------------------
    currLayout.addRow(hostEditor.setDefault)
    hostEditor.usernameLine.setText(hostEditor.MODULE.XnatSettingsFile.getCurrUsername(hostEditor.nameLine.text))
    currLayout.addRow(spaceLabel)
    currLayout.addRow(unmLabel)
    currLayout.addRow(hostEditor.usernameLine)
    
    buttonLayout = qt.QHBoxLayout()
    buttonLayout.addStretch(1)
    buttonLayout.addWidget(cancelButton)
    buttonLayout.addWidget(saveButton)
    
    masterForm = qt.QFormLayout()    
    masterForm.addRow(currLayout)
    masterForm.addRow(buttonLayout)


    
    #--------------------
    # The modal.
    #--------------------
    editHostModal = qt.QDialog(hostEditor.addButton)
    editHostModal.setWindowTitle("Edit Host")
    editHostModal.setFixedWidth(300)
    editHostModal.setLayout(masterForm)
    editHostModal.setWindowModality(2)


    
    #--------------------
    # Button Connectors
    #--------------------
    cancelButton.connect("clicked()", editHostModal.close)
    saveButton.connect("clicked()", hostEditor.rewriteHost) 

    return editHostModal




def makeDeleteHostModal(hostEditor):
    """ As stated.
    """

    #--------------------
    # get selected strings from host list
    #--------------------
    selHost = hostEditor.hostTable.currentRowItems


    
    #--------------------
    # Buttons
    #--------------------
    okButton = qt.QPushButton("OK")
    cancelButton = qt.QPushButton("Cancel")



    #--------------------
    # Labels
    #--------------------
    messageLabel = qt.QTextEdit()
    messageLabel.setReadOnly(True)
    messageLabel.insertPlainText("Are you sure you want to delete the host ") 
    messageLabel.setFontItalic(True)
    messageLabel.setFontWeight(100)    
    messageLabel.insertPlainText(selHost['name'])

    messageLabel.setFontWeight(0)   
    messageLabel.insertPlainText(" ?")
    messageLabel.setFixedHeight(40)
    messageLabel.setFrameShape(0)


    
    #--------------------
    # Layouts
    #--------------------
    currLayout = qt.QVBoxLayout()
    currLayout.addWidget(messageLabel)
    currLayout.addStretch(1)
    
    buttonLayout = qt.QHBoxLayout()
    buttonLayout.addStretch(1)
    buttonLayout.addWidget(cancelButton)
    buttonLayout.addWidget(okButton)
    
    masterForm = qt.QFormLayout()    
    masterForm.addRow(currLayout)
    masterForm.addRow(buttonLayout)



    #--------------------
    # Window
    #--------------------
    deleteHostModal = qt.QDialog(hostEditor.addButton)
    deleteHostModal.setWindowTitle("Delete Host")
    deleteHostModal.setLayout(masterForm)
    deleteHostModal.setWindowModality(2)



    #--------------------
    # Button Connectors
    #--------------------
    cancelButton.connect("clicked()", deleteHostModal.close)
    okButton.connect("clicked()", hostEditor.deleteHost) 
    
    return deleteHostModal

    



def makeButtons(hostEditor):
    """ As described.
    """
    addButton = hostEditor.MODULE.utils.generateButton(iconOrLabel = 'Add', 
                                                                               toolTip = "Need tool-tip.", 
                                                                               font = hostEditor.MODULE.GLOBALS.LABEL_FONT,
                                                                               size = qt.QSize(90, 20), 
                                                                               enabled = True)
    editButton = hostEditor.MODULE.utils.generateButton(iconOrLabel = 'Edit', 
                                                                               toolTip = "Need tool-tip.", 
                                                                               font = hostEditor.MODULE.GLOBALS.LABEL_FONT,
                                                                               size = qt.QSize(90, 20), 
                                                                               enabled = True)
    deleteButton = hostEditor.MODULE.utils.generateButton(iconOrLabel = 'Delete', 
                                                                               toolTip = "Need tool-tip.", 
                                                                               font = hostEditor.MODULE.GLOBALS.LABEL_FONT,
                                                                               size = qt.QSize(90, 20), 
                                                                               enabled = True)
    
    deleteButton.setEnabled(False)
    editButton.setEnabled(False)  

    return addButton, editButton, deleteButton




def makeSharedHostModalObjects(hostEditor):
    """ Makes commonly shared UI objects for the Add, Edit popups.
    """
    urlLine = qt.QLineEdit()
    nameLine = qt.QLineEdit()
    setDefault = qt.QCheckBox("Set As Default?")
    usernameLine = qt.QLineEdit()
        
    urlLine.setEnabled(True)
    nameLine.setEnabled(True) 
    usernameLine.setFont(hostEditor.MODULE.GLOBALS.LABEL_FONT_ITALIC) 

    return urlLine, nameLine, setDefault, usernameLine 
