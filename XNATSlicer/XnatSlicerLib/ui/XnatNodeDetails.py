from __main__ import vtk, ctk, qt, slicer

import os

from XnatSettings import *



comment = """
XnatNodeDetails inherits QTextEdit and is the display widget
for the details of a selected 'node' within an XnatView.  By 'details'
we mean, it displays all of the relevant metadata pertaining to a given 
XNAT node, whether it's a folder (project, subject, experiment, scan)
or a file.

TODO : 
"""



class XnatNodeDetails(qt.QWidget):
    """ Descriptor above.
    """

    def __init__(self, MODULE = None):
        """ Init function.
        """

        #--------------------
        # Call parent init.
        #--------------------
        super(XnatNodeDetails, self).__init__()

        
        self.MODULE = MODULE


        #self.settingsButton = self.MODULE.utils.makeSettingsButton(self.MODULE.XnatDetailsSettings)



        self.textEdit = qt.QTextEdit(self)

        self.currFont = self.MODULE.GLOBALS.LABEL_FONT
        self.textEdit.setFont(self.currFont)
        self.textEdit.setReadOnly(True)



        self._layout = qt.QGridLayout()
        self._layout.setContentsMargins(0,0,0,0)

        
        #--------------------
        # Call parent init.
        #--------------------
        self.numColumns = 2


        self.textEdit.setStyleSheet('border: none; padding: 0px; margin-left: 0px; margin-right: 0px')

        
        #--------------------
        # NOTE: fixes a scaling error that occurs with the scroll 
        # bar.  Have yet to pinpoint why this happens.
        #--------------------
        self.textEdit.verticalScrollBar().setStyleSheet('width: 15px;')


        self._layout.addWidget(self.textEdit, 0, 0)

        self.setLayout(self._layout)

        


    def changeFontSize(self, size):
        """
        """
        self.currFont.setPointSize(size)
        self.textEdit.setFont(self.currFont)


        
        
    def setColumnCount(self, num):
        """
        """
        


    def setText(self, string):
        """
        """
        self.textEdit.setText(string)

        
        
    def setXnatNodeText(self, detailsDict):
        """ Sets the text of the widget based on a key-value pair
            styling method.
        """

        #--------------------
        # The argument is a tuple because
        # the callback is called with multiple
        # arguments (see 'runNodeClickedCallbacks' in 
        # XnatUtils).
        #--------------------      
        detailsDict = detailsDict[0]
        detailsText = ''

        #print "\n\n\t\tDETAILS DICT", detailsDict, '\n\n\n'
        
        
        #--------------------
        # Refer to the settings file to get the visible
        # tags.
        #--------------------     
        xnatHost = self.MODULE.XnatLoginMenu.hostDropdown.currentText
        metadataTag = self.MODULE.XnatDetailsSettings.ON_METADATA_CHECKED_TAGS['main'] + detailsDict['XNAT_LEVEL']
        visibleTags = self.MODULE.XnatSettingsFile.getTagValues(xnatHost, metadataTag)


                    
        #--------------------
        # Construct the priorty strings as an HTML table.
        # HTML table example below.
            
        """
        <table border="1">
        <tr>
        <td>row 1, cell 1</td>
        <td>row 1, cell 2</td>
        </tr>
        <tr>
        <td>row 2, cell 1</td>
        <td>row 2, cell 2</td>
        </tr>
        </table>
        """  
        #--------------------   

        colCount = 0
        detailsText = '<table cellpadding=2 >\n<tr>'
        for key, value in detailsDict.iteritems():
            if key in visibleTags:

                if key in self.MODULE.GLOBALS.DATE_TAGS:
                    value = self.MODULE.utils.makeDateReadable(value)
                    
                detailsStr = "<b>%s</b>:  %s"%(key, value)

                
                detailsText += "\n\t<td>%s</td>\n"%(detailsStr)
                colCount += 1
                if colCount == self.numColumns:
                    detailsText +='</tr>\n<tr>'
                    colCount = 0

        if detailsText.endswith('<tr>'):
            detailsText = detailsText[:-4]
        else:
            detailsText += '</tr>'
        detailsText += '\n</table>'



        #--------------------
        # Call parent 'setText'
        #-------------------- 
        self.textEdit.setText(detailsText)

