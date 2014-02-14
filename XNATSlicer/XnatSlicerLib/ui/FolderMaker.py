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
    FONT_NAME = 'Arial'
    FONT_SIZE = 10
    EVENT_TYPES = [
        'folderAdded',
    ] 

    def __init__(self, parent, View):
        """ 
        @param parent: Parent widget.
        @type parent: qt.QWidget

        @param View: The View module.
        @type View: View
        """

        #--------------------
        # Call parent init.
        #--------------------
        super(FolderMaker, self).__init__(parent)


        #--------------------
        # Params
        #--------------------
        self.View = View
        self.Events = MokaUtils.Events(self.EVENT_TYPES)
        self.xsiList = qt.QComboBox()
        self.xsiList.addItems([key for key, value in \
                               Xnat.xsi.DEFAULT_TYPES.iteritems()])
        self.levelLabels = {}
        self.lineEdits = {}
        self.errorLines = {}
        self.levelTracker = {}
        self.nextLevelList = []


        #--------------------
        # Inits
        #--------------------
        self.__initWindow()
        self.__createWidgets()
        self.__createButtons()
        self.__setLayout();




    def show(self):
        """
        Inherits from qt.QWidget.  Display the FolderMaker widget.
        """
        try:
            for key, widget in self.lineEdits.iteritems():
                widget.clear()
        except:
            pass
        selectedXnatLevel = self.__getSelectedXnatLevel()     
        self.__storeLevelValues(selectedXnatLevel) 
        
        # hide and show to bring back to front
        self.hide()
        qt.QWidget.show(self)
        # enable line edits
        for level, item in self.lineEdits.iteritems():
            item.setEnabled(True)
        # prepopulate based on viewer
        self.__prepopulate_ByViewSelection(selectedXnatLevel)




    def __prepopulate_ByViewSelection(self, level):
        """
        As stated.
        """
        # Only do this for non-projects
        levelInd = self.xnatLevels.index(level)
        if levelInd > 0:
            levelInd -= 1
            while levelInd > -1:
                #MokaUtils.debug.lf(self.levelTracker)
                currLevel = self.xnatLevels[levelInd]
                val = self.levelTracker[currLevel][0]
                self.lineEdits[currLevel].setText(val)
                self.lineEdits[currLevel].setEnabled(False)
                levelInd -= 1

                




    def eventFilter(self, widget, event):
        """ 
        Inherits from qt.QWidget -- does not need to be called programatically.
        Event filter for line edit interaction

        @param widget: The widget calling the event.
        @type widget: qt.QWidget

        @param event: The QT event.
        @type event: number     
        """
        for level, lineEdit in self.lineEdits.iteritems():
            # click or key release
            if (event.type() == 3 or event.type() == 7) and widget == lineEdit:
                #print "CLICK!"
                if widget.enabled:
                    self.__onLineEditTextChanged(level, lineEdit.text)





    def __getSelectedXnatLevel(self):
        """
        Get the current XNAT level of the selected node in the viewer.  If 
        higher than 'experiments' we default to experiments If no node is 
        selected, we just assume it's projects

        @return: The XNAT level valid for adding a folder. (Usually between 
            'projects' and 'experiments')
        @rtype: string
        """
        selectedXnatLevel = ''
        try:
            selectedXnatLevel = self.View.getItemLevel()
            if not selectedXnatLevel in self.xnatLevels:
                selectedXnatLevel = self.xnatLevels[-1]
        except Exception, e:
            selectedXnatLevel = 'projects'   
        return selectedXnatLevel




    def __generateUriFromLines(self):
        """
        As sated.
        @return: The generated XNAT uri.
        @rtype: str
        """
        # Construct URI based on XNAT rules.
        xnatUri = ''
        for level in self.xnatLevels:
            lineText = XnatSlicerUtils.toPlainText(self.lineEdits[level].text)
            if len(lineText) > 0:
                xnatUri += '/' + level + '/'
                uriAdd = lineText
                xnatUri += uriAdd
                # Special case for experiments
                if level == 'experiments':
                    xnatUri += '?xsiType=' + \
                               Xnat.xsi.DEFAULT_TYPES[self.xsiList.currentText]
            else:
                break
        return xnatUri


        

    def __clearErrorLines(self):
        """
        As stated.
        """
        #MokaUtils.debug.lf()
        for key, errorLine in self.errorLines.iteritems():
            errorLine.setText('')



    def __onAddButtonClicked(self):
        """
        As stated.
        """
        self.close()
        self.__clearErrorLines()
        xnatUri = self.__generateUriFromLines()
        #MokaUtils.debug.lf(xnatUri)
        self.Events.runEventCallbacks('folderAdded', xnatUri)
        
        


    def __onButtonClicked(self, button):
        """ 
        Callback if the create button is clicked. Communicates with
        XNAT to create a folder. Details below.

        @param button: The button that was clicked.
        @type button: qt.QAbstractButton
        """
        if 'add' in button.text.lower():
            self.__onAddButtonClicked()
        elif 'cancel' in button.text.lower():
            self.close()




    def __prepopulateParentLines(self, level, item = None):
        """
        As stated.
        @param level: The level of the current lineEdit.
        @type level: string
        """
        currNodeText = self.View.getItemName() if not item else \
                       self.View.getItemName(item)
        currNodeLevel = self.View.getItemLevel() if not item else \
                        self.View.getItemLevel(item)
        if (currNodeLevel.lower() != level.lower()) and \
           (currNodeLevel in self.xnatLevels):
            currNodeLevelInd = self.xnatLevels.index(currNodeLevel)
            lineEditLevelInd = self.xnatLevels.index(level)
            if currNodeLevelInd > -1 and \
               lineEditLevelInd > currNodeLevelInd:
                #
                # Only populate the parent line if the parent
                # is found in the stored values OR the parent
                # line is empty.
                #
                currText = self.lineEdits[currNodeLevel].text
                if currText in self.levelTracker[currNodeLevel] or \
                   len(currText.strip()) == 0:
                    self.lineEdits[currNodeLevel].setText(currNodeText)




    def __unpopulateChildLines(self, level):
        """
        As stated.
        @param level: The level of the current lineEdit.
        @type level: string
        """
        currNodeText = self.View.getItemName()
        currNodeLevel = self.View.getItemLevel()

        if (currNodeLevel.lower() == level.lower()) and \
           (currNodeLevel in self.xnatLevels):
            currNodeLevelInd = self.xnatLevels.index(currNodeLevel)
            lineEditLevelInd = self.xnatLevels.index(level)
            if currNodeLevelInd > -1:
                childLevel = currNodeLevelInd + 1
                try:
                    self.lineEdits[childLevel].setText('')
                except: 
                    pass
        
        


    def __showInvalidLineError(self, level):
        """
        As sated.

        @param level: The level of the pertaining lineEdit.
        @type level: string
        """
        #
        # Show error if there are invalid characters
        #
        invalidMsg = MokaUtils.string.getInvalidMessage(spacesValid = False)
        self.errorLines[level].setText(\
                            '<font color=\"red\">%s</font>'%(invalidMsg))
        self.addButton.setEnabled(False)




    def __checkTextInvalid(self, level, text):
        """ 
        @param level: The level of the pertaining lineEdit.
        @type level: string

        @param text:  The text in the pertaining lineEdit.
        @type text: string
        """   
        #print "VALID", MokaUtils.string.isValid(text, spacesValid = False)
        if not MokaUtils.string.isValid(text, spacesValid = False):
            #MokaUtils.debug.lf()
            self.__showInvalidLineError(level)
            return




    def __isChildLevelPopulated(self, level):
        """
        As stated.
        @param level: The level of the pertaining lineEdit.
        @type level: string
        """
        childLevel = None
        try:
            childLevel = self.xnatLevels[self.xnatLevels.index(level)+1]
        except:
            pass
        if childLevel and len(self.lineEdits[childLevel].text) > 0:
            return True
        return False


        

    def __checkTextInUse(self, level, text):
        """
        As stated.

        @param level: The level of the pertaining lineEdit.
        @type level: string

        @param text:  The text in the pertaining lineEdit.
        @type text: string
        """
        #MokaUtils.debug.lf(level, text, self.levelTracker)
        if level in self.levelTracker:
            
            for itemText in self.levelTracker[level]:
                #MokaUtils.debug.lf(text.lower(), itemText, itemText.lower())
                if text.lower() == itemText.lower():
                    #MokaUtils.debug.lf("CHILD POP", 
                    #                   self.__isChildLevelPopulated(level))
                    if self.__isChildLevelPopulated(level):
                        #MokaUtils.debug.lf("CHILD LEVEL POPULATED")
                        self.errorLines[level].setText('')
                        continue
                    errorText = \
                    "<font color=\"red\">The %s name '%s' is"%(\
                                level[:-1].title(), text) + " already taken."

                    if level != 'experiments':
                        errorText += '  Populate below fields to remove this '
                        errorText += ' message. </font>'
                    self.errorLines[level].setText(errorText)
                    self.addButton.setEnabled(False)

        parentInd = self.xnatLevels.index(level) - 1
        if parentInd >= 0:
            self.errorLines[self.xnatLevels[parentInd]].setText('')
                        




    def __onLineEditTextChanged(self, level, text):
        """ 
        Validates the line edit text for the folder
        to add:
            - Checks for invalid characters.
            - Checks if the name is already taken.
            - Populates the line edits accordingly.
            - Unpopulates the line edits accordingly.

        @param level: The level of the pertaining lineEdit.
        @type level: string

        @param text:  The text in the pertaining lineEdit.
        @type text: string
        """

        if hasattr(self, 'addButton'):
            self.addButton.setEnabled(True)

        if len(text.strip(" ")) > 0 and self.View.currentItem():
            self.__prepopulateParentLines(level)
            self.__unpopulateChildLines(level)
            self.errorLines[level].setText('')
            self.__checkTextInvalid(level, text)
            self.__checkTextInUse(level, text)
        else:
            if hasattr(self, 'addButton'):
                self.addButton.setEnabled(False)




    def __storeAtXnatLevel(self, xnatLevel):
        """
        @param xnatLevel: The selected XNAT devel to derive values from
        @type xnatLevel: string
        """
        #MokaUtils.debug.lf(xnatLevel)
        # Store siblings
        self.levelTracker = {}
        self.levelTracker[xnatLevel] = []
        def addToList(item):
            self.levelTracker[xnatLevel].append(self.View.getItemName(item))
        self.View.loopSiblingNodes(addToList)

        # Store parents
        itemParents = self.View.getParents(self.View.currentItem())
        #print itemParents
        for parent in itemParents:
            #print self.View.getItemLevel(parent)
            #print self.View.getItemName(parent)
            self.levelTracker[self.View.getItemLevel(parent)] = \
                                                [self.View.getItemName(parent)]
        #MokaUtils.debug.lf("STORE PARENTS", self.levelTracker)
            



    def __storeAtChildXnatLevel(self, xnatLevel):
        """
        @param xnatLevel: The selected XNAT devel to derive values from
        @type xnatLevel: string
        """
        levelInd = self.xnatLevels.index(xnatLevel)
        if levelInd > -1 and levelInd < len(self.xnatLevels)-1:
            self.View.expandItem()
            def addToSublevelList(item):                
                itemLevel = self.View.getItemLevel(item)
                itemValue = self.View.getItemName(item)
                if not itemLevel in self.levelTracker: 
                    self.levelTracker[itemLevel] = []
                self.levelTracker[itemLevel].append(itemValue)
            self.View.loopChildren(self.View.currentItem(), addToSublevelList)




    def __storeLevelValues(self, xnatLevel, storeChildLevel = True):
        """
        Store all of the existing values in the current selected XnatLevel.
        
        @param xnatLevel: The selected XNAT devel to derive values from
        @type xnatLevel: string

        @param storeChildLevel: Whether to store the next level values.
        @type storeChildLevel: bool
        """
        self.__storeAtXnatLevel(xnatLevel)
        if storeChildLevel:
            self.__storeAtChildXnatLevel(xnatLevel)

            



    def __createLevelLabels(self, level):
        """
        As stated.
        @param level: The level to make the widget for.
        @type level: str
        """
        self.levelLabels[level] = qt.QLabel(self)
        self.levelLabels[level].setFixedHeight(25)      
        self.levelLabels[level].setText('<b>' + 
                             MokaUtils.string.toTitleCase(level) + ': </b>')    




    def __createLineEdits(self, level):
        """
        As stated.
        @param level: The level to make the widget for.
        @type level: str
        """
        self.lineEdits[level] = qt.QLineEdit(self)
        self.lineEdits[level].installEventFilter(self)
        self.lineEdits[level].setFixedHeight(25)




    def __createErrorLines(self, level):
        """
        As stated.
        @param level: The level to make the widget for.
        @type level: str
        """
        self.errorLines[level] = qt.QLabel(self)
        self.errorLines[level].setTextFormat(1)
        self.errorLines[level].setFixedHeight(12)
        self.errorLines[level].setFont(qt.QFont(self.FONT_NAME, 
                                                self.FONT_SIZE, 10, False))




    def __createWidgets(self):
        """
        As stated.
        """
        levelInd = Xnat.path.DEFAULT_LEVELS.index(\
                                        Xnat.path.HIGHEST_FOLDER_ADD_LEVEL)
        self.xnatLevels = Xnat.path.DEFAULT_LEVELS[:levelInd+1]
        for level in self.xnatLevels:
            self.__createLevelLabels(level)
            self.__createLineEdits(level)
            self.__createErrorLines(level)




    def __createButtons(self):
        """
        As stated.
        """
        self.addButton = qt.QPushButton()
        self.addButton.setText("Add")
        self.addButton.setEnabled(False)
        self.cancelButton = qt.QPushButton()
        self.cancelButton.setText("Cancel")
        self.buttonRow = qt.QDialogButtonBox()
        self.buttonRow.addButton(self.cancelButton, 2)
        self.buttonRow.addButton(self.addButton, 0)
        self.buttonRow.connect('clicked(QAbstractButton*)', 
                               self.__onButtonClicked)




    def __initWindow(self):
        """
        As stated.
        """
        self.setWindowTitle("Add Folder to Xnat")
        self.setWindowModality(1)
        self.setFixedWidth(500)
        self.setFixedHeight(200)
        self.hide()



    def __setLayout(self):
        """
        As stated.
        """
        self.mainLayout = qt.QVBoxLayout()
        for level in self.xnatLevels:
            lineLayout = qt.QHBoxLayout()
            lineLayout.addWidget(self.levelLabels[level])
            if level == 'experiments':
                lineLayout.addWidget(self.xsiList)
            lineLayout.addWidget(self.lineEdits[level])            
            self.mainLayout.addLayout(lineLayout)
            self.mainLayout.addWidget(self.errorLines[level])
        self.mainLayout.addStretch()
        self.mainLayout.addWidget(self.buttonRow)
        self.setLayout(self.mainLayout)







