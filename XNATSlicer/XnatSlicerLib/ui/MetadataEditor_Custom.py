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

# external
from Xnat import *

# module 
from MetadataEditor import *
from XnatSlicerUtils import *


class MetadataEditor_Custom(MetadataEditor):
    """ 
    MetadataEditor_Custom presents and manages custom metadata
    for the user to add/remove and toggle when traversing an XNAT 
    tree in a given View.  It is in constant communication with
    the SettingsFile, storing the changes accordingly.  This is 
    in contrast with the XnatMetadataEditor_Default, which 
    refers to the XnatGlobals to populate its contents.
    """

    EVENT_TYPES = [
        'ADDCLICKED',
        'REMOVECLICKED'
    ] 
    
    def setup(self):
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
        self.lineEdit.connect('textChanged(const QString)', 
                              self.onLineEditFocused)
        

        
        #--------------------
        # The addButton
        #--------------------          
        self.addButton = qt.QPushButton('Add')
        self.addButton.setFixedHeight(buttonHeight)
        self.addButton.setFixedWidth(buttonWidth)
        self.addButton.connect('clicked()', self.__onAddButtonClicked)


        
        #--------------------
        # The deleteButton
        #--------------------        
        self.deleteButton = qt.QPushButton('Remove')
        self.deleteButton.setFixedHeight(buttonHeight)
        self.deleteButton.setFixedWidth(buttonWidth)
        self.deleteButton.connect('clicked()', self.__onRemoveButtonClicked)
        self.deleteButton.setEnabled(False)



        #--------------------
        # The custom add/edit line.
        #--------------------  
        self.lineLayout = qt.QHBoxLayout()
        self.lineLayout.addWidget(self.lineEdit)
        self.lineLayout.addWidget(self.addButton)
        self.lineLayout.addWidget(self.deleteButton)
        self.mainLayout.addLayout(self.lineLayout)

        

        

    def eventFilter(self, widget, event):
        """ 
        Tracks whether the lineEdit was focused
        and runs the relevant callback.

        @deprecated
        """
        #print widget, event.type()
        if widget == self.lineEdit:
            if event.type() == qt.QEvent.FocusIn:
                self.onLineEditFocused()
        



    def __onRemoveButtonClicked(self):
        """ 
        Deletes a custom metadata item from the listWidget,
        communicating with the SettingsFile accordingly.
        """
        

        self.Events.runEventCallbacks('REMOVECLICKED', self)




        
            

            
            
    def __onAddButtonClicked(self):
        """ 
        Callback when the addButton is clicked.
        Communicates with XnatSettingFile accordingly.
        """

        #--------------------
        # Return out of there's no
        # text in the lineEdit.
        #--------------------       
        if len(self.lineEdit.text.strip()) == 0:
            return

        self.Events.runEventCallbacks('ADDCLICKED', self)



        

    def setEditLineVisible(self, visible):
        """ 
        Allows the editline to be displayed
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


            

    @property
    def storageTagName(self):
        """
        @return: The tag pertaining to the checked metadata level.
        @rtype: string
        """
        return XnatSlicerUtils.makeCustomMetadataTag(self.xnatLevel)




    def onItemClicked(self, listWidgetItem):
        """ 
        Runs class-specific callbacks for
        when an item in the listWidget is clicked.
        Also refers to the parent 'onItemClicked'
        function.
        """

        #--------------------
        # Call parent 'onItemClicked'
        #-------------------- 
        super(MetadataEditor_Custom, self).onItemClicked(listWidgetItem)


        
        #--------------------
        # Update the edit widgets.
        #-------------------- 
        self.deleteButton.setEnabled(True)
        self.addButton.setEnabled(False)
        self.lineEdit.clear()


        

    def onLineEditFocused(self, *args):
        """ 
        Callback for when the user
        focuses on the lineEdit.
        Toggles the edit buttons accordingly.
        """
        if self.listWidget.currentItem():
            self.listWidget.currentItem().setSelected(False)
        self.addButton.setEnabled(True)
        self.deleteButton.setEnabled(False)
        


