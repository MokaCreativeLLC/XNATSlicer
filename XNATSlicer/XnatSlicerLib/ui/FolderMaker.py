# application
from __main__ import qt
from __main__ import slicer

# external
from Xnat import *
from MokaUtils import *

# module
from XnatSlicerUtils import *
from XnatSlicerGlobals import *




class FolderMaker(qt.QWidget):
    """
    FolderMaker is used for creating new folders
    within XNAT at the projects, subjects, experiments levels.
    """

    def __init__(self, parent, MODULE):
        """ 
        @param parent: Parent widget.
        @type parent: qt.QWidget

        @param MODULE: The XNATSlicer module
        @type MODULE: XnatSlicerModule
        """

        self.MODULE = MODULE



        #--------------------
        # Call parent init.
        #--------------------
        super(FolderMaker, self).__init__(parent)



        #--------------------
        # Adjust window features.
        #--------------------
        self.setWindowTitle("Add Folder to Xnat")
        self.setWindowModality(1)



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
        self.xsiList.addItems([key for key, value in Xnat.xsi.DEFAULT_TYPES.iteritems()])



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
        self.levelTracker = {}
        self.nextLevelList = []



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



        #--------------------
        # Create widgets
        #--------------------
        self.__createWidgets()



        #--------------------
        # Connect button click events.
        #--------------------
        buttonRow.connect('clicked(QAbstractButton*)', self.__onAddButtonClicked)



        #--------------------
        # Make the mainLayout and add all widgets.
        #--------------------
        self.mainLayout = qt.QVBoxLayout()
        for level in self.xnatLevels:
            self.mainLayout.addWidget(self.levelRows[level])
        self.mainLayout.addStretch()
        self.mainLayout.addWidget(buttonRow)
        self.setLayout(self.mainLayout)



    def __createWidgets(self):
        """
        """
        levelInd = Xnat.path.DEFAULT_LEVELS.index(Xnat.path.HIGHEST_FOLDER_ADD_LEVEL)
        self.xnatLevels = Xnat.path.DEFAULT_LEVELS[:levelInd+1]
        for level in self.xnatLevels:

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
            self.errorLines[level].setFixedHeight(12)
            self.errorLines[level].setFont(qt.QFont(XnatSlicerGlobals.FONT_NAME, XnatSlicerGlobals.FONT_SIZE, 10, False)) 

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




    def show(self):
        """
        Inherits from qt.QWidget.
        Display the FolderMaker widget.
        """

        #--------------------
        # Clear the window's items.
        #--------------------
        for key, widget in self.lineEdits.iteritems():
            widget.clear()


        #--------------------
        # Get selected XNAT Level
        #--------------------
        selectedXnatLevel = self.__getSelectedXnatLevel()

  

        #--------------------
        # Store the level values
        #--------------------      
        self.__storeLevelValues(selectedXnatLevel)


        #--------------------
        # Create the window layout
        #--------------------  
        self.__createLayout(selectedXnatLevel)



        #--------------------
        # Show the widget window.
        #--------------------
        qt.QWidget.show(self)




    def eventFilter(self, widget, event):
        """ 
        Inherits from qt.QWidget -- does not
        need to be called programatically.
        Event filter for line edit interaction

        @param widget: The widget calling the event.
        @type widget: qt.QWidget

        @param MODULE: The XNATSlicer module
        @type MODULE: XnatSlicerModule        
        """
        for level, lineEdit in self.lineEdits.iteritems():
            if widget == lineEdit:
                self.__onLineEditTextChanged(level, lineEdit.text)





    def __getSelectedXnatLevel(self):
        """
        Get the current XNAT level of
        the selected node in the viewer.  If higher than 'experiments'
        we default to experiments
        If no node is selected, we just
        assume it's projects

        @return: The XNAT level valid for adding a folder. (Usually between 'projects' and 'experiments')
        @rtype: string
        """
        selectedXnatLevel = ''
        try:
            selectedXnatLevel = self.MODULE.View.currentItem().text(self.MODULE.View.columns['XNAT_LEVEL']['location'])
            if not selectedXnatLevel in self.xnatLevels:
                selectedXnatLevel = self.xnatLevels[-1]
        except Exception, e:
            selectedXnatLevel = 'projects'   

        return selectedXnatLevel




    def __createLayout(self, selectedXnatLevel):
        """
        Show all levelRows that pertain to adding
        a folder at the current level, and if needed
        the level below it.
        
        For instance, if the selected View node
        is at 'projects' then we hide the lineRows
        pertaining to 'experiments,' but not 'subjects'.
        
        @param selectedXnatLevel: The selected XNAT devel to derive the layout from.
        @type selectedXnatLevel: string
        """
        selectedLevelIndex = self.xnatLevels.index(selectedXnatLevel)
        nextLevelIndex = selectedLevelIndex + 1 if selectedLevelIndex < len(self.xnatLevels) - 1 else None


        #
        # Adjust the window height depending on the
        # selectedLevelIndex
        #
        height = 78 + 78 * (selectedLevelIndex + 1) if nextLevelIndex else 234
        self.setFixedHeight(height)

        for level, levelRow in self.levelRows.iteritems():

            #
            # Hide the error lines at first.
            #
            self.errorLines[level].setText('')
            #
            # Show the lineEdit if the selectedLevel matches
            # the level.
            #
            if self.xnatLevels.index(level) == selectedLevelIndex or self.xnatLevels.index(level) == nextLevelIndex:
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
            elif self.xnatLevels.index(level) < selectedLevelIndex:
                levelRow.show()

                #
                # Shows the nameLabel
                #
                self.labelLineStacks[level].setCurrentIndex(0)
                self.lineEdits[level].setText('')

                #
                # Set the nameLabel text value by getting the View's
                # current item, and then matching the parents with the
                # 'level'
                #
                itemParents = self.MODULE.View.getParents(self.MODULE.View.currentItem())
                for item in itemParents:
                    if level == item.text(self.MODULE.View.columns['XNAT_LEVEL']['location']):
                        self.nameLabels[level].setText('<b>%s</b>'%(item.text(self.MODULE.View.columns['MERGED_LABEL']['location'])))
                self.levelLabels[level].setText('<i>%s</i>:      '%(level[:-1].title()))


            #
            # Otherwise hide the levelRow.
            #
            else:
                levelRow.hide()



    def __onAddButtonClicked(self, button):
        """ 
        Callback if the create button is clicked. Communicates with
        XNAT to create a folder. Details below.

        @param button: The button that was clicked.
        @type button: qt.QAbstractButton
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
            for level in self.xnatLevels:
                nameText = XnatSlicerUtils.toPlainText(self.nameLabels[level].text)
                lineText = XnatSlicerUtils.toPlainText(self.lineEdits[level].text) 
                notEmpty = len(nameText) > 0 or len(lineText) > 0
                if not self.levelRows[level].isHidden() and notEmpty:
                    xnatUri += '/' + level + '/'
                    # Choose the text that does not have
                    # a zero length.
                    uriAdd = nameText if len(nameText) != 0 else lineText
                    xnatUri += uriAdd
                    # Special case for experiments
                    if level == 'experiments':
                        xnatUri += '?xsiType=' + Xnat.xsi.DEFAULT_TYPES[self.xsiList.currentText]
                else:
                    break
                    
            #
            # Put the folder in XNAT
            #
            self.MODULE.XnatIo.putFolder(xnatUri)
            slicer.app.processEvents()
            self.close()

            #
            # Select new folder in View
            #
            self.MODULE.View.selectItem_byUri(xnatUri.split('?')[0])



        #--------------------
        # Close window if 'cancel' pressed.
        #--------------------
        elif 'cancel' in button.text.lower():
            self.close()




    def __onLineEditTextChanged(self, level, text):
        """ 
        Validates the line edit text for the folder
        to add:
            - Checks for invalid characters.
            - Checks if the name is already taken.
            - Populates the line edits accordingly.

        @param level: The level of the pertaining lineEdit.
        @type level: string

        @param text:  The text in the pertaining lineEdit.
        @type text: string
        """

        
        #--------------------
        # Begin validation of text.
        #--------------------
        if len(text.strip(" ")) > 0 and self.MODULE.View.currentItem():

            #
            # Populate the lineEdits depending on nodeLevel
            #
            viewNodeText = self.MODULE.View.currentItem().text(self.MODULE.View.columns['MERGED_LABEL']['location'])
            viewNodeLevel = self.MODULE.View.currentItem().text(self.MODULE.View.columns['XNAT_LEVEL']['location'])
            if (viewNodeLevel.lower() != level.lower()) and (viewNodeLevel in self.xnatLevels):
                viewNodeLevelInd = self.xnatLevels.index(viewNodeLevel)
                lineEditLevelInd = self.xnatLevels.index(level)
                if viewNodeLevelInd > -1 and lineEditLevelInd > viewNodeLevelInd:
                    self.lineEdits[viewNodeLevel].setText(viewNodeText)

            #
            # Show error if there are invalid characters
            #
            invalidMsg = self.__checkInvalid(text)
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
                for itemText in self.levelTracker[level]:
                    if text.lower() == itemText.lower():
                        # Don't display an error if editing a level below the 
                        # current viewNode level
                        nextLevel = None
                        try:
                            nextLevel = self.xnatLevels[self.xnatLevels.index(level)+1]
                        except:
                            pass
                        if nextLevel and len(self.lineEdits[nextLevel].text) > 0:
                            continue

                        # Otherwise, display the error
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




    def __checkInvalid(self, text):
        """ 
        Removes the invalid name characters from
        a given string.
        
        From: http://stackoverflow.com/questions/5698267/efficient-way-to-search-for-invalid-characters-in-python

        @param text: The text to check for invalid characters.
        @type text: string

        @return: The error string explaining why 'text' is invalid.
        @rtype: string
        """

        invalidChars = " .;:[<>/{}[\]~`]"

        for char in invalidChars:
            if char in text:
                return "The following characters are not allowed: %s"%(invalidChars)

        if ' ' in text:
            return "Spaces are not allowed."
        else:
            return None



    def __storeLevelValues(self, selectedXnatLevel, storeNextLevel = True):
        """
        Store all of the existing values
        in the current selected XnatLevel.
        
        @param selectedXnatLevel: The selected XNAT devel to derive valus from
        @type selectedXnatLevel: string
        """
        self.levelTracker = {}
        self.levelTracker[selectedXnatLevel] = []
        def addToList(item):
            self.levelTracker[selectedXnatLevel].append(item.text(self.MODULE.View.columns['MERGED_LABEL']['location']))
        if selectedXnatLevel == 'projects':
            self.MODULE.View.loopProjectNodes(addToList)
        else:
            self.MODULE.View.loopChildren(self.MODULE.View.currentItem().parent(), addToList)


        if not storeNextLevel:
            return

        #--------------------
        # Get the next level attrs
        #--------------------
        levelInd = self.xnatLevels.index(selectedXnatLevel)
        if levelInd > -1 and levelInd < len(self.xnatLevels)-1:
            self.MODULE.View.onTreeItemExpanded(self.MODULE.View.currentItem())
            def addToSublevelList(item):                
                itemLevel = item.text(self.MODULE.View.columns['XNAT_LEVEL']['location'])
                itemValue = item.text(self.MODULE.View.columns['MERGED_LABEL']['location'])
                if not itemLevel in self.levelTracker: self.levelTracker[itemLevel] = []
                self.levelTracker[itemLevel].append(itemValue)

            self.MODULE.View.loopChildren(self.MODULE.View.currentItem(), addToSublevelList)
            
