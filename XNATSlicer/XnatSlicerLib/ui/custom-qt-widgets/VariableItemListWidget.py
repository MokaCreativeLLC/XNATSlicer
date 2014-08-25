__author__ = "Sunil Kumar (kumar.sunil.p@gmail.com)"
__copyright__ = "Copyright 2014, Washington University in St. Louis"
__credits__ = ["Sunil Kumar", "Steve Pieper", "Dan Marcus"]
__license__ = "XNAT Software License Agreement " + \
              "(see: http://xnat.org/about/license.php)"
__version__ = "2.1.1"
__maintainer__ = "Rick Herrick"
__email__ = "herrickr@mir.wustl.edu"
__status__ = "Production"


from __main__ import qt





class VariableItemListWidget (qt.QListWidget):
    """
    VariableItemListWidget is a customized QListWidget
    that allows the user to add items of varying ineractive 
    types (checkboxes, etc.).  
    
    TODO: Add more support for various item types specified
    here:
    http://harmattan-dev.nokia.com/docs/library/html/qt4/qt.html#ItemDataRole-enum
    """
    
    def __init__(self):
        """ Init function.
        """
        
        #--------------------
        # Call parent init.
        #--------------------
        super(VariableItemListWidget, self).__init__(self)


        
        #--------------------
        # QT quirk: the scrollbar's width displays widely 
        # if we don't set this.
        #--------------------
        self.verticalScrollBar().setStyleSheet('width: 15px')


        

    def addItemsByType(self, textList, itemType = None):
        """ 
        Adds an item to the list widget according to the 
        specificed arguments: the text and the itemType.
        The itemType argument is optional: if it's not 
        set then the default QListWidgetItem flags are
        applied.
        
        See http://harmattan-dev.nokia.com/docs/library/html/qt4/qt.html#ItemDataRole-enum
        for further descriptions of the item types.
        
        TODO: Add support for more item types beyond the
        checkbox.
        """

        #--------------------
        # Call parent function 'addItems'
        #--------------------
        self.addItems(textList)


        
        #--------------------
        # If 'itemType' is specified, set the
        # items accordingly
        #
        # TODO: Add more support for the various
        # item types.
        #--------------------       
        if itemType:
            for i in range(0, self.count):

                #
                # CHECKBOXES
                #
                if itemType == 'checkbox':

                    #
                    # Set the checkbox size.
                    #
                    checkboxSize = qt.QSize(20,20)
                    self.item(i).setSizeHint(checkboxSize)

                    #
                    # Flags for checkboxes.
                    #
                    self.item(i).setFlags(4 | 8 | 16 | 32)
                    self.item(i).setCheckState(0)


                #
                # DISABLED
                #    
                elif itemType == 'disabled':
                    self.item(i).setFlags(0)




