from __main__ import vtk, ctk, qt, slicer
import datetime, time

import os
import sys
import re
import urllib2

from XnatUtils import *




comment = """
XnatFolderMaker is used for creating new folders 
within XNAT (projects, subjects, experiments).  
It utilizes the class 'XnatIo' to create the folders 
within XNAT.

TODO : 
"""




class XnatFolderMaker(qt.QWidget):
    """ Described above.
    """
    
    def __init__(self, parent, MODULE = None):
        """ Init function.
        """

        self.MODULE = MODULE


        
        #--------------------
        # Call parent init.
        #--------------------   
        super(XnatFolderMaker, self).__init__()



        #--------------------
        # Adjust window features.
        #--------------------
        self.setWindowTitle("Add Folder to Xnat")
        self.setWindowModality(2)



        #--------------------
        # Hide the widget initially.
        #--------------------   
        self.hide()



        #--------------------
        # Set fixed width.
        #--------------------   
        self.setFixedWidth(500)
        self.setFixedHeight(250)



        #--------------------
        # Make the xsiList for experiment
        # creation.
        #--------------------
        self.xsiList = qt.QComboBox()
        self.xsiList.addItems([key for key, value in self.MODULE.GLOBALS.XNAT_XSI_TYPES.iteritems()])


        
        #--------------------
        # Displayable wigets.
        #--------------------  
        self.levelLabels = {}
        self.nameLabels = {}
        self.lineEdits = {}
        self.errorLines = {}
        self.levelLayouts = {}
        self.labelLineStacks = {}
        self.levelRows = {}


        
        #--------------------
        # Make the buttons: 
        # create, cancel,
        # etc.
        #--------------------
        self.addButton = qt.QPushButton()
        self.addButton.setText("Add")
        self.addButton.setEnabled(False)
        self.cancelButton = qt.QPushButton()
        self.cancelButton.setText("Cancel")
        buttonRow = qt.QDialogButtonBox()
        buttonRow.addButton(self.cancelButton, 2)
        buttonRow.addButton(self.addButton, 0)


        
        #-------------------
        # Create the keys in the displayable widgets.
        #--------------------
        self.addFolderXnatLevels = ['projects', 'subjects', 'experiments']
        for level in self.addFolderXnatLevels:

            #
            # Labels (name and level)
            #
            self.levelLabels[level] = qt.QLabel(self)
            self.levelLabels[level].setFixedHeight(25)
            self.nameLabels[level] = qt.QLabel(self)
            self.nameLabels[level].setFixedHeight(25)

            #
            # Line edits
            #
            self.lineEdits[level] = qt.QLineEdit(self)
            self.lineEdits[level].installEventFilter(self)
            self.lineEdits[level].setFixedHeight(25)
            
            #
            # Error lines
            #
            self.errorLines[level] = qt.QLabel(self)
            self.errorLines[level].setTextFormat(1)
            self.errorLines[level].setFixedHeight(25)

            #
            # Make the label-line stacks, adjusting
            # for 'experiments' as necessary.
            #
            self.labelLineStacks[level] = qt.QStackedLayout()
            if level == 'experiments':
                experimentRow = qt.QHBoxLayout()
                experimentRow.addWidget(self.xsiList)
                experimentRow.addWidget(self.lineEdits[level])
                experimentWidget = qt.QWidget()
                experimentWidget.setLayout(experimentRow)
                self.labelLineStacks[level].addWidget(experimentWidget)
            else:
                self.labelLineStacks[level].addWidget(self.nameLabels[level])
                self.labelLineStacks[level].addWidget(self.lineEdits[level])                

            #
            # make row widgets
            #
            self.levelRows[level] = qt.QWidget(self)
            levelRowLayout = qt.QGridLayout()
            levelRowLayout.addWidget(self.levelLabels[level], 0,0) 
            levelRowLayout.addLayout(self.labelLineStacks[level], 0, 1)
            levelRowLayout.addWidget(self.errorLines[level], 1, 1) 
            self.levelRows[level].setLayout(levelRowLayout)


        
        #--------------------
        # Connect button click events.
        #--------------------
        buttonRow.connect('clicked(QAbstractButton*)', self.onAddButtonClicked)



        #--------------------
        # Make the mainLayout and add all widgets.
        #--------------------
        self.mainLayout = qt.QVBoxLayout()
        for level in self.addFolderXnatLevels:
            self.mainLayout.addWidget(self.levelRows[level])
        self.mainLayout.addStretch()
        self.mainLayout.addWidget(buttonRow)
        self.setLayout(self.mainLayout)



        
    def eventFilter(self, widget, event):
        """ Filter for dropdown interaction
            and line edit interaction.  

            Right now this only applies to line edits: 
            making sure there are no invalid characters
            or the name in the line edit isn't taken.
        """
                
        #--------------------
        # Callback for the lineEdit.
        #--------------------
        for level, lineEdit in self.lineEdits.iteritems():
            if widget == lineEdit:
                self.onLineEditTextChanged(level, lineEdit.text)

                

            
    def show(self):
        """ Display the XnatFolderMaker widget.
        """

        #--------------------
        # Clear the window's items.
        #--------------------
        for key, widget in self.lineEdits.iteritems():
            widget.clear()



        #--------------------
        # Get the current XNAT level of 
        # the selected node in the viewer.
        #
        # If no node is selected, we just 
        # assume it's projects
        #--------------------
        try:
            selectedXnatLevel = self.MODULE.XnatView.currentItem().text(self.MODULE.XnatView.columns['XNAT_LEVEL']['location'])
        except Exception, e:
            selectedXnatLevel = 'projects'


            
        #--------------------
        # Get all of the existing values
        # in the current selected XnatLevel
        #--------------------        
        self.levelList = []
        def addToList(item):
            self.levelList.append(item.text(self.MODULE.XnatView.columns['MERGED_LABEL']['location']))

        if selectedXnatLevel == 'projects':
            self.MODULE.XnatView.loopProjectNodes(addToList)
        else:
            self.MODULE.XnatView.loopChildNodes(self.MODULE.XnatView.currentItem().parent(), addToList)



        #--------------------
        # If the selected level is deeper than
        # 'experiments' we default back to 'experiments.'
        #--------------------
        if not selectedXnatLevel in self.addFolderXnatLevels:
            selectedXnatLevel = 'experiments'
            
        

        #--------------------
        # Show all levelRows that pertain to adding
        # a folder at the current level.
        #
        # For instance, if the selected XnatView node
        # is at 'projects' then we hide the lineRows
        # pertaining to 'subjects' and 'experiments.'
        #-------------------- 
        selectedLevelIndex = self.addFolderXnatLevels.index(selectedXnatLevel)

        #
        # Adjust the window height depending on the
        # selectedLevelIndex
        #
        self.setFixedHeight(100 + 80 * selectedLevelIndex)
        
        for level, levelRow in self.levelRows.iteritems():

            #
            # Hide the error lines at first.
            #
            self.errorLines[level].setText('')

            
            #
            # Show the lineEdit if the selectedLevel matches
            # the level.
            #
            if self.addFolderXnatLevels.index(level) == selectedLevelIndex:
                levelRow.show()

                #
                # Shows the lineEdit
                #
                self.labelLineStacks[level].setCurrentIndex(1)

                #
                # Set the relevant text.
                #
                self.nameLabels[level].setText('')
                self.levelLabels[level].setText('Add <i>%s</i>:     '%(level[:-1]))
                

            #
            # Show the label level if less than the selectedLevelIndex
            #
            elif self.addFolderXnatLevels.index(level) < selectedLevelIndex:
                levelRow.show()

                #
                # Shows the nameLabel
                #
                self.labelLineStacks[level].setCurrentIndex(0)
                self.lineEdits[level].setText('')
                
                #
                # Set the nameLabel text value by getting the XnatView's
                # current item, and then matching the parents with the
                # 'level'
                #
                itemParents = self.MODULE.XnatView.getParents(self.MODULE.XnatView.currentItem())
                for item in itemParents:
                    if level == item.text(self.MODULE.XnatView.columns['XNAT_LEVEL']['location']):
                        self.nameLabels[level].setText('<b>%s</b>'%(item.text(self.MODULE.XnatView.columns['MERGED_LABEL']['location'])))
                self.levelLabels[level].setText('<i>%s</i>:      '%(level[:-1].title()))
                

            #
            # Otherwise hide the levelRow.
            #
            else:
                levelRow.hide()


                
        #--------------------
        # Show the widget window.
        #--------------------
        qt.QWidget.show(self)
            



    def onAddButtonClicked(self, button):
        """ Callback if the create button is clicked. Communicates with
            XNAT to create a folder. Details below.  
        """
        
        #--------------------
        # If add is clicked....
        #--------------------
        if 'add' in button.text.lower():

            #
            # Clear error lines
            #
            for key, errorLine in self.errorLines.iteritems():
                errorLine.setText('')            

            #
            # Construct URI based on XNAT rules.
            #
            xnatUri = ''
            for level in self.addFolderXnatLevels:
                if not self.levelRows[level].isHidden():
                    xnatUri += '/' + level + '/'

                    #
                    # Get the plainText values of the nameLine
                    # and the lineEdit associated with the level.
                    #
                    nameText = self.MODULE.utils.toPlainText(self.nameLabels[level].text)
                    lineText = self.MODULE.utils.toPlainText(self.lineEdits[level].text)
                    
                    #
                    # Choose the text that does not have
                    # a zero length.
                    #
                    if len(nameText) != 0:
                        xnatUri += nameText 
                    else:
                        xnatUri += lineText

                    #
                    # Special case for experiments
                    #
                    if level == 'experiments':
                        xnatUri += '?xsiType=' + self.MODULE.GLOBALS.XNAT_XSI_TYPES[self.xsiList.currentText]
                    
                else:
                    break
                #
                # IMPORTANT: Add the xsi for experiments
                #
                #xnatUri += '?xsiType=' + self.MODULE.GLOBALS.XNAT_XSI_TYPES[self.xsiList.currentText]

            #
            # Make folder in XnatIo, processEvents
            #
            print ("%s creating %s "%(self.MODULE.utils.lf(), xnatUri))
            self.MODULE.XnatIo.makeFolder(xnatUri)
            slicer.app.processEvents()
            
            #
            # Close window
            #
            self.close()

            #
            # Select new folder in XnatView
            #
            self.MODULE.XnatView.selectItem_byUri(xnatUri.split('?')[0])
            


        #--------------------
        # Close window if 'cancel' pressed.
        #--------------------        
        elif 'cancel' in button.text.lower():
            self.close()


            
            
    def onLineEditTextChanged(self, level, text):
        """ Validates the line edit text for the folder
            to add:
            -Checks for invalid characters.
            -Checks if the name is already taken.
        """


        #--------------------
        # Begin validation of text.
        #--------------------
        if len(text.strip(" ")) > 0:

            #
            # Show error if there are invalid characters
            #
            invalidMsg = self.checkForInvalidCharacters(text)
            if invalidMsg != None:
                self.errorLines[level].show()
                self.errorLines[level].setText('<font color=\"red\">%s</font>'%(invalidMsg))
                self.addButton.setEnabled(False)
                return
            else:
                self.errorLines[level].setText('')
                
            #
            # Show error if the lineEdit.text 
            # is an already taken name
            #
            try:
                for itemText in self.levelList:
                    if text.lower() == itemText.lower():
                        self.errorLines[level].show()
                        self.errorLines[level].setText("<font color=\"red\">The %s name '%s' is already taken.</font>"%(level[:-1].title(), text))
                        self.addButton.setEnabled(False)
                        return
                else:
                    self.errorLines[level].setText('')
            except Exception, e:
                pass

        else:
            self.addButton.setEnabled(False)
            
        #--------------------
        # If no errors, enable the add button.
        #--------------------
        self.addButton.setEnabled(True)
            
                


    def checkForInvalidCharacters(self, text):
        """ Removes the invalid name characters from
            a given string.
        
            From: http://stackoverflow.com/questions/5698267/efficient-way-to-search-for-invalid-characters-in-python
        """

        invalidChars = " .;:[<>/{}[\]~`]"

        for char in invalidChars:
            if char in text:
                return "The following characters are not allowed: %s"%(invalidChars)

        if ' ' in text:
            return "Spaces are not allowed."
        else:
            return None
