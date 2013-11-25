from __main__ import vtk, qt, ctk, slicer

import os
import glob
import sys
import shutil


from FingerTabWidget import *




comment = """
XnatSettingsWindow is the window for user-inputted XNAT settings, 
such as the Host Manager, Tree View Settings, etc.

TODO:
"""


        

class XnatSettingsWindow(FingerTabWidget):
    """ Popup window for managing user-inputted XnatSettings, 
        such as host names and default users.
    """
    
    def __init__(self, parent, MODULE):  
        """ Descriptor
        """      


        
        #--------------------
        # Call parent init.
        #--------------------
        super(XnatSettingsWindow, self).__init__(parent)

        self.setWindowTitle("XNATSlicer Settings")
 
        self.MODULE = MODULE
        self.settingsDict = {}


        #self.setTabPosition(2)

        #self.tabBar().setStyle(newStyle);


        
        #--------------------
        # Set sizes.
        #--------------------
        self.setFixedWidth(750)
        self.setFixedHeight(400)
        self.setWindowModality(0)
        self.hide()

        
        

        #self.masterLayout.addWidget(self.closeButton, 1, 1)



        self.settingsWidgets = []



        self.connect('currentChanged(int)', self.updateSettingWidgets)


        self.addCancelAndDoneButton()








        
        
        
    
        
    def addCancelAndDoneButton(self):
        """
        """
        self.doneButton = qt.QPushButton("Done")
        self.doneButton.connect('clicked()', self.hide)


        self.cancelButton = qt.QPushButton("Cancel")

        def restoreSettings():
            self.hide()
            self.MODULE.XnatSettingsFile.restorePreviousSettings()
            self.updateSettingWidgets()
            self.MODULE.XnatView.refreshColumns()
            
        self.cancelButton.connect('clicked()', restoreSettings)

        
        
        doneButtonRow = qt.QHBoxLayout()
        doneButtonRow.addStretch()
        doneButtonRow.addWidget(self.cancelButton)
        doneButtonRow.addWidget(self.doneButton)
        #doneButtonRow.addSpacing(5)



        
        doneButtonRow.setContentsMargins(5,5,5,5)
        self.mainWidgetLayout.addLayout(doneButtonRow)



        

    def updateSettingWidgets(self, tabIndex = None):
        """
        """


        
        #print "(Settings Window) SETTINGS WINDOW UPDATE:"
        #--------------------
        # Remove the metadata editor from the previous settings.
        #--------------------       
        try:
            for i in range(0, len(self.tabButtons)):
                for key, manager in self.settingsWidgets[i]['widget'].XnatMetadataManagers.iteritems(): 
                    #print "\n\tUpdating Manager for: ", key
                    manager.update()
        except Exception, e:
            print self.MODULE.utils.lf(), "XnatMetadataManagerObject error."
            print str(e)

            

            
        
    def showWindow(self, settingName = None, position = True):
        """ Creates a new window, adjusts aesthetics, then shows.
        """ 

        self.showSettingWidget(settingName)

        self.MODULE.XnatSettingsFile.backupCurrentSettings()
        
        #--------------------
        # Reposition window if argument is true.
        #--------------------
        if position:
            mainWindow = slicer.util.mainWindow()
            screenMainPos = mainWindow.pos
            x = screenMainPos.x() + mainWindow.width/2 - self.width/2
            y = screenMainPos.y() + mainWindow.height/2 - self.height/2
            self.move(qt.QPoint(x,y))

            

        #--------------------
        # Show the window.
        #--------------------
        self.show()
        self.raise_()
        

        
        #--------------------
        # Sync the Metadata settings dropdown with the login menu
        #--------------------
        self.MODULE.XnatMetadataSettings.update()
        self.updateSettingWidgets()
        


        

        

    def showSettingWidget(self, settingName):
        """ Changes the settingsAreaLayout index (a QStackedLayout)
            to the relevant settings widget based on the 'settingsName'
            argument.
        """

        if not settingName or len(settingName.strip()) == 0:
            self.setCurrentIndex(self.currentIndex)
            
        for i in range(0, len(self.settingsWidgets)):
            sDict = self.settingsWidgets[i]
            #print "***********", sDict, settingName
            if sDict['name'] == settingName:
                self.setCurrentIndex(i)
                return
        

            

        
    def doneClicked(self):
        """ Hide window if done was clicked.
        """
        #self.MODULE.XnatLoginMenu.loadDefaultHost()
        self.hide()


        


    def addSetting(self, settingName, widget = None):
        """ Inserts a setting into the settings window.
        """

        self.settingsWidgets.append({'widget': widget, 'name': settingName})
        self.addTab(widget, settingName)
        widget.update()



        
        
        
class SettingsLister(qt.QTextEdit):
    """ Inherits qt.QTextEdit to list the settings categories in the 
        SettingsWindow
    """


    
    def __init__(self, parent = None, selectCallback = None): 
        """ Init function.
        """
        qt.QTextEdit.__init__(self, parent)
        
        self.currText = None        
        self.setReadOnly(True)
        self.setFixedWidth(130)
        self.setLineWrapMode(False)
        self.setHorizontalScrollBarPolicy(1)
        self.selectCallback = selectCallback





    def onTextSelected(self):
        """ Runs the appropriate callbacks
            when text is selected.
            
        """
        cursor = self.textCursor()


        
        #--------------------
        # Set currText
        #--------------------
        if cursor.selectedText():
            self.currText = cursor.selectedText()



        #--------------------
        # Apply callbacks.
        #--------------------
        if self.selectCallback:
            self.selectCallback(self.currText)
            


        
    def mouseReleaseEvent(self, event):
        """ After the user clicks on a given line.
        """
        
        #--------------------
        # Define a cursor and select the line
        # that the cursor clicked on.
        #--------------------
        cursor = qt.QTextCursor(self.textCursor())
        cursor.select(qt.QTextCursor.LineUnderCursor)


        
        #--------------------
        # Select the text.
        #--------------------
        self.setTextCursor(cursor)



        #--------------------
        # Run event method.
        #--------------------
        self.onTextSelected()



            
    def selectSetting(self, settingName):
        """ Highlights a settingsName within the 
            text of the object.
        """
        
        #--------------------
        # Get the text of the widget
        # then find the index of the 'settingName'
        #--------------------
        text = self.toPlainText()
        settingNameIndex = text.find(settingName)



        #--------------------
        # Make a cursor, then manually highlight
        # the text based on the index name and text length.
        #--------------------
        cursor = qt.QTextCursor(self.textCursor())
        cursor.setPosition(settingNameIndex, 0);
        cursor.setPosition(settingNameIndex + len(settingName), 1)
        self.setTextCursor(cursor)

        

        #--------------------
        # Run event method.
        #--------------------
        self.onTextSelected()


            

        

        

    def getSettingsAsList(self):
        """ Returns a list of the settings as strings.
            Needs to break apart the linebreaks and clean
            the list before returning.
        """
        textList = self.toPlainText().split('\n')

        returnList = []
        for text in textList:
            if len(text) > 0:
                returnList.append(text)

        return returnList

    
        

    def addSettingToList(self, settingsName):
        """ Applies aesthetic scheme will adding name and Url.
        """
        #
        # Need to create a newline every time
        # we insert a settingsName into the settingsLister.
        #
        if len(self.toPlainText()) > 0:
            settingsName = '\n\n' + settingsName

            
        self.insertPlainText(settingsName) 


        
        
    def selectedText(self):
        """ Returns selected text.
        """ 
        return self.currText





class CustomTabStyle(qt.QProxyStyle):
    """
       Reinterpreted from C++ here:
       http://www.qtcentre.org/threads/13293-QTabWidget-customization?highlight=QTabWidget
    """


    def __init__(self):
        super(CustomTabStyle, self).__init__(self)

    
    def sizeFromContents(self, sizeType, option, size, widget):
        """
        """
        s = qt.QProxyStyle.sizeFromContents(sizeType, option, size, widget)
        if type == qt.QStyle.CT_TabBarTab:
            s.transpose()
        return s
    


    
    def drawControl(self, element, option, painter, widget):
        """
        """

        
        if element == qt.QStyle.CE_TabBarTabLabel:
            #if (const QStyleOptionTab *tab = qstyleoption_cast<const QStyleOptionTab *>(option))
            tab = qt.QStyleOptionTab
            opt.shape = qt.QTabBar.RoundedNorth
            qt.QProxyStyle.drawControl(element, opt, painter, widget)
            return       
        
            

            
        
        qt.QProxyStyle.drawControl(element, option, painter, widget)
    

