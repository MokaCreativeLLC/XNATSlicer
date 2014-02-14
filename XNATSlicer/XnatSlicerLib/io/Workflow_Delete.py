# python
import os

# application
from __main__ import qt



    
class Workflow_Delete(object):
    """ 
    Conducts the necessary steps to delete
    a folder or a file from a given XNAT host.  The ability to delete
    either depends on the user's priveleges determined both by the 
    projects and the XNAT host.


    @todo: Consider setting the current item to the deleted 
    sibling above or below it.  If no siblings, then go to parent.
    """
    
    def __init__(self, MODULE):
        """
        @param MODULE: The XNATSlicer module
        @type MODULE: XnatSlicerWidget
        """
        self.MODULE = MODULE
        self.deleteDialog = self.__makeDialog()

        


    def __makeDialog(self):
        """
        The Dialog box.  If the user 'OK's the delete
        it calls on 'Workflow_Delete.beginWorkflow'

        @return: The delete dialog.
        @rtype: qt.QMessageBox
        """
        deleteDialog = qt.QMessageBox()
        deleteDialog.setIcon(qt.QMessageBox.Warning)
        deleteDialog.setText("Are you sure you want to delete '%s' from Xnat?"\
                             %(self.MODULE.View.getItemName()))   
        deleteDialog.connect('buttonClicked(QAbstractButton*)', 
                             self.beginWorkflow)
        deleteDialog.addButton(qt.QMessageBox.Ok)
        deleteDialog.addButton(qt.QMessageBox.Cancel) 
        return deleteDialog


        
        
    def beginWorkflow(self, button = None):
        """ 
        Main workflow function for the class.

        @param button: The button pressed from the delete dialog.
        @type button: qt.QAbstractButton.
        """

        #--------------------
        # If there's no button argument, then exit out of function
        # by showing the deleteDialog.
        #--------------------
        if not button:
            self.deleteDialog.show()

            
        #--------------------
        # If 'ok' pressed in the deleteDialog...
        #--------------------
        elif button and 'ok' in button.text.lower(): 
            
            #
            # Construct the full delete string based on type of tree item deleted
            #
            delStr = self.MODULE.View.getXnatUri()
            #print "delStr", delStr

            if not '/files/' in delStr:
                delStr = os.path.dirname(delStr)
                
            #
            # Call delete XnatIo's 'delete' function.
            #
            self.MODULE.XnatIo.delete(delStr)

            
            #
            # Set currItem to parent of deleted item and expand it. 
            #
            self.MODULE.View.removeCurrItem()



        #--------------------
        # Cancel workflow if 'Cancel' button was pressed.
        #--------------------
        elif button and button.text.lower().find('cancel') > -1:
             return
