# application
from __main__ import qt

# external
from MokaUtils import *

# module
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

    FONT_NAME =  "Arial"
    FONT_SIZE =  10
    FONT = qt.QFont(FONT_NAME, FONT_SIZE, 10, False) 
    FONT_ITALIC = qt.QFont(FONT_NAME, FONT_SIZE, 10, True)

    PERMANENT_HOSTS = {
        'Central': {
            'url': 'https://central.xnat.org',
            'username': ''
        }
    }
    DEFAULT_HOSTS = {
        'CNDA': {
            'url': 'https://cnda.wustl.edu',
            'username': ''
        }
    }
    DEFAULT_HOSTS = dict(DEFAULT_HOSTS.items() + PERMANENT_HOSTS.items())

    

    def setup(self):
        """
        Creates the necessary widgets for the Setting.
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
        self.lineEdits, \
        self.errorLines, \
        self.checkBoxes = makeSharedHostModalObjects(self)
        self.lineEdits['hostname'].connect('textChanged(const QString)',
                                           self.__onHostNameLineChanged)
        
        
        
        #--------------------
        # Add Buttons and connect their events.
        # Like the variables above, they are created in a 
        # separate UI function.
        #--------------------
        self.addButton, self.editButton, self.deleteButton = makeButtons(self)
        self.addButton.connect('clicked()', self.__showAddHostModal)     
        self.editButton.connect('clicked()', self.__showEditHostModal) 
        self.deleteButton.connect('clicked()', self.__showDeleteHostModal)  
        

        
        #--------------------
        # Make frame for setup window
        #--------------------
        self.__makeFrame()
        
        

    
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
        self.__loadHosts()

        
        
        
    def __onHostRowClicked(self):
        """ 
        Callback for when a user clicks on a given item
        within the host editor.
        """
        try:
            self.__setButtonStates(self.hostTable.currentRowItems['name'])
        except:
            #print "No row items selected"
            return
        
        
        
        
    def __setButtonStates(self, hostName = None):   
        """ 
        Enables / Disables button based upon the editable
        quality of the host (provided by the 'hostName'
        argument).  Some hosts cannot be modified.

        @param hostName: The name of the host to to apply the changes to.
        @type hostName: str
        """
        self.deleteButton.setEnabled(not hostName in self.PERMANENT_HOSTS)
        self.editButton.setEnabled(True)




        
    def __loadHosts(self):     
        """ 
        Loads the hosts into the table widget.
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
            # Add name and URL to host table.
            #
            self.hostTable.addNameAndUrl(name, hostDictionary[name])

            #
            # Get curr username
            #
            currName = self.SettingsFile.getCurrUsername(name)
            
            #
            # If there's a username, add it to the hostTable
            #
            if len(currName) > 0:
                self.hostTable.addUsername(currName) 
                



    def __stylizeErrorString(self, string):
        """
        Retruns a stylzed error string.

        @param string: The string to stylize.
        @type string: str

        @return: The stylized string.
        @rtype: str
        """
        return  '<font color=\"red\"><i>* %s</i></font>' %(string)
        



    def __onHostNameLineChanged(self, string):
        """
        As stated.

        @param string: The string of the hostname line.
        @type string: str
        """
        if not self.__validateHostName():
            if hasattr(self, 'saveButtons'):
                for key, button in self.saveButtons.iteritems():
                    button.setEnabled(False)
            return

        if hasattr(self, 'saveButtons'):
            for key, button in self.saveButtons.iteritems():
                button.setEnabled(True)




    def __validateHostName(self):
        """
        As stated.

        @return: The whether the host name is valid.
        @rtype: bool
        """
        nameLine = self.lineEdits['hostname'].text.strip("")
        if self.hostExists(nameLine):
            errorString = 'Host name \'%s\' is already taken.'%(nameLine)
            errorString = self.__stylizeErrorString(errorString)
            self.errorLines['hostname'].setText(errorString)
            return False
        self.errorLines['hostname'].setText('')
        return True
        


    
    def modifyHost(self):
        """ 
        As stated.
        """
        #MokaUtils.debug.lf()

        self.currModal.close()
        hostName = self.lineEdits['hostname'].text.strip()

        self.__setNonCriticalSettings()
        self.writeHost()
        self.Events.runEventCallbacks('SETTINGS_FILE_MODIFIED', 
                                      self.__class__.__name__, 
                                      'HOST_MODIFIED',
                                      hostName)



    def __setNonCriticalSettings(self):
        """
        """
        #--------------------
        # Set host to default if checkbox is checked.
        # 'Default' means it will be the host that is
        # selected automatically on loadup.
        #--------------------
        if self.checkBoxes['setdefault'].isChecked():
            self.SettingsFile.setDefault(self.lineEdits['hostname'].text)   

        #--------------------
        # Set hosts associated username accordingly.
        #--------------------
        if len(self.lineEdits['username'].text.strip()) != 0:
            self.SettingsFile.setCurrUsername(self.lineEdits['hostname'].text, 
                                              self.lineEdits['username'].text)


    
    
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
            self.__loadHosts()

            
        #--------------------
        # Close popup
        #--------------------
        self.currModal.close()
        self.currModal = None
        self.Events.runEventCallbacks('SETTINGS_FILE_MODIFIED', 
                                      self.__class__.__name__, 'HOST_DELETED', 
                                      hostStr['name'])



    def hostExists(self, hostName):
        """
        @param hostName: The host name to check
        @type hostName: str

        @return: Whether the host name exists.
        @rtype: bool
        """
        for rowDict, item in self.hostTable.trackedItems.iteritems():
            if item['name'].text() == hostName:
                return True
        return False



    
    def writeHost(self, runEvents = True):
        """ 
        Writes the host both to the SettingsFile,
        then reloads the hosts from the file.

        @param runEvents: Option to run event callbacks.
        @type runEvents: bool
        """
        #print "write host"
        #--------------------
        # Close popup
        #--------------------
        self.currModal.close()
        self.currModal = None


        #--------------------
        # Determine if enetered host was set to default,
        # which means it will be loaded up on startup.
        #--------------------
        modifiable = self.lineEdits['hostname'] in self.PERMANENT_HOSTS
        modStr = str(modifiable)
        checkStr = str(self.checkBoxes['setdefault'].isChecked())
        
        
        
        #--------------------
        # Save Host to SettingsFile.
        #--------------------
        self.SettingsFile.saveHost(self.lineEdits['hostname'].text, 
                                   self.lineEdits['url'].text, 
                                   isModifiable = modifiable, 
                                   isDefault = self.checkBoxes['setdefault'].\
                                   isChecked())

        self.__setNonCriticalSettings()


        #--------------------
        # Reload hosts from the SettingsFile.
        #--------------------
        #self.Events.runEventCallbacks('HOSTADDED')
        self.__loadHosts() 

        if runEvents:
            self.Events.runEventCallbacks('SETTINGS_FILE_MODIFIED', 
                                          self.__class__.__name__, 'HOST_ADDED',
                                          self.lineEdits['hostname'].text)



    def updateFromSettings(self):
        """
        Callback function for when the settings file changes.
        """
        #MokaUtils.debug.lf()
        #MokaUtils.debug.lf("UPDATE", self.__class__.__name__)
        self.__loadHosts()

    


    def __showEditHostModal(self):
        """ 
        Shows the modal that prompts the user to edit a given host.
        """
        #MokaUtils.debug.lf()
        self.currModal = makeEditHostModal(self)
        self.currModal.setWindowModality(1)
        self.currModal.show()  
        for key, line in self.errorLines.iteritems():
            line.setText('')
        
        
        
        
    def __showDeleteHostModal(self, message=None):
        """ 
        Shows the modal that prompts the user to delete a given host.
        """
        #MokaUtils.debug.lf()
        self.currModal = makeDeleteHostModal(self)
        self.currModal.show()   
            
            
            
            
    def __showAddHostModal(self):  
        """ 
        Shows the modal that prompts the user to add a given host.
        """ 
        #MokaUtils.debug.lf()
        self.currModal = makeAddHostModal(self)
        self.currModal.show()


    

    def __makeFrame(self):
        """ 
        Makes the widget frame.
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
    """ 
    Inherits qt.QTableWidget to list the hosts in the 
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
        """ 
        As stated.
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
        # http://www.qtcentre.org/threads/12499-QTableWidget-set- + 
        # items-disappear-after-new-insertion
        #--------------------     
        self.trackedItems = {}


        
        #--------------------
        # Connect interaction event.
        #--------------------   
        self.connect('currentCellChanged(int, int, int, int)', 
                     self.__onCurrentCellChanged)

        


    def printAll(self):
        """ 
        Prints the row/column count of the hostTable.
        """
        MokaUtils.debug.lf("PRINT ALL:", self.rowCount, self.columnCount)


        

    def getRowItems(self, rowNumber = None):
        """ 
        Returns a dictionary of the row items
        with a key-value pairing of column name
        to value.

        @param rowNumber: The row number to get the items from.  Defaults to 
           the stored 'currentRowNumber' if nothing provided.
        @type rowNumber: int
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
            #MokaUtils.debug.lf("Skipping (Ref: '%s')"%(str(e)))
            pass


        

    def clear(self):
        """ 
        Clears the table of all values, then reapplies
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

            
    

            
    def __onCurrentCellChanged(self, rowNum, colNum, oldRow, oldCol):
        """  
        Callback when the cell changes.

        @param rowNum: The row number of the changed cell.
        @type rowNum: int

        @param colNum: The column number of the changed cell.
        @type colNum: int

        @param oldRow: The previously focused cell's row number.
        @type oldRow: int

        @param oldCol: The previously focused cell's column number.
        @type oldCol: int
        """

        #--------------------
        # Set the current row number and
        # currentRowItems accordingly.
        #--------------------
        self.currentRowNumber = rowNum
        self.currentRowItems = self.getRowItems()
        self.clickCallback()


        

        
    def getColumn(self, colName):
        """ 
        Returns the column index if it's name matches the
        'colName' argument.

        @param colName: The column to get.
        @type colName: str
        """
        for i in range(0, self.columnCount):
            if self.horizontalHeaderItem(i).text().lower() == colName.lower():
                return i


            

    def addNameAndUrl(self, name, url):
        """ 
        Adds a name and url to the table by adding a 
        new row.

        @param name: The name of the host to add.
        @type name: str

        @param url: The url of the host to add.
        @type url: str
        """

                                                      
        #--------------------
        # Add the hostName and hostUrl items
        # accordingly.
        #--------------------                
        hostNameItem = qt.QTableWidgetItem(name)
        hostUrlItem = qt.QTableWidgetItem(url)


            
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
            item.setFont(Settings_Hosts.FONT)



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
        """ 
        Adds username to row, storing within the class
        'trackedItems' and adding it to the table.
        
        For more information on 'trackedItems' please
        see its declaration in the __init__ function.

        @param username: The username to add.
        @type username: str
        """
        self.trackedItems[self.rowCount-1]['stored login'].setText(username)
        self.setItem(self.rowCount-1, self.getColumn('stored login'), \
                     self.trackedItems[self.rowCount-1]['stored login'])





    
###########################################################################
#
#                                UI FUNCTIONS
#
# These exist because they tend to clutter up __init__ functions.  They deal 
# primarily with setting up the aesthetics of various QWidgets and modals 
# needed for adding hosts.
#
############################################################################
def makeAddHostModal(_Settings_Hosts):
    """
    Creates the modal for adding hosts.

    @param _Settings_Hosts: The widget that is the parent of the modal.
    @param _Settings_Hosts: Settings_Hosts
    """
    _Settings_Hosts.lineEdits['hostname'].clear()
    _Settings_Hosts.lineEdits['url'].clear()
    _Settings_Hosts.lineEdits['hostname'].setEnabled(True)
    _Settings_Hosts.lineEdits['url'].setEnabled(True)
    return genericHostEditor(_Settings_Hosts, _Settings_Hosts.writeHost)




def makeEditHostModal(_Settings_Hosts):
    """ 
    As stated.

    @type _Settings_Hosts: The widget that is the parent of the modal.
    @param _Settings_Hosts: Settings_Hosts
    """
    #print "Edit host modal"
    #--------------------
    # Get selected strings from host list.
    #--------------------
    selHost = _Settings_Hosts.hostTable.currentRowItems

    
    #--------------------
    # Populate the line edits from selecting strings.
    #--------------------
    _Settings_Hosts.lineEdits['hostname'].setText(selHost['name'])
    _Settings_Hosts.lineEdits['url'].setText(selHost['url'])


    #--------------------
    # Prevent editing of default host. 
    #--------------------
    if selHost['name'] in _Settings_Hosts.PERMANENT_HOSTS:
        _Settings_Hosts.lineEdits['hostname'].setEnabled(False)
        _Settings_Hosts.lineEdits['url'].setEnabled(False)
    else:
        _Settings_Hosts.lineEdits['hostname'].setEnabled(True)
        _Settings_Hosts.lineEdits['url'].setEnabled(True)
    _Settings_Hosts.prevName = _Settings_Hosts.lineEdits['hostname'].text


    #--------------------
    # Default checkbox if default.
    #--------------------
    if _Settings_Hosts.SettingsFile.isDefault(\
                                _Settings_Hosts.lineEdits['hostname'].text):
        _Settings_Hosts.checkBoxes['setdefault'].setCheckState(2)

    
    #--------------------
    # Layouts.
    #--------------------
    _Settings_Hosts.lineEdits['username'].setText(_Settings_Hosts.\
                                    SettingsFile.getCurrUsername(\
                                    _Settings_Hosts.lineEdits['hostname'].text))

    return genericHostEditor(_Settings_Hosts,_Settings_Hosts.modifyHost,'Edit')




def makeDeleteHostModal(_Settings_Hosts):
    """ 
    As stated.

    @param _Settings_Hosts: The widget that is the parent of the modal.
    @param _Settings_Hosts: Settings_Hosts
    """

    #--------------------
    # get selected strings from host list
    #--------------------
    selHost = _Settings_Hosts.hostTable.currentRowItems


    
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
    deleteHostModal = qt.QDialog(_Settings_Hosts.addButton)
    deleteHostModal.setWindowTitle("Delete Host")
    deleteHostModal.setLayout(masterForm)
    deleteHostModal.setWindowModality(1)



    #--------------------
    # Button Connectors
    #--------------------
    cancelButton.connect("clicked()", deleteHostModal.close)
    okButton.connect("clicked()", _Settings_Hosts.deleteHost) 
    
    return deleteHostModal

    



def makeButtons(_Settings_Hosts):
    """ 
    As described.

    @param _Settings_Hosts: The widget that is the parent of the modal.
    @param _Settings_Hosts: Settings_Hosts
    """
    addButton = XnatSlicerUtils.generateButton(iconOrLabel = 'Add', 
                                         toolTip = "Need tool-tip.", 
                                         font = Settings_Hosts.FONT,
                                         size = qt.QSize(90, 20), 
                                         enabled = True)
    editButton = XnatSlicerUtils.generateButton(iconOrLabel = 'Edit', 
                                          toolTip = "Need tool-tip.", 
                                          font = Settings_Hosts.FONT,
                                          size = qt.QSize(90, 20), 
                                          enabled = True)
    deleteButton = XnatSlicerUtils.generateButton(iconOrLabel = 'Delete', 
                                            toolTip = "Need tool-tip.", 
                                            font = Settings_Hosts.FONT,
                                            size = qt.QSize(90, 20), 
                                            enabled = True)
    
    deleteButton.setEnabled(False)
    editButton.setEnabled(False)  

    return addButton, editButton, deleteButton




def genericHostEditor(_Settings_Hosts, saveCallback, linePrefix = ''):
    """
    @param _Settings_Hosts: The widget that is the parent of the modal.
    @type _Settings_Hosts: Settings_Hosts

    @param saveCallback: The save button callback.
    @type saveCallback: function

    @param linePrefix: The to prefix to append to the line edit labels.
    @type linePrefix: str
    """
    
    if len(linePrefix) > 0:
        linePrefix += ' '

    #--------------------
    # Create for line editors
    #--------------------
    currLayout = qt.QFormLayout()
    currLayout.addRow(linePrefix + "Name:", 
                      _Settings_Hosts.lineEdits['hostname'])
    currLayout.addRow('', _Settings_Hosts.errorLines['hostname'])
    currLayout.addRow(linePrefix + 'URL:', _Settings_Hosts.lineEdits['url'])
    currLayout.addRow('', _Settings_Hosts.errorLines['url'])
    currLayout.addRow(_Settings_Hosts.checkBoxes['setdefault'])


    spaceLabel = qt.QLabel("")
    unmLabel = qt.QLabel("Stored Username:")

    currLayout.addRow(spaceLabel)
    currLayout.addRow(unmLabel)
    currLayout.addRow(_Settings_Hosts.lineEdits['username'])


    #--------------------    
    # Buttons
    #--------------------
    saveButton = qt.QPushButton("OK")
    cancelButton = qt.QPushButton("Cancel")

    _Settings_Hosts.saveButtons = {}
    _Settings_Hosts.saveButtons[linePrefix] = saveButton 
    _Settings_Hosts.cancelButtons = {}
    _Settings_Hosts.cancelButtons[linePrefix] = cancelButton 


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
    modal = qt.QDialog(_Settings_Hosts)
    modal.setWindowTitle("Add Host")
    modal.setFixedWidth(300)
    modal.setLayout(masterForm)
    modal.setWindowModality(1)


    #--------------------
    # Clear previous host
    #--------------------
    _Settings_Hosts.prevName = None

    

    #--------------------
    # Button Connectors
    #--------------------
    cancelButton.connect("clicked()", modal.close)
    saveButton.connect("clicked()", saveCallback)

    return modal




def makeSharedHostModalObjects(_Settings_Hosts):
    """ 
    Makes commonly shared UI objects for the Add, Edit popups.

    @param _Settings_Hosts: The widget that is the parent of the modal.
    @param _Settings_Hosts: Settings_Hosts
    """
    lineEdits = {}
    lineEdits['url'] = qt.QLineEdit()
    lineEdits['hostname'] = qt.QLineEdit()

    lineEdits['username'] = qt.QLineEdit()

    errorLines = {}
    errorLines['url'] = qt.QLabel()
    errorLines['hostname'] = qt.QLabel()
    errorLines['username'] = qt.QLabel()
        
    checkBoxes = {}
    checkBoxes['setdefault'] = qt.QCheckBox("Set As Default?")

    lineEdits['url'].setEnabled(True)
    lineEdits['hostname'].setEnabled(True) 
    lineEdits['username'].setFont(Settings_Hosts.FONT_ITALIC) 

    

    return lineEdits, errorLines, checkBoxes
