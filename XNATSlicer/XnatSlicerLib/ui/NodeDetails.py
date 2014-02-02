# application
from __main__ import qt

# external
from Xnat import *
from MokaUtils import *

# module
from XnatSlicerGlobals import *
from XnatSlicerUtils import *




class NodeDetails(qt.QWidget):
    """
    NodeDetails inherits QTextEdit and is the display widget
    for the details of a selected 'node' within an View.  By 'details'
    we mean it displays all of the relevant metadata pertaining to a given 
    XNAT node, whether it's a folder (project, subject, experiment, scan)
    or a file.
    """

    def __init__(self, Setting = None):
        """ 
        @param Setting: The Setting to associate with the widget 
            (i.e. Setting_Details)
        @type Setting: Setting
        """

        super(NodeDetails, self).__init__()

        self.Setting = Setting
        self.storedDetailsDict = None
        self.currFont = XnatSlicerGlobals.LABEL_FONT

        self._layout = qt.QGridLayout()
        self._layout.setContentsMargins(0,0,0,0)

        self.numColumns = 2

        # new method
        self.__textViewer = qt.QTableWidget(self)
	self.__textViewer.verticalHeader().hide()
	self.__textViewer.horizontalHeader().hide()
	self.__textViewer.horizontalHeader().setResizeMode(1)
        self.__textViewer.setShowGrid(False)
        self.__textViewer.setColumnCount(self.numColumns)
        self.__textViewer.setStyleSheet('border: none; padding:' + 
                                ' 0px; margin-left: 0px; margin-right: 0px')
        self.__textViewer.verticalScrollBar().setStyleSheet('width: 15px;')


        self._layout.addWidget(self.__textViewer, 0, 0)
        self.setLayout(self._layout)
        self.updateFontFromSettings()
        



    def changeFontSize(self, size):
        """
        Changes the font size of the widget.

        @param size: The size of the font.
        @type size: int
        """
        self.currFont.setPointSize(size)
        self.__textViewer.setFont(self.currFont)

        


    def setText(self, string):
        """
        Sets the text of the widget.

        @param string: The string to apply to the wiget.
        @type string: str
        """
        self.__textViewer.setText(string)

        


    def updateFontFromSettings(self):
        """
        Updates the font size of the widget by querying the stored Setting
        variable.
        """
        storedFontSetting = self.Setting.getStoredFont(self.Setting.\
                                                       LABEL_FONT_SIZE)
        storedFont = int(storedFontSetting[0]) if \
                     len(storedFontSetting) > 0 else \
                     XnatSlicerGlobals.FONT_SIZE
        self.changeFontSize(storedFont)




    def updateFromSettings(self):
        """
        Updates the widget from the Settings_Details widget.
        """
        self.updateFontFromSettings()
        self.setXnatNodeText(None)




    def setXnatNodeText(self, detailsDict):
        """ 
        Sets the text of the widget based on a key-value pair
        styling method.

        @param detailsDict: The dictionary containing details information 
           (including the metadata) specific to the View node.
        @type detailsDict:  dict(str, str)
        """

        if detailsDict == None:
            detailsDict = self.storedDetailsDict
        else:
            self.storedDetailsDict = detailsDict

        if not detailsDict:
            return
        #--------------------
        # The argument is a tuple because
        # the callback is called with multiple
        # arguments (see 'runNodeClickedCallbacks' in 
        # XnatSlicerUtils).
        #--------------------      
        if isinstance(detailsDict, list):
            detailsDict = detailsDict[0]
            
        detailsText = ''  
        storedMetadata = self.Setting.getStoredMetadata( \
                                      self.Setting.LABEL_METADATA, 
                                      detailsDict['XNAT_LEVEL'],
                                      True)
        #MokaUtils.debug.lf("DETAILS DICT", detailsDict, '\n\n\n') 
        #MokaUtils.debug.lf("STORED METADATA", storedMetadata)
        self.__constructItemTable(detailsDict, storedMetadata)
        self.__setItems()




    def __setItems(self):
        """
        Sets the stored itemTable QTableWidget items to the textViewer.
        """
        self.__textViewer.clear()
        self.__textViewer.setRowCount(len(self.itemTable))
        for i in range(0, len(self.itemTable)):
            self.currFont.setWeight(75 if i%2 == 0 else 50)
            for j in range (0, len(self.itemTable[i])):
                currItem = self.itemTable[i][j]
                self.__textViewer.setItem(i, j, currItem)
                currItem.setFlags(32)
                currItem.setTextAlignment(0x0001)
                currItem.setFont(self.currFont)
        self.__textViewer.resizeRowsToContents()




    def __printItemTable(self):
        """
        As stated.
        """
        MokaUtils.debug.lf("ITEM TABLE", itemTable, len(itemTable))
        for i in range(0, len(self.itemTable)):
            print self.itemTable[i][0].text() + ': \'', \
                self.itemTable[i][1].text() +'\' | ', \
                self.itemTable[i][2].text() + ': \'', \
                self.itemTable[i][3].text() + '\'' 
        print '\n\n'



    def __constructItemTable(self, detailsDict, storedMetadata):
        """
        Constructs an item table for populating into the __textViewer.

        @param detailsDict: The details dictionary associated with the node.
        @type detailsDict: dict(str, dict(str, str))

        @param storedMetadata: The metadata associated with the node.
        @type storedMetadata: dict(str, str)
        """
        currRow = 0
        self.itemTable = []
        for key, value in detailsDict.iteritems():
            if key in storedMetadata:
                if key in Xnat.metadata.DEFAULT_DATE_TAGS:
                    value = XnatSlicerUtils.makeDateReadable(value)
                tableItemK = qt.QTableWidgetItem('\n' + key.strip() + ':')
                tableItemV = qt.QTableWidgetItem(value.strip())
                try:
                    self.itemTable[currRow] += [tableItemK]
                    self.itemTable[currRow+1] += [tableItemV]
                except Exception, e:
                    self.itemTable.append([])
                    self.itemTable.append([])
                    self.itemTable[currRow] += [tableItemK]
                    self.itemTable[currRow+1] += [tableItemV]

                if len(self.itemTable[currRow]) == (self.numColumns):        
                    currRow += 2


        
    def setXnatNodeText_old(self, detailsDict):
        """ 
        Sets the text of the widget based on a key-value pair
        styling method.

        @param detailsDict: The dictionary containing details information 
           (including the metadata) specific to the View node.
        @type detailsDict:  dict(str, str)
        """

        if detailsDict == None:
            detailsDict = self.storedDetailsDict
        else:
            self.storedDetailsDict = detailsDict

        if not detailsDict:
            return
        #--------------------
        # The argument is a tuple because
        # the callback is called with multiple
        # arguments (see 'runNodeClickedCallbacks' in 
        # XnatSlicerUtils).
        #--------------------      
        if isinstance(detailsDict, list):
            detailsDict = detailsDict[0]
            
        detailsText = ''
        #MokaUtils.debug.lf("DETAILS DICT", detailsDict, '\n\n\n')
        
        
        #--------------------
        # Refer to the settings file to get the visible
        # tags.
        #--------------------     
        storedMetadata = self.Setting.getStoredMetadata( \
                                      self.Setting.LABEL_METADATA, 
                                      detailsDict['XNAT_LEVEL'],
                                      True)
        
        #MokaUtils.debug.lf("STORED METADATA", storedMetadata)
                    
        #--------------------
        # Construct the priorty strings as an HTML table.
        # HTML table example below.
        #
        # <table border="1">
        # <tr>
        # <td style="width:50%">row 1, cell 1</td>
        # <td style="width:50%">row 1, cell 2</td>
        # </tr>
        # <tr>
        # <td>row 2, cell 1</td>
        # <td>row 2, cell 2</td>
        # </tr>
        # </table>
        # 
        #--------------------   

        colCount = 0
        detailsText = """<table cellpadding="2">
<tr>"""
        for key, value in detailsDict.iteritems():
            if key in storedMetadata:
                if key in Xnat.metadata.DEFAULT_DATE_TAGS:
                    #print value
                    value = XnatSlicerUtils.makeDateReadable(value)
                detailsStr = "<b>%s</b>:  %s"%(key, value)                
                detailsText += "\n\t<td style=\"width:50%\"" + \
                               ">%s</td>\n"%(detailsStr)
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
        self.__textViewer.setText(detailsText)

