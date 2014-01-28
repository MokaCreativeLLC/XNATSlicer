# application
from __main__ import qt

# external
from Xnat import *
from MokaUtils import *

# module 
from VariableItemListWidget import *

        

class MetadataEditor(qt.QFrame):
    """
    MetadataEditor is the editor widget that resides
    twice in every XnatMetadaManager section, or XnatLevel.
    Like the "Settings" widgets, it is also in 
    communication with the SettingsFile as the 
    metadata that exists within its lists are loaded, synced
    and stored within the SettingsFile.  It is also 
    in touch with XnatGlobals to refer to any default
    metadata that may exist within all XNAT hosts.
    
    The user must specifiy the XnatLevel that the 
    MetadataEditor belongs to as an argument
    in the __init__ function.

    XnatMetadataEdtior is a
    parent class of the specific metadata editors:
    XnatMetadataEditor_Defaults, XnatMetadataEditor_Custom.
    It contains functions shared between the two.
    
    Each subclass of XnatMetadataEdtior resides in one 
    section of the MetadataEditorSet.For example, there are 
    two MetadataEditors in the 'projects' section,
    (XnatMetadataEditor_Defaults, XnatMetadataEditor_Custom)
    two in the 'subjects' section (XnatMetadataEditor_Defaults, 
    XnatMetadataEditor_Custom), etc.  

    With respect to the child classes of the MetadataEditor,
    the user can further customize each edtior.  For instance,
    if the list items are to be checkboxes, or if the "Add" and
    "Remove" buttons are visible. 
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




    @property
    def checkedLevelTag(self):
        """
        @return: The tag pertaining to the checked metadata level.
        @rtype: string

        """
        return self.onMetadataCheckedTag + self.xnatLevel




    @property
    def checkedMetadataItems(self):
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
                checkedMetadataItems.append(currItem.text())
        return checkedMetadataItems




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
        """ Allows the user to set the kind of QListWidgetItems to be displayed: 
            either a label or a checkbox, as provided by the 'itemType' argument.

            Refer to here for more information about the flags for setting the
            item type: 
            http://harmattan-dev.nokia.com/docs/library/html/qt4/qt.html#ItemFlag-enum
        """
        
        #--------------------
        # Record the item type for reference.
        #
        # NOTE: XnatMetadataEdtiors can only
        # have one itemType (checkbox or label)
        # for now.
        #--------------------
        ##print "\t\t(Meadata Editor) EDITOR SET ITEM TYPE", self.__class__.__name__
        self.currItemType = itemType


        
        #--------------------
        # Set the flags based on the 'self.currItemType' 
        # argument:
        # either a 'checkbox' or a 'label'
        #--------------------
        if self.currItemType == 'checkbox':
            self.itemFlags = 16 | 32          
        elif self.currItemType == 'label':
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
        # Loop through all the listWidget's items
        # and set their flags accordingly.
        #--------------------
        ##print "EDITOR SUPER UPDATE"
        self.setItemType(self.currItemType)



        #--------------------
        # Connect item click event.
        #--------------------
        self.listWidget.connect('itemClicked(QListWidgetItem *)', self.onItemClicked)


        
        #--------------------
        # Refer to items in the settings file
        # if the items are a checkbox.  
        #
        # NOTE: If the items are labels, we 
        # refer to the XnatGlobal files because
        # those metadata points will be shared
        # by all XNAT hosts.
        #--------------------
        if self.currItemType == 'checkbox':
            try:
                self.Events.runEventCallbacks('UPDATE', self.getCheckBoxes())
            except Exception, e:
                return



    def getCheckBoxes(self):
        """
        """
        checkBoxes = []
        for i in range(0, self.listWidget.count):
            item = self.listWidget.item(i)
            if item.flags() == 48:
                checkBoxes.append(item)
        return checkBoxes
        
            

    def onItemClicked(self, item):
        """ Callback for when an item in the listWidget
            is clicked.
        """


        
        #--------------------
        # If the item is a checkbox
        #--------------------
        if item.flags() == 48:

            #
            # Query the settings file for the saved 'checked'
            # metadata values.
            #
            savedMetadataItems = self.SettingsFile.getSetting(self.currXnatHost, self.checkedLevelTag)

            #
            # If the item was CHECKED
            # then we modify the saved metadata
            # accordingly...
            #
            if item.checkState() == 2:

                checkedMetadataItems = self.checkedMetadataItems
                
                
                #
                # Union the 'checkedMetadataItems' list with the 
                # 'savedMetadataItems' list.
                #
                mergedItems = list(set(savedMetadataItems) | set(checkedMetadataItems))
            
                #
                # Save the unioned list back to the SettingsFile.
                #
                tagDict = {self.checkedLevelTag : mergedItems}
                self.SettingsFile.setSetting(self.currXnatHost, tagDict)



            #
            # If the item was UNCHECKED
            # then we modify the saved metadata
            # accordingly...
            #
            if item.checkState() == 0:
                
                #
                # Difference the checked items in the listWidget
                # with the saved checked items in the SettingsFile.
                #
                differenceItems = list(set(savedMetadataItems) - set([item.text()]))                
                tagDict = {self.checkedLevelTag : differenceItems}
                self.SettingsFile.setSetting(self.currXnatHost, tagDict)  

                
        self.Events.runEventCallbacks('ITEMCLICKED')
        self.MODULE.View.refreshColumns()


