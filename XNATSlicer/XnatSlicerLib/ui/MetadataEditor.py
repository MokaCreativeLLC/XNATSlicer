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
from MokaUtils import *

# module 
from VariableItemListWidget import *

        

class MetadataEditor(qt.QFrame):
    """
    MetadataEditor is the parent class of the MetadataEditor widgets that 
    reside twice in every MetadataEditorSet: MetadataEditor_Custom 
    and MetadataEditor_Default.  MetadataEditor contains a variety of shared
    functions between the aforementioned child classes.
    """

    EVENT_TYPES = [
        'UPDATE',
        'ITEMCLICKED'
    ] 



    def __init__(self, xnatLevel):
        """ 
        Init function.  In addtion to the
        MODULE, the user must also provide
        the xnatLevel that the editor applies to.
        """

        #--------------------
        # Parent init.
        #--------------------
        qt.QFrame.__init__(self)

        self.EVENT_TYPES = list(set(MetadataEditor.EVENT_TYPES + 
                                    self.EVENT_TYPES))
        self.Events = MokaUtils.Events(self.EVENT_TYPES)


        
        #--------------------
        # Class variables.
        #--------------------       
        self.xnatLevel = xnatLevel
        self.onMetadataCheckedTag = "ON_METADATA_CHECKED"


        
        #--------------------
        # The list widget.
        #--------------------         
        self.listWidget = VariableItemListWidget()
        self.listWidget.setStyleSheet('margin-top: 0px; margin-bottom: 0px')
        #
        # Connect item click event.
        #
        self.listWidget.connect('itemClicked(QListWidgetItem *)', 
                                self.onItemClicked)

        
        #--------------------
        # The main layout of the widget.
        #--------------------         
        self.mainLayout = qt.QVBoxLayout()
        self.mainLayout.addWidget(self.listWidget)
        self.setLayout(self.mainLayout)


        
        #--------------------
        # Widget item size.
        #--------------------
        self.itemSize = qt.QSize(20,20)



        #--------------------
        # Call setup function:
        # this is a to be inherited
        # by child classes.
        #--------------------          
        self.setup()


        
        #--------------------
        # List items are defaulted to 
        # 'label'.  The user can change
        # the item type after initialization.
        #--------------------        
        self.setItemType('label')

        

        #--------------------
        # Sync list contents with the
        # the metadata stored in the
        # SettingsFile.
        #--------------------          
        self.update()


        
        
    @property
    def count(self):
        """ Returns the listWidget's count.
        """
        return self.listWidget.count




    def getCheckedBoxesOnly(self):
        """
        Returns all checked metadata items from
        the list.

        @return: A list of the checked metadata items (strings).
        @rtype: string
        """
        checkedMetadataItems = []
        for i in range(0, self.listWidget.count):
            currItem = self.listWidget.item(i)
            #print currItem.text(), currItem.flags(), currItem.checkState()
            if currItem.flags() == 48 and currItem.checkState() == 2:
                checkedMetadataItems.append(currItem)
        return checkedMetadataItems





    def listItemsOnly(self, items, itemType = 'label'):
        """
        """
        self.listWidget.clear()
        self.listWidget.addItems(items)
        self.setItemType(itemType)




    def setCheckedOnly(self, boxTexts):
        """
        """
        for checkBox in self.getCheckBoxes():
            if checkBox.text() in boxTexts:
                checkBox.setCheckState(2) 
            else:
                checkBox.setCheckState(0)



    def clear(self):
        """ Clears the listWidget.
        """
        self.listWidget.clear()
    

        
        
    def item(self, index):
        """ Returns the item allocated
            by 'index'
        """
        return self.listWidget.item(index)



    
    def addItems(self, items):
        """ Adds qListWidgetItems to the
            listWidget.
        """
        self.listWidget.addItems(items)



        
    def setItemType(self, itemType):
        """ 
        Allows the user to set the kind of QListWidgetItems to be 
        displayed: 
        either a label or a checkbox, as provided by the 'itemType' 
        argument.
        
        Refer to here for more information about the flags for setting the
        item type: 
        http://harmattan-dev.nokia.com/docs/library/html/qt4/qt.html#
            ItemFlag-enum
        """
        
        #--------------------
        # Record the item type for reference.
        #
        # NOTE: XnatMetadataEdtiors can only
        # have one itemType (checkbox or label)
        # for now.
        #--------------------
        #print "\t\t(Meadata Editor) EDITOR SET ITEM TYPE", \
        #    self.__class__.__name__
        self.currItemType = itemType


        
        #--------------------
        # Set the flags based on the 'self.currItemType' 
        # argument:
        # either a 'checkbox' or a 'label'
        #--------------------
        if self.currItemType == 'checkbox':
            self.itemFlags = 16 | 32          
        elif self.currItemType == 'label':
            if 'Custom' in self.__class__.__name__:
                self.itemFlags = 1 | 32
            else:
                self.itemFlags = 1              



        #--------------------
        # Loop through all the listWidget's items
        # and set their flags accordingly.
        #--------------------
        if self.listWidget:    
            for i in range(0, self.listWidget.count):
                self.listWidget.item(i).setSizeHint(self.itemSize)
                self.listWidget.item(i).setFlags(self.itemFlags)
                
                #
                # If the item type is a checkbox, 
                # we set it unchecked at first.
                #
                if self.currItemType == 'checkbox':
                    self.listWidget.item(i).setCheckState(0)
               

                

    def update(self):
        """ 
        Refreshes the contents of the listWidget
        to match the stored contents within the
        SettingsFile.  Also reconnects the event
        callbacks when the items are clicked.
        """

        #--------------------
        # Necessary to ensure the widget types are 
        # maintained. 
        #--------------------
        self.setItemType(self.currItemType)


        #--------------------
        # Run callbacks
        #--------------------
        self.Events.runEventCallbacks('UPDATE', self)
        




    def getCheckBoxes(self):
        """
        """
        checkBoxes = []
        for i in range(0, self.listWidget.count):
            item = self.listWidget.item(i)
            #MokaUtils.debug.lf("CHECK BOXES", item, item.text(), \
            #                   item.flags(), self.currItemType)
            if item.flags() == 48:
                checkBoxes.append(item)
        return checkBoxes
        
            


    def onItemClicked(self, item):
        """ 
        Callback for when an item in the listWidget
        is clicked.
        """
        #--------------------
        # If the item is a checkbox
        #--------------------
        if item.flags() == 48:
            #MokaUtils.debug.lf()
            self.Events.runEventCallbacks('ITEMCLICKED', self)
            


