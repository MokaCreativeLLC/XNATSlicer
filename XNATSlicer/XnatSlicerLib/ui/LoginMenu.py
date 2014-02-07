# python
import os

# application
from __main__ import qt, slicer

# external
from MokaUtils import *




class LoginMenu(qt.QWidget):
    """ 
    LoginMenu is the class that handles all of the UI to the XnatIo related to 
    logging in to a given  XNAT host.  
    Handles UI for loggin into XNAT as well as settings by 
    linking to button clicks to external methods in the
    XnatIo.
    """

    FONT_NAME =  "Arial"
    FONT_SIZE =  10
    LABEL_FONT =  qt.QFont(FONT_NAME, FONT_SIZE, 10, False)        
    LABEL_FONT_BOLD =  qt.QFont(FONT_NAME, FONT_SIZE, 100, False)
    LABEL_FONT_ITALIC =  qt.QFont(FONT_NAME, FONT_SIZE, 10, True)

    EVENT_TYPES = [
        'HOSTSELECTED',
        'MANAGEHOSTSCLICKED'
    ]

    def __init__(self, parent = None, MODULE = None, Setting = None):
        """ 
        @param parent: The parent widget to attach to.
        @type parent: qt.QWidget
        
        @param MODULE: The XNATSlicer module
        @type MODULE: XnatSlicerWidget
        """

        super(LoginMenu, self).__init__(self)


        self.MODULE = MODULE
        self.Setting = Setting

        
        #--------------------
        # Set relevant variables.
        #--------------------
        self.currHostUrl = None
        self.currHostName = None
        self.currHostAddress = None
        self.XnatHosts = None
        self.hostLoggedIn = False
        self.defaultPasswordText = "Password"
        self.defaultUsernameText = "Login"

        
        #--------------------
        # Create Username and password lines 
        #--------------------
        self.usernameLabel, self.passwordLabel, \
        self.usernameLine, self.passwordLine = makeCredentialsWidgets(self)


        
        #--------------------
        # Create login button
        #--------------------
        self.loginButton = makeLoginButton(self)
        

        
        #--------------------
        # Create host dropdown.
        #--------------------
        self.hostDropdown = makeHostDropdown(self)
        


        #--------------------
        # Create settings button.
        #--------------------
        self.manageHostsButton = makeManageHostsButton(self)  
        

        
        #--------------------
        # Create login layout.
        #--------------------
        self.loginLayout = makeLoginLayout(self)



        #--------------------
        # Set event connections.
        #--------------------

        self.usernameLine.installEventFilter(self)
        self.usernameLine.setObjectName("XnatUsernameLine")
        self.passwordLine.installEventFilter(self)
        self.passwordLine.setObjectName("XnatPasswordLine")
        self.passwordLine.connect('returnPressed()', 
                                  self.simulateLoginClicked)
        self.hostDropdown.connect('currentIndexChanged(const QString&)', 
                                  self.__onHostSelected)
        self.manageHostsButton.connect('pressed()', 
                                       self.__onManageHostsButtonClicked)



        #--------------------
        # Define the widgets list.
        #--------------------
        self.Events = MokaUtils.Events(self.EVENT_TYPES)
        self.setLayout(self.loginLayout)




    def updateFromSettings(self):
        """
        """
        #MokaUtils.debug.lf("Update from settings")
        self.loadDefaultHost()



        
    def eventFilter(self, eventObject, event):
        """
        """
        
        if event.type() == qt.QEvent.FocusIn:
            if str(eventObject.objectName).strip() == \
               str(self.passwordLine.objectName).strip():
                self.onPasswordLineFocused()
            elif str(eventObject.objectName).strip() == \
                 str(self.usernameLine.objectName).strip():
                self.onUsernameLineFocused()
            
    
            

        
    def resetHostDropdown(self):
        """ Clears the host dropdown widget and then
            loads the defaults from the Settings object.
        """
    
        #--------------------
        # Clear host dropdown
        #--------------------
        self.hostDropdown.clear()
        #MokaUtils.debug.lf("Update from settings")
        
        
        #--------------------
        # Get the dictionary from settings and the key to 
        # the dropdown widget.
        #--------------------
        #print "\n\n"
        hostDict = self.MODULE.SettingsFile.getHostsDict()
        slicer.app.processEvents()
        #MokaUtils.debug.lf("hostDict", hostDict)
        for name in hostDict:  
            if self.hostDropdown.findText(name) == -1:
                self.hostDropdown.addItem(name) 
        
        
        



            
    def loadDefaultHost(self):
        """ Loads the default host into the 
            hostDropdown from Settings.
        """
        #MokaUtils.debug.lf("LOAD DEFAULT HOST")
        #--------------------
        # Reset the dropdown.
        #--------------------
        self.resetHostDropdown()

        

        #--------------------
        # Set host dropdown to default stored hostName.
        #--------------------
        defaultName = self.MODULE.SettingsFile.getDefault()
        self.setHost(defaultName)


        
        #--------------------
        # Populate the stored user into the username line.
        #--------------------
        self.__onHostSelected()
        self.populateCurrUser()

        


    def setHost(self, hostName):
        """ Sets the current intem in the hostDropdown
            to the name specified in the 'hostName' argument by
            looping through all of its visible items.
        """

        if not hostName:
            return
        for i in range(0, self.hostDropdown.maxVisibleItems):
            if self.hostDropdown.itemText(i).lower() == \
               hostName.strip().lower():
                self.hostDropdown.setCurrentIndex(i)
                self.currHostName = self.hostDropdown.itemText(i)
                break
            

            
        
    def populateCurrUser(self):
        """ 
        If "Remember username" is clicked, queries the settings 
        file to bring up the username saved.
        """

        #--------------------
        # Does the username exist in the settings file?
        #--------------------
        if self.currHostName: 
            currUser = self.MODULE.SettingsFile.getCurrUsername(\
                                                self.currHostName).strip()
            #
            # If it does, and it's not a '' string, then apply it to the
            # usernameLine....
            #
            if len(currUser) > 0:  
                self.usernameLine.setText(currUser)
            #
            # Otherwise apply a default string to the username line.
            #
            else: 
                self.usernameLine.setText(self.defaultUsernameText)


                
        #--------------------        
        # If not, populate with default line
        #--------------------
        else:
            self.usernameLine.setText(self.defaultUsernameText)       




    def simulateLoginClicked(self):
        """ Equivalent of clicking the login button.
        """
        self.loginButton.animateClick()


        

        
    def __onManageHostsButtonClicked(self):
        """ 
        Event function for when the settings button
        is clicked.  Displays the SettingsPopup 
        from the MODULE.
        """
        self.Events.runEventCallbacks('MANAGEHOSTSCLICKED', 'host manager')
        



        
    def onUsernameLineFocused(self):
        """ Event function for when the username line is edited.
        """     
        if self.defaultUsernameText in str(self.usernameLine.text): 
            self.usernameLine.setText("")   


            
            
    def onPasswordLineFocused(self):  
        """ Event function for when the password line is edited.
        """     
        ##print "PWD FOCUSED"
        if self.defaultPasswordText in str(self.passwordLine.text): 
            self.passwordLine.setText('')
        self.passwordLine.setStyleSheet("color: black")
        self.passwordLine.setEchoMode(2)



        
    def __onHostSelected(self):
        """ 
        Event function for when the hostDropdown is clicked.  
        Loads the stored username into the username line, 
        if it's there.
        
        @param name: Dummy variable for the host name.
        @param type: name
        """
        
        selHostName = self.hostDropdown.currentText

        
        #--------------------
        # Clear the password line if the newly selected
        # host is different from the previous
        #--------------------
        if (self.currHostName != selHostName):
            self.passwordLine.setText('')

        self.currHostName = selHostName
        if self.hostDropdown.currentText:    
            self.populateCurrUser()

        #MokaUtils.debug.lf("ON HOST SELECTED: ", selHostName,
        #                   self.hostDropdown.currentText)

        self.Events.runEventCallbacks('HOSTSELECTED', selHostName)


            
            


def makeCredentialsWidgets(LoginMenu):
    """ Makes the username and password lines
        and lables.
    """

    #--------------------
    # Username + password label and lines.
    #--------------------
    usernameLabel = qt.QLabel('username:')
    usernameLabel.setFont(LoginMenu.LABEL_FONT_BOLD)
    
    passwordLabel = qt.QLabel('password:')
    passwordLabel.setFont(LoginMenu.LABEL_FONT_BOLD)    
    
    usernameLine = qt.QLineEdit()   
    passwordLine = qt.QLineEdit() # encrypted
    
    usernameLine.setFixedWidth(100)
    passwordLine.setFixedWidth(100)

    
    #--------------------
    # Sets aesthetics.
    #--------------------
    usernameLine.setText(LoginMenu.defaultUsernameText)
    usernameLine.setFont(LoginMenu.LABEL_FONT_ITALIC)
    passwordLine.setFont(LoginMenu.LABEL_FONT_ITALIC) 

    passwordLine.setStyleSheet("color: lightgray")
    passwordLine.setText(LoginMenu.defaultPasswordText)
    passwordLine.setCursorPosition(0)


        
    return usernameLabel, passwordLabel, usernameLine, passwordLine



        
def makeHostDropdown(LoginMenu):
    """ Initiates the dropdown that allows the user to select hosts
    """
    
    hostDropdown = qt.QComboBox()
    hostDropdown.setFont(LoginMenu.LABEL_FONT)
    hostDropdown.toolTip = "Select Xnat host"
    return hostDropdown



        
def makeLoginButton(LoginMenu):
    """ Connects the login to the first treeView call
    """
    
    plt = qt.QPalette()
    plt.setColor(qt.QPalette().Button, qt.QColor(255,255,255))  
    loginButton = qt.QPushButton("Login")
    loginButton.setFont(LoginMenu.LABEL_FONT)    
    loginButton.toolTip = "Login to selected Xnat host"    
    loginButton.setFixedSize(48, 24)
    return loginButton




def makeManageHostsButton(LoginMenu):
    """ Initiates the button aesthetics for the button 
        that opens the manage hosts popup 
    """
    
    manageHostsButton = qt.QPushButton('+')
    manageHostsButton.toolTip = "Manage XNAT hosts."
    manageHostsButton.setFixedSize(24, 24)

    return manageHostsButton




def makeLoginLayout(LoginMenu):
    """ As stated.
    """

    #--------------------
    # Username/Password Row
    #--------------------
    credentialsRow = qt.QHBoxLayout()
    credentialsRow.addWidget(LoginMenu.manageHostsButton)
    credentialsRow.addWidget(LoginMenu.hostDropdown)
    credentialsRow.addSpacing(20)
    credentialsRow.addWidget(LoginMenu.usernameLine)
    credentialsRow.addWidget(LoginMenu.passwordLine)
    credentialsRow.addWidget(LoginMenu.loginButton)
    

    
    #--------------------
    # Everything related to logging in.
    #--------------------
    loginLayout = qt.QGridLayout() 
    loginLayout.addLayout(credentialsRow, 0,2)
    
    return loginLayout
