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
from XnatSlicerUtils import *



class NodeDetails(qt.QWidget):
    """
    NodeDetails inherits QTextEdit and is the display widget
    for the details of a selected 'node' within an View.  By 'details'
    we mean it displays all of the relevant metadata pertaining to a given 
    XNAT node, whether it's a folder (project, subject, experiment, scan)
    or a file.
    """
    
    DEFAULT_FONT_SIZE = 11
    DEFAULT_FONT = qt.QFont('Arial', DEFAULT_FONT_SIZE, 10, False)  

    def __init__(self, Setting = None):
        """ 
        @param Setting: The Setting to associate with the widget 
            (i.e. Setting_Details)
        @type Setting: Setting
        """
    
        super(NodeDetails, self).__init__()

        self.storedDetailsDict = None
        self.Setting = Setting
        self.currFont = NodeDetails.DEFAULT_FONT

        self._layout = qt.QFormLayout()
        self._layout.setContentsMargins(0,0,0,0)

        self.numColumns = 2
            
        self.__textViewer = qt.QTextEdit(self)
        self.__textViewer.setReadOnly(True)
        self.__textViewer.setObjectName('nodeDetails')
        self.__textViewer.setStyleSheet('#nodeDetails{border: none;}')
        self.__textViewer.verticalScrollBar().setFixedWidth(15)

        self._layout.addWidget(self.__textViewer)
        self.setLayout(self._layout)

        
        self.__showEmptyMetadata = True

        self.Setting.Events.onEvent('SHOWEMPTY', self.__toggleEmptyMetadata)
        #--------------------
        # NOTE: We call this so that the callback above will sync before load.
        #-------------------- 
        self.Setting.syncToFile()
        self.updateFromSettings()
        



    def changeFontSize(self, size):
        """
        Changes the font size of the widget.

        @param size: The size of the font.
        @type size: int
        """
        self.currFont.setPointSize(size)
        self.__textViewer.setFont(self.currFont)


        #--------------------
        # Adaptive style
        #--------------------          
        if (size <= 10):
            self.numColumns = 3
        else:
            self.numColumns = 2

        #MokaUtils.debug.lf(self.currFont.pointSize())



        
    def __toggleEmptyMetadata(self, checked):
        """
        Stores the internal variable to show empty metadata values.

        @param checked: Whether to show the empty metadata.
        @type checked: bool
        """

        self.__showEmptyMetadata = checked
        self.setXnatNodeText(None)



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
                     NodeDetails.DEFAULT_FONT_SIZE
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
        # Adjusts the scrollbar -- minor Qt bug.
        #--------------------        
        self.__textViewer.verticalScrollBar().setStyleSheet(\
                       'left: ' + 
                        str(self.__textViewer.width - 15) + 'px; ' + 
                        'width: 15px')


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
        value = ''
        for key, value in detailsDict.iteritems():
            if key in storedMetadata:
                if key in Xnat.metadata.DEFAULT_DATE_TAGS:
                    #print value
                    value = XnatSlicerUtils.makeDateReadable(value)

                value = value.strip()
                if len(value) == 0 and self.__showEmptyMetadata == False:
                    continue
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





    def setXnatNodeText_old(self, detailsDict):
        """ 
        @deprecated
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
