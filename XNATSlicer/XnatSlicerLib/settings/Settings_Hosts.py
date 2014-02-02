# application
from __main__ import qt

# external
from MokaUtils import *

# module
from XnatSlicerGlobals import *
from XnatSlicerUtils import *
from Settings import *



        
class Settings_Hosts(Settings):
    """ 
    Settings_Hosts is the Settings pertaining to
    tracking and saving the various XnatHosts, and also
    saving these settings to the XnatSlicerFile.  

    All 'Settings' subclasses
    are to be displaed in the 'SettingsWindow' class.
    """

    

    def setup(self):
        """
        """

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
        self.hostTable = HostTable(clickCallback = \
                                   self.__onHostRowClicked)

        
        
        #--------------------
        # Shared popup objects.
        # The function that creates them
        # are outside of the scope of the class
        # and are made by a UI-making function below.
        #--------------------
        self.urlLine, self.nameLine, self.setDefault, \
        self.usernameLine = makeSharedHostModalObjects(self)
        
        
        
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

        
        
        
    def __onHostRowClicked(self):
        """ Callback for when a user clicks on a given item
            within the host editor.
        """
        try:
            self.setButtonStates(self.hostTable.currentRowItems['name'])
        except:
            #print "No row items selected"
            return
        
        
        
        
    def setButtonStates(self, hostName):   
        """ Enables / Disables button based upon the editable
            quality of the host (provided by the 'hostName'
            argument).  Some hosts cannot be modified.
        """
        ##print hostName, self.SettingsFile.isModifiable(hostName) 
        if self.SettingsFile.isModifiable(hostName):
            self.deleteButton.setEnabled(True)
            self.editButton.setEnabled(True)
        else:
            self.deleteButton.setEnabled(False)
            self.editButton.setEnabled(True)



        
    def loadHosts(self):     
        """ Communicates with Settings to load the stored hosts.
        """
        #MokaUtils.debug.lf("LOAD HOSTS")
        #--------------------
        # Empty host table in the editor.
        #--------------------
        self.hostTable.clear()


        
        #--------------------
        # Get host dictionary from Settings
        #--------------------
        hostDictionary = self.SettingsFile.getHostsDict()  
        
        
        
        #--------------------
        # Iterate through dictionary and apply text to the host table.
        #--------------------
        for name in hostDictionary:
            
            #
            # Apply style if default
            #
            setModfiable = [True, True]
            if not self.SettingsFile.isModifiable(name):
                setModfiable = [False, False]
                
            #
            # Add name and URL to host table.
            #
            self.hostTable.addNameAndUrl(name, hostDictionary[name], 
                                         setModfiable)

            #
            # Get curr username
            #
            currName = self.SettingsFile.getCurrUsername(name)
            
            #
            # If there's a username, add it to the hostTable
            #
            if len(currName) > 0:
                self.hostTable.addUsername(currName) 




    
    def rewriteHost(self):
        """ As stated.  Deletes the host then 
            calls on the internal "writeHost" function.
        """
        #MokaUtils.debug.lf('')
        self.SettingsFile.deleteHost(self.prevName)
        self.prevName = None
        self.writeHost()
        self.Events.runEventCallbacks('SETTINGS_FILE_MODIFIED', 
                                      self.__class__.__name__)


    
    
    def deleteHost(self):
        """ 
        Removes the host from the settings file
        and then reloads the HostTable, which
        refers to the SettingsFile.
        """
        #MokaUtils.debug.lf()
        #--------------------
        # Delete the selected host by
        # removing it from the settings.
        #--------------------
        hostStr = self.hostTable.currentRowItems
        deleted = self.SettingsFile.deleteHost(hostStr['name'])
        

        
        #--------------------
        # Reload all hosts back into the table
        # from the SettingsFile.
        #--------------------
        if deleted: 
            self.loadHosts()
            #self.Events.runEventCallbacks('HOSTDELETED')
            


            
        #--------------------
        # Close popup
        #--------------------
        self.currModal.close()
        self.currModal = None
        self.Events.runEventCallbacks('SETTINGS_FILE_MODIFIED', 
                                      self.__class__.__name__)


    
    
    def writeHost(self):
        """ Writes the host both to the SettingsFile,
            then reloads the hosts from the file.
        """

        #MokaUtils.debug.lf()
        #--------------------
        # Check if the nameLine's name is
        # is modifiable as per the SettingsFile.
        #--------------------
        modifiable = self.SettingsFile.isModifiable(self.nameLine.text.\
                                                    strip(""))



        #--------------------
        # Determine if enetered host was set to default,
        # which means it will be loaded up on startup.
        #--------------------
        modStr = str(modifiable)
        checkStr = str(self.setDefault.isChecked())
        
        
        
        #--------------------
        # Save Host to SettingsFile.
        #--------------------
        self.SettingsFile.saveHost(self.nameLine.text, 
                                              self.urlLine.text, 
                                              isModifiable = modifiable, 
                                              isDefault = self.setDefault.\
                                   isChecked())

        

        #--------------------
        # Set host to default if checkbox is checked.
        # 'Default' means it will be the host that is
        # selected automatically on loadup.
        #--------------------
        if self.setDefault.isChecked():
            self.SettingsFile.setDefault(self.nameLine.text)   



        #--------------------
        # Set hosts associated username accordingly.
        #--------------------
        if self.usernameLine.text != "":
            self.SettingsFile.setCurrUsername(self.nameLine.text, 
                                              self.usernameLine.text)



        #--------------------
        # Reload hosts from the SettingsFile.
        #--------------------
        #self.Events.runEventCallbacks('HOSTADDED')
        self.loadHosts() 



        #--------------------
        # Close popup
        #--------------------
        self.currModal.close()
        self.currModal = None

        self.Events.runEventCallbacks('SETTINGS_FILE_MODIFIED', 
                                      self.__class__.__name__)



    def updateFromSettings(self):
        """
        """
        #MokaUtils.debug.lf()
        #MokaUtils.debug.lf("UPDATE", self.__class__.__name__)
        self.loadHosts()

    

    def showEditHostModal(self):
        """ As described.
        """
        #MokaUtils.debug.lf()
        self.currModal = makeEditHostModal(self)
        self.currModal.setWindowModality(1)
        self.currModal.show()  
        
        
        
        
    def showDeleteHostModal(self, message=None):
        """ As described.
        """
        #MokaUtils.debug.lf()
        self.currModal = makeDeleteHostModal(self)
        self.currModal.show()   
            
            
            
            
    def showAddHostModal(self):  
        """ As described.
        """ 
        #MokaUtils.debug.lf()
        self.currModal = makeAddHostModal(self)
        self.currModal.show()


    

    def makeFrame(self):
        """ Makes the widget frame.
        """
        #MokaUtils.debug.lf()
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

    def __init__(self, clickCallback = None): 
        """ Init function.
        """
        super(HostTable, self).__init__(self)
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
        MokaUtils.debug.lf("PRINT ALL:", self.rowCount, self.columnCount)


        

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
        try:
            if self.trackedItems[rowNumber]:
                returner = {}
                for key, item in self.trackedItems[rowNumber].iteritems():
                    returner[key] = item.text()
                
                return returner
        except Exception, e:
            MokaUtils.debug.lf("Skipping (Ref: '%s')"%(str(e)))
            pass


        

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
        # feeding into the SettingsFile.
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
            item.setFont(XnatSlicerGlobals.LABEL_FONT)



        #--------------------
        # Call on the QTableWidget 'setItem' function.
        #--------------------
        self.setItem(self.rowCount-1, self.getColumn('name'), hostNameItem)
        self.setItem(self.rowCount-1, self.getColumn('url'), hostUrlItem)
        self.setItem(self.rowCount-1, self.getColumn('stored login'), \
                     usernameItem)
 


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
        self.setItem(self.rowCount-1, self.getColumn('stored login'), \
                     self.trackedItems[self.rowCount-1]['stored login'])





        
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
    addHostModal.setWindowModality(1)



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
    if not hostEditor.SettingsFile.isModifiable(selHost['name']):
        hostEditor.nameLine.setReadOnly(True)
        hostEditor.nameLine.setFont(XnatSlicerGlobals.LABEL_FONT_ITALIC)
        hostEditor.nameLine.setEnabled(False)
        hostEditor.urlLine.setReadOnly(True)
        hostEditor.urlLine.setFont(XnatSlicerGlobals.LABEL_FONT_ITALIC)
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
    if hostEditor.SettingsFile.isDefault(hostEditor.nameLine.text):
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
    hostEditor.usernameLine.setText(hostEditor.\
                                    SettingsFile.getCurrUsername(\
                                                hostEditor.nameLine.text))
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
    editHostModal.setWindowModality(1)


    
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
    deleteHostModal.setWindowModality(1)



    #--------------------
    # Button Connectors
    #--------------------
    cancelButton.connect("clicked()", deleteHostModal.close)
    okButton.connect("clicked()", hostEditor.deleteHost) 
    
    return deleteHostModal

    



def makeButtons(hostEditor):
    """ As described.
    """
    addButton = XnatSlicerUtils.generateButton(iconOrLabel = 'Add', 
                                         toolTip = "Need tool-tip.", 
                                         font = XnatSlicerGlobals.LABEL_FONT,
                                         size = qt.QSize(90, 20), 
                                         enabled = True)
    editButton = XnatSlicerUtils.generateButton(iconOrLabel = 'Edit', 
                                          toolTip = "Need tool-tip.", 
                                          font = XnatSlicerGlobals.LABEL_FONT,
                                          size = qt.QSize(90, 20), 
                                          enabled = True)
    deleteButton = XnatSlicerUtils.generateButton(iconOrLabel = 'Delete', 
                                            toolTip = "Need tool-tip.", 
                                            font = XnatSlicerGlobals.LABEL_FONT,
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
    usernameLine.setFont(XnatSlicerGlobals.LABEL_FONT_ITALIC) 

    return urlLine, nameLine, setDefault, usernameLine 
