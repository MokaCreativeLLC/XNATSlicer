__author__ = "Sunil Kumar (kumar.sunil.p@gmail.com)"
__copyright__ = "Copyright 2014, Washington University in St. Louis"
__credits__ = ["Sunil Kumar", "Steve Pieper", "Dan Marcus"]
__license__ = "XNAT Software License Agreement " + \
              "(see: http://xnat.org/about/license.php)"
__version__ = "2.1.1"
__maintainer__ = "Rick Herrick"
__email__ = "herrickr@mir.wustl.edu"
__status__ = "Production"


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
    FolderMaker is used for creating new folders within XNAT at the projects, 
    subjects, experiments levels.
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

        @param View: The View module of XNATSlicer.
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
        self.__xsiList = qt.QComboBox()
        self.__xsiList.addItems([key for key, value in \
                               Xnat.xsi.DEFAULT_TYPES.iteritems()])
        self.__levelLabels = {}
        self.__lineEdits = {}
        self.__errorLines = {}
        self.__levelTracker = {}
        self.__nextLevelList = []


        #--------------------
        # Inits
        #--------------------
        self.__initWindow()
        self.__createWidgets()
        self.__createButtons()
        self.__setLayout();




    def show(self):
        """
        Inherits from qt.QWidget.   Conducts some custom routines as well.
        """
        try:
            for key, widget in self.__lineEdits.iteritems():
                widget.clear()
        except:
            pass
        selectedXnatLevel = self.__getSelectedXnatLevel()     
        self.__trackRelevantNodes(selectedXnatLevel) 
        

        #--------------------
        # Hide and show to bring back to front
        #--------------------
        self.hide()
        qt.QWidget.show(self)


        #--------------------
        # Enable line edits
        #--------------------
        for level, item in self.__lineEdits.iteritems():
            item.setEnabled(True)


        #--------------------
        # Prepopulate
        #--------------------
        self.__prepopulate_ByViewSelection(selectedXnatLevel)




    def eventFilter(self, widget, event):
        """ 
        Inherits from qt.QWidget -- does not need to be called programatically.
        Event filter for line edit interaction.
        Refer to: U{http://qt-project.org/doc/qt-4.8/qevent.html#Type-enum} for
        more information.

        @param widget: The widget calling the event.
        @type widget: qt.QWidget

        @param event: The QT event.
        @type event: number     
        """
        for level, lineEdit in self.__lineEdits.iteritems():
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
        Generates an XNAT uri to create a folder based on the line edits.
        @return: The generated XNAT uri.
        @rtype: str
        """
        # Construct URI based on XNAT rules.
        xnatUri = ''
        for level in self.xnatLevels:
            lineText = XnatSlicerUtils.toPlainText(self.__lineEdits[level].text)
            if len(lineText) > 0:
                xnatUri += '/' + level + '/'
                uriAdd = lineText
                xnatUri += uriAdd
                # Special case for experiments
                if level == 'experiments':
                    xnatUri += '?xsiType=' + \
                    Xnat.xsi.DEFAULT_TYPES[self.__xsiList.currentText]
            else:
                break
        return xnatUri


        

    def __clearErrorLines(self):
        """
        Clears the error lines.
        """
        #MokaUtils.debug.lf()
        for key, errorLine in self.__errorLines.iteritems():
            errorLine.setText('')




    def __onAddButtonClicked(self):
        """
        Callback when the add button is clicked.
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




    def __onLineEditTextChanged(self, level, text):
        """ 
        Validates the line edit text for the folder to add:
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
            self.__prepopulate_byParentLines(level)
            self.__unpopulateChildLines(level)
            self.__errorLines[level].setText('')
            self.__checkTextInvalid(level, text)
            self.__checkTextInUse(level, text)
        else:
            if hasattr(self, 'addButton'):
                self.addButton.setEnabled(False)




    def __prepopulate_ByViewSelection(self, level):
        """
        Prepopulates the lineEdits based on the selection in the View.
        @param level: The level of the current lineEdit.
        @type level: string
        """
        # Only do this for non-projects
        levelInd = self.xnatLevels.index(level)
        if levelInd > 0:
            levelInd -= 1
            while levelInd > -1:
                #MokaUtils.debug.lf(self.__levelTracker)
                currLevel = self.xnatLevels[levelInd]
                val = self.__levelTracker[currLevel][0]
                self.__lineEdits[currLevel].setText(val)
                self.__lineEdits[currLevel].setEnabled(False)
                levelInd -= 1




    def __prepopulate_byParentLines(self, level, item = None):
        """
        Prepopulates the line edits based on the the parent lines of the
        currently edited line edit.
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
                currText = self.__lineEdits[currNodeLevel].text
                if currText in self.__levelTracker[currNodeLevel] or \
                   len(currText.strip()) == 0:
                    self.__lineEdits[currNodeLevel].setText(currNodeText)




    def __unpopulateChildLines(self, level):
        """
        Unpopulates the child lines of a lineEdit given certain criteria.
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
                    self.__lineEdits[childLevel].setText('')
                except: 
                    pass
        
     

   
    def __checkTextInvalid(self, level, text):
        """ 
        Checks if a text line is invalid based on it's characters.
        @param level: The level of the pertaining lineEdit.
        @type level: string
        @param text:  The text in the pertaining lineEdit.
        @type text: string
        """   
        #print "VALID", MokaUtils.string.isValid(text, spacesValid = False)
        if not MokaUtils.string.isValid(text, spacesValid = False):
            #MokaUtils.debug.lf()
            invalidMsg = MokaUtils.string.getInvalidMessage(spacesValid = False)
            self.__errorLines[level].setText(\
                                '<font color=\"red\">%s</font>'%(invalidMsg))
            self.addButton.setEnabled(False)
            return

               


    def __isChildLineEditPopulated(self, level):
        """
        Determines if the child level line edit is populated.
        @param level: The level of the pertaining lineEdit.
        @type level: string
        @return: Whether the child line edit is populated.
        @rtype: str
        """
        childLevel = None
        try:
            childLevel = self.xnatLevels[self.xnatLevels.index(level)+1]
        except:
            pass
        if childLevel and len(self.__lineEdits[childLevel].text) > 0:
            return True
        return False


        

    def __checkTextInUse(self, level, text):
        """
        Shows an error message if a given text is taken already by the sibling
        nodes of the current view object.
        @param level: The level of the pertaining lineEdit.
        @type level: string
        @param text:  The text in the pertaining lineEdit.
        @type text: string
        """
        #MokaUtils.debug.lf(level, text, self.__levelTracker)
        if level in self.__levelTracker:
            
            for itemText in self.__levelTracker[level]:
                #MokaUtils.debug.lf(text.lower(), itemText, itemText.lower())
                if text.lower() == itemText.lower():
                    #MokaUtils.debug.lf("CHILD POP", 
                    #                   self.__isChildLineEditPopulated(level))
                    if self.__isChildLineEditPopulated(level):
                        #MokaUtils.debug.lf("CHILD LEVEL POPULATED")
                        self.__errorLines[level].setText('')
                        continue
                    errorText = \
                    "<font color=\"red\">The %s name '%s' is"%(\
                                level[:-1].title(), text) + " already taken."

                    if level != 'experiments':
                        errorText += '  Populate below fields to remove this '
                        errorText += ' message. </font>'
                    self.__errorLines[level].setText(errorText)
                    self.addButton.setEnabled(False)

        parentInd = self.xnatLevels.index(level) - 1
        if parentInd >= 0:
            self.__errorLines[self.xnatLevels[parentInd]].setText('')
                        



    def __trackSiblingsAndParents(self, xnatLevel):
        """
        Stores the sibling nodes of wthin the given XNAT level provided 
        in the view.
        @param xnatLevel: The selected XNAT devel to derive values from
        @type xnatLevel: string
        """
        #MokaUtils.debug.lf(xnatLevel)
        # Store siblings
        self.__levelTracker = {}
        self.__levelTracker[xnatLevel] = []
        def addToList(item):
            self.__levelTracker[xnatLevel].append(self.View.getItemName(item))
        self.View.loopSiblingNodes(addToList)

        # Store parents
        itemParents = self.View.getParents(self.View.currentItem())
        #print itemParents
        for parent in itemParents:
            #print self.View.getItemLevel(parent)
            #print self.View.getItemName(parent)
            self.__levelTracker[self.View.getItemLevel(parent)] = \
                                                [self.View.getItemName(parent)]
        #MokaUtils.debug.lf("STORE PARENTS", self.__levelTracker)
            



    def __trackChildren(self, xnatLevel):
        """
        Tracks the child node values of relative to the given view item.
        @param xnatLevel: The selected XNAT devel to derive values from
        @type xnatLevel: string
        """
        levelInd = self.xnatLevels.index(xnatLevel)
        if levelInd > -1 and levelInd < len(self.xnatLevels)-1:
            self.View.expandItem()
            def addToSublevelList(item):                
                itemLevel = self.View.getItemLevel(item)
                itemValue = self.View.getItemName(item)
                if not itemLevel in self.__levelTracker: 
                    self.__levelTracker[itemLevel] = []
                self.__levelTracker[itemLevel].append(itemValue)
            self.View.loopChildren(self.View.currentItem(), addToSublevelList)




    def __trackRelevantNodes(self, xnatLevel, trackChildren = True):
        """
        Tracks the relevant nodes for error checking: children, parents, and 
        siblings.
        @param xnatLevel: The selected XNAT devel to derive values from
        @type xnatLevel: string
        @param trackChildren: Whether to store the next level values.
        @type trackChildren: bool
        """
        self.__trackSiblingsAndParents(xnatLevel)
        if trackChildren:
            self.__trackChildren(xnatLevel)

            


    def __createLevelLabels(self, level):
        """
        As stated.
        @param level: The level to make the widget for.
        @type level: str
        """
        self.__levelLabels[level] = qt.QLabel(self)
        self.__levelLabels[level].setFixedHeight(25)      
        self.__levelLabels[level].setText('<b>' + 
                             MokaUtils.string.toTitleCase(level) + ': </b>')    




    def __createLineEdits(self, level):
        """
        As stated.
        @param level: The level to make the widget for.
        @type level: str
        """
        self.__lineEdits[level] = qt.QLineEdit(self)
        self.__lineEdits[level].installEventFilter(self)
        self.__lineEdits[level].setFixedHeight(25)




    def __createErrorLines(self, level):
        """
        As stated.
        @param level: The level to make the widget for.
        @type level: str
        """
        self.__errorLines[level] = qt.QLabel(self)
        self.__errorLines[level].setTextFormat(1)
        self.__errorLines[level].setFixedHeight(12)
        self.__errorLines[level].setFont(qt.QFont(self.FONT_NAME, 
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
            lineLayout.addWidget(self.__levelLabels[level])
            if level == 'experiments':
                lineLayout.addWidget(self.__xsiList)
            lineLayout.addWidget(self.__lineEdits[level])            
            self.mainLayout.addLayout(lineLayout)
            self.mainLayout.addWidget(self.__errorLines[level])
        self.mainLayout.addStretch()
        self.mainLayout.addWidget(self.buttonRow)
        self.setLayout(self.mainLayout)







