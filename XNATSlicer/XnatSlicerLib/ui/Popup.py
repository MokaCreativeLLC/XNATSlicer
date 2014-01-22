# python
import math

# application
from __main__ import qt, slicer

# external
from Xnat import *
from MokaUtils import *

# module
from XnatSlicerUtils import *
from XnatSlicerGlobals import *




class XnatClearScenePopup(qt.QMessageBox):
    """
    Popup and its children are used for any needed popup interaction with XNAT.
    It's a generic class that allows the user to create popups for any number
    of purposes.  The popups are QWidgets but could be more specific QWindow classes
    as well.
    
    This file contains the subclasses of Popup as well: XnatDownloadPopup.
    
    
    MODALITIES:
    (from: http://harmattan-dev.nokia.com/docs/library/html/qt4/qt.html#WindowModality-enum)
    
    0   Qt::NonModal		    The window is not modal and does not block input to other windows.
    
    1   Qt::WindowModal		    The window is modal to a single window hierarchy and blocks input to 
    its parent window, all grandparent windows, and all siblings of its 
    parent and grandparent windows.
    
    2   Qt::ApplicationModal	The window is modal to the application and blocks input to all windows.
    
    """


    def __init__(self, title = "Clear current scene", modality = 1):

        """
        """
        #--------------------
        # Call parent init.
        #--------------------
        super(XnatClearScenePopup, self).__init__(self)
        
        self.setStandardButtons(qt.QMessageBox.Yes | qt.QMessageBox.No)
        #self.setTitle(title)
        #self.setWindowModality(modality)
        self.setDefaultButton(qt.QMessageBox.No)
        self.setText("Clear the current scene?")


        
    

class XnatEmptyPopup(qt.QWidget):
    """ 
    Popup class for XNAT-relevant interactions
    """
    
    def __init__(self, title = "Popup", modality = 1):
        """ 
        Init function.
        """
        #--------------------
        # Call parent init.
        #--------------------
        super(XnatEmptyPopup, self).__init__(self)

        self.spacer = qt.QLabel("\n\n\n")


        self.windowTitle = title
                
        self.setWindowModality(modality)
        self.hide()
        
        self.masterLayout = qt.QFormLayout()
        self.setLayout(self.masterLayout)
        #self.hide()


        
        
    def show(self, position = True):
        """ Generic show function.  Repositions the
            popup to be cenetered within the slicer app.
        """
        
        self.raise_()
        qt.QWidget.show(self)
        XnatSlicerUtils.repositionToMainSlicerWindow(self, 'center')
        


        
        
class XnatTextPopup(XnatEmptyPopup):
    """
    A sublcass of Popup that displays text.
    """
    def __init__(self, text = 'Empty Text', title = ''):
        """ 
        @param text: The rich text value to display.
        @type text: string

        @param title: The window title.
        @type title: string
        """
        super(XnatTextPopup, self).__init__(title = title)

        self.setFixedHeight(70)
        self.textEdit = qt.QTextEdit(text)
        self.textEdit.setAlignment(0x0084)
        self.textEdit.setStyleSheet('border: none')

        emptyRow = qt.QLabel('')
        self.masterLayout.addRow(emptyRow)
        self.masterLayout.addRow(self.textEdit)

        

        
        
class XnatDownloadPopup(XnatEmptyPopup):
    """ 
    Subclass of the Popup class pertaining
    specifically to downloading files.
    """

    def __init__(self, title = "XNAT Download Queue", memDisplay = "MB"):
        """ 
        @param title: The window title.
        @type title: string

        @param memDisplay: The memory value to display.
        @type memDisplay: string
        """
        super(XnatDownloadPopup, self).__init__(title = title)
        self.memDisplay = memDisplay
        
        self.downloadRows = {}

        self.setFixedWidth(710)
        self.setMinimumHeight(260)
        self.setStyleSheet('padding: 0px')

        self.innerWidget = None
        self.innerWidgetLayout = None
        self.scrollWidget = None


        self.masterLayout.setContentsMargins(0,0, 0, 0)
        self.hide()
        self.cancelCallback = None

        self.rowWidgetHeight = 75
        #self.show()
        #for i in range(0, 10):
        #    self.addDownloadRow('projects/fooProject/subjects/fooSuject/experiments/fooExperiments/scans/fooScan/%s/files/foo_%s.dcm'%(i, i))



    def setCancelCallback(self, callback):
        """
        """
        self.cancelCallback = callback
        


    def addDownloadRow(self, uri, size = -1):
        """ Constructs a download row object based
            on the URI
        """


        #-------------------
        # Cancel button row
        #-------------------
        rowWidget = qt.QWidget()
        rowWidget.setObjectName('downloadRowWidget')
        rowWidget.setStyleSheet('#downloadRowWidget {border: 1px solid rgb(160,160,160); border-radius: 2px; width: 100%;}')
        rowWidget.setFixedHeight(self.rowWidgetHeight)
        rowWidget.setSizePolicy(qt.QSizePolicy.MinimumExpanding, qt.QSizePolicy.MinimumExpanding)
        layout = qt.QFormLayout()
        rowWidget.setLayout(layout)



        #-------------------
        # Text Edit
        #-------------------
        textEdit = qt.QTextEdit()
        textEdit.setStyleSheet("border: none")
        textEdit.setFixedHeight(40)
        textEdit.verticalScrollBar().hide()
        textEdit.setFont(qt.QFont(XnatSlicerGlobals.FONT_NAME, XnatSlicerGlobals.FONT_SIZE, 10, False))
        layout.addRow(textEdit)
        

        
        #-------------------
        # Progress Bar
        #-------------------
        progressBar = qt.QProgressBar(rowWidget)
        progressBar.setFixedHeight(17)
        progressBar.setFixedWidth(600)
        progressBar.setMinimum(0)
        progressBar.setMaximum(100)
        progressBar.setAlignment(0x0084)
        

        
        #-------------------
        # Cancel button row
        #-------------------
        cancelButton = qt.QPushButton()
        cancelButton.setText("Cancel")
        cancelButton.setFont(XnatSlicerGlobals.LABEL_FONT) 
        cancelButton.setFixedWidth(60)
        cancelButton.setFixedHeight(19)



        #-------------------
        # Progress bar row
        #-------------------
        progressRow = qt.QHBoxLayout()
        progressRow.addWidget(progressBar)
        progressRow.addStretch()
        progressRow.addWidget(cancelButton)
        layout.addRow(progressRow)
        


        #-------------------
        # Row dict
        #-------------------
        downloadRow = {
            'queuePosition': len(self.downloadRows),
            'size': 0, 
            'downloaded': 0,
            'textEdit': textEdit,
            'pathDict': XnatSlicerUtils.getXnatPathDict(uri),
            'progressBar': progressBar,
            'widget': rowWidget,
            'cancelButton': cancelButton
        }


        
        #-------------------
        # default text
        #-------------------
        dlStr = self.makeDownloadPath(downloadRow['pathDict'])
        textEdit.setText("QUEUED<br>%s<br>Please wait...<br>"%(dlStr))


        #-------------------
        # Cancel callback
        #-------------------
        def cancelClick():
            rowWidget.setEnabled(False)
            #print "Cancelling download '%s'"%(dlStr)
            textEdit.setText(textEdit.toHtml().replace('DOWNLOADING', 'CANCELLED'))
            for key, item in self.downloadRows.iteritems():
                if item['progressBar'] == progressBar:
                    item['progressBar'].setEnabled(False)
                    item['progressBar'].setMaximum(100)
                    self.cancelCallback(key)
        cancelButton.connect('pressed()', cancelClick)

        self.downloadRows[uri] = downloadRow
        self.remakeWidget()


        

    def remakeWidget(self):
        """ Ideally, this would be unncessary.  But, since QScrollArea doesn't
            dynamically update, we have to update this ourselves.
        """
        
        #-------------------
        # Clear all of the inner widgets
        #-------------------
        if self.innerWidget:
            del self.innerWidget
        if self.innerWidgetLayout:
            del self.innerWidgetLayout
        if self.scrollWidget:
            del self.scrollWidget


        #-------------------
        # Reset the inner widget layout
        #-------------------
        self.innerWidgetLayout = qt.QFormLayout()
        self.innerWidgetLayout.setVerticalSpacing(10)


        
        #-------------------
        # Sort download rows by their queue positions,
        # add them to the innerWidgetLayout.
        #-------------------
        sortedRows = [None] * len(self.downloadRows)
        for key, item in self.downloadRows.iteritems():
            #print len(sortedRows), item['queuePosition']
            sortedRows[item['queuePosition']] = key
        for key in sortedRows:
            self.innerWidgetLayout.addRow(self.downloadRows[key]['widget'])


            
        #-------------------
        # Remake the inner widget
        #-------------------     
        self.innerWidget = qt.QWidget()
        self.innerWidget.setLayout(self.innerWidgetLayout)
        self.innerWidget.setObjectName('innerWidget')
        self.innerWidget.setStyleSheet('#innerWidget {width: 100%;}')
        self.innerWidget.setSizePolicy(qt.QSizePolicy.MinimumExpanding, qt.QSizePolicy.MinimumExpanding)



        #-------------------
        # Remake the scroll widget
        #------------------- 
        self.scrollWidget = qt.QScrollArea()
        self.scrollWidget.setWidget(self.innerWidget)
        self.scrollWidget.verticalScrollBar().setStyleSheet('width: 15px')
        self.scrollWidget.setObjectName('scrollWidget')
        self.scrollWidget.setStyleSheet('#scrollWidget {border: none}')
        self.scrollWidget.setSizePolicy(qt.QSizePolicy.MinimumExpanding, qt.QSizePolicy.MinimumExpanding)
        self.scrollWidget.setWidgetResizable(True)
      

        
        #-------------------
        # Clear the master widget and add the new contents.
        #-------------------     
        delWidget = self.masterLayout.itemAt(0)
        while (delWidget):
            self.masterLayout.removeItem(delWidget)
            del delWidget
            delWidget = self.masterLayout.itemAt(0)
        
        self.innerWidget.update()
        self.masterLayout.addRow(self.scrollWidget)
        self.setSizePolicy(qt.QSizePolicy.MinimumExpanding, qt.QSizePolicy.MinimumExpanding)

        calcHeight = (self.rowWidgetHeight + 12)* len(self.downloadRows)
        if calcHeight < 800:
            self.setMinimumHeight(calcHeight)
        else:
            self.setMinimumHeight(800)

        self.update()
        


        
    def setText(self, uriKey, text):
        """
        """
        self.downloadRows[uriKey]['textEdit'].setText(text)


        

    def setSize(self, uriKey, size = -1):
        """
        """
        #print self.downloadRows
        uriKey = str(uriKey)
        if size > -1:
            self.downloadRows[uriKey]['size'] = self.recalcMem(size)
            self.downloadRows[uriKey]['progressBar'].setMaximum(100)
        else:
            self.downloadRows[uriKey]['progressBar'].setMinimum(0)
            self.downloadRows[uriKey]['progressBar'].setMaximum(0)


            

    def makeDownloadPath(self, pathDict):
        """
        """
        if isinstance(pathDict, basestring):
            pathDict = self.downloadRows[pathDict]['pathDict']
        dlStr = ''
        for level in Xnat.path.DEFAULT_LEVELS:
            if level in pathDict and str(pathDict[level]) != 'None':
                dlStr += "<b>%s:</b> %s  "%(level, pathDict[level])

        return dlStr
        


            
    def updateDownload(self, uriKey, downloaded = 0):
        """
        """
        
        self.downloadRows[uriKey]['downloaded'] = self.recalcMem(downloaded)

        downloadSize = str(self.downloadRows[uriKey]['size']) + 'MB'
        if downloadSize == '0MB':
            downloadSize = '[Unknown Size]'
        self.downloadRows[uriKey]['textEdit'].setText("DOWNLOADING<br>%s<br>%sMB out of %s<br>"%(self.makeDownloadPath(self.downloadRows[uriKey]['pathDict']),  
                                                                                                 self.downloadRows[uriKey]['downloaded'], 
                                                                                                 downloadSize))

        if self.downloadRows[uriKey]['size'] > 0:
            self.downloadRows[uriKey]['progressBar'].setValue((self.downloadRows[uriKey]['downloaded'] / self.downloadRows[uriKey]['size']) * 100)
        else:
            self.downloadRows[uriKey]['progressBar'].setValue(self.downloadRows[uriKey]['downloaded'])
        

            
        
    def changeRowKey(self, oldKey, newKey):
        """
        """
        self.downloadRows[newKey] = self.downloadRows.pop(oldKey)


        
        
    def resizeEvent(self):
        """ Overloaded callback when the user
            resizes the download popup window.
        """ 
        if self.scrollWidget != None:
            self.scrollWidget.resize(self.width, self.height)


        

    def abbreviateFile(self, filename):
        """
        """
        maxLen = 55
        return filename if len(filename) < maxLen else '...' + filename[-1 * (maxLen-3):]


        

    def setCancelled(self, uriKey):
        """
        Updates the relevant download row to the cancelled state.
        
        @param uriKey: The key referring to the download row.
        @type uriKey: str
        """
        self.downloadRows[uriKey]['widget'].setEnabled(False)
        self.downloadRows[uriKey]['textEdit'].setText("CANCELLED<br><i>%s</i>"%(self.makeDownloadPath(self.downloadRows[uriKey]['pathDict'])))
        



    def setFinished(self, uriKey):
        """
        Updates the relevant download row to the complete state.
        
        @param uriKey: The key referring to the download row.
        @type uriKey: str
        """
        self.downloadRows[uriKey]['widget'].setEnabled(False)
        self.downloadRows[uriKey]['textEdit'].setText("FINISHED<br><i>%s</i>"%(self.makeDownloadPath(self.downloadRows[uriKey]['pathDict'])))
        self.setProgressBarValue(uriKey, 100)
        

        

    def setEnabled(self, uriKey, enabled = True):
        """
        """
        self.downloadRows[uriKey]['widget'].setEnabled(enabled)



    def setProgressBarValue(self, uriKey, value, _min = 0, _max = 100):
        """
        """
        self.downloadRows[uriKey]['progressBar'].setMinimum(_min)
        self.downloadRows[uriKey]['progressBar'].setMaximum(_max)
        self.downloadRows[uriKey]['progressBar'].setValue(value)
        


    def recalcMem(self, size):
        """ For toggling between MB display and byte
            display.
        """
        if (self.memDisplay.lower() == 'mb'):
            return math.ceil(MokaUtils.convert.bytesToMB(size) * 100)/100
        return size      



    
    def setDownloadFileSize(self, uriKey, size):
        """ Descriptor
        """
        if size:
            self.downloadRows[uriKey]['size'] = size
            self.downloadRows[uriKey]['progressBar'].setMinimum(0)
            self.downloadRows[uriKey]['progressBar'].setMaximum(100)



            

            

        
        
        
    

