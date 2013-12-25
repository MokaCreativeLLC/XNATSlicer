from __main__ import vtk, qt, ctk, slicer

import math

comment =  """
XnatPopup and its children are used for any needed popup interaction with XNAT.
It's a generic class that allows the user to create popups for any number
of purposes.  The popups are QWidgets but could be more specific QWindow classes
as well.

This file contains the subclasses of XnatPopup as well: XnatDownloadPopup.


MODALITIES:
(from: http://harmattan-dev.nokia.com/docs/library/html/qt4/qt.html#WindowModality-enum)

0   Qt::NonModal		    The window is not modal and does not block input to other windows.

1   Qt::WindowModal		    The window is modal to a single window hierarchy and blocks input to 
                            its parent window, all grandparent windows, and all siblings of its 
                            parent and grandparent windows.
                            
2   Qt::ApplicationModal	The window is modal to the application and blocks input to all windows.


TODO:
"""



class XnatPopup(qt.QWidget):
    """ Popup class for XNAT-relevant interactions
    """
    
    def __init__(self, MODULE, title = "XnatPopup", modality = 1):
        """ Init function.
        """
        #--------------------
        # Call parent init.
        #--------------------
        super(XnatPopup, self).__init__(self)
        self.MODULE = MODULE
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
        
        if position:
            mainWindow = slicer.util.mainWindow()
            screenMainPos = mainWindow.pos
            x = screenMainPos.x() + mainWindow.width/2 - self.width/2
            y = screenMainPos.y() + mainWindow.height/2 - self.height/2
            self.move(qt.QPoint(x,y))
        
        self.raise_()
        qt.QWidget.show(self)
        

        

        
class XnatDownloadPopup(XnatPopup):
    """ Subclass of the XnatPopup class pertaining
        specifically to downloading files.
    """

    def __init__(self, MODULE, title = "XNAT Download Queue", memDisplay = "MB"):
        """ Init funnction.
        """
        super(XnatDownloadPopup, self).__init__(MODULE = MODULE, title = title)
        self.memDisplay = memDisplay
        
        self.downloadRows = {}

        self.setFixedWidth(500)
        self.setMinimumHeight(300)
        self.setStyleSheet('padding: 0px')

        self.innerWidget = None
        self.innerWidgetLayout = None
        self.scrollWidget = None


        self.masterLayout.setContentsMargins(0,0, 0, 0)
        self.hide()

        #for i in range(0, 10):
        #    self.addDownloadRow('easdfasdfasdfasdf/AAAAAAAAADDDDDDDDDDDDDDDDDDDDD/333333333333333333333333/%s/asdf.asdf'%(i))




        


    def addDownloadRow(self, uri, size = -1):
        """
        """
        
        rowWidget = qt.QWidget()
        rowWidget.setObjectName('downloadRowWidget')
        rowWidget.setStyleSheet('#downloadRowWidget {border: 1px solid rgb(160,160,160); border-radius: 2px; width: 100%;}')
        rowWidget.setFixedHeight(90)
        rowWidget.setSizePolicy(qt.QSizePolicy.MinimumExpanding, qt.QSizePolicy.MinimumExpanding)
        layout = qt.QFormLayout()
        rowWidget.setLayout(layout)
        #rowWidget.setEnabled(False)


        
        textEdit = qt.QTextEdit("Checking: '%s'<br>Please wait...<br>"%(self.abbreviateFile(uri)))
        textEdit.setStyleSheet("border: none")
        textEdit.setFixedHeight(60)
        layout.addRow(textEdit)
        

        progressBar = qt.QProgressBar(rowWidget)
        progressBar.setFixedHeight(17)
        progressBar.setMinimum(0)
        #progressBar.setTextVisible(False)
        progressBar.setAlignment(0x0084)
        layout.addRow(progressBar)

        
        #-------------------
        # Cancel button row
        #-------------------

        cancelButton = qt.QPushButton()
        cancelButton.setText("Cancel")
        cancelButton.setFont(self.MODULE.GLOBALS.LABEL_FONT) 
        def cancelClick():
            rowWidget.setEnabled(False)
            textEdit.setText("Cancelled: '%s'<br>"%(self.abbreviateFile(uri)))
            self.MODULE.XnatIo.cancelDownload(uri)
            self.MODULE.XnatView.setEnabled(True)
        cancelButton.connect('pressed()', cancelClick)
        cancelButton.setFixedWidth(60)
        cancelButton.setFixedHeight(15)
        cancelRow = qt.QHBoxLayout()
        cancelRow.addStretch()
        cancelRow.addWidget(cancelButton)
        layout.addRow(cancelRow)
        
        
        downloadRow = {
            'queuePosition': len(self.downloadRows),
            'size': -1, 
            'downloaded': 0,
            'textEdit': textEdit,
            'progressBar': progressBar,
            'widget': rowWidget
        }

        self.downloadRows[uri] = downloadRow
        self.remakeWidget()


        

    def remakeWidget(self):
        """ Ideally, this would be unncessary.  But, since QScrollArea doesn't
            dynamically update, we have to update this ourselves.
        """
        

        if self.innerWidget:
            del self.innerWidget
        if self.innerWidgetLayout:
            del self.innerWidgetLayout
        if self.scrollWidget:
            del self.scrollWidget
        
        self.innerWidgetLayout = qt.QFormLayout()
        self.innerWidgetLayout.setVerticalSpacing(10)

        
        for key, item in self.downloadRows.iteritems():
            self.innerWidgetLayout.addRow(item['widget'])

       
        
        self.innerWidget = qt.QWidget()
        self.innerWidget.setLayout(self.innerWidgetLayout)
        self.innerWidget.setObjectName('innerWidget')
        self.innerWidget.setStyleSheet('#innerWidget {width: 100%;}')
        self.innerWidget.setSizePolicy(qt.QSizePolicy.MinimumExpanding, qt.QSizePolicy.MinimumExpanding)

        
        self.scrollWidget = qt.QScrollArea()
        self.scrollWidget.setWidget(self.innerWidget)
        self.scrollWidget.verticalScrollBar().setStyleSheet('width: 15px')
        self.scrollWidget.setObjectName('scrollWidget')
        self.scrollWidget.setStyleSheet('#scrollWidget {border: none}')
        self.scrollWidget.setSizePolicy(qt.QSizePolicy.MinimumExpanding, qt.QSizePolicy.MinimumExpanding)
        self.scrollWidget.setWidgetResizable(True)
      

    
        delWidget = self.masterLayout.itemAt(0)
        while (delWidget):
            self.masterLayout.removeItem(delWidget)
            del delWidget
            delWidget = self.masterLayout.itemAt(0)
        
        self.innerWidget.update()
        self.masterLayout.addRow(self.scrollWidget)
        self.setSizePolicy(qt.QSizePolicy.MinimumExpanding, qt.QSizePolicy.MinimumExpanding)
        self.update()
        


    def setText(self, uriKey, text):
        """
        """
        self.downloadRows[uriKey]['textEdit'].setText(text)



    def setSize(self, uriKey, size):
        """
        """
        self.downloadRows[uriKey]['size'] = self.recalcMem(size)

        
    def updateDownload(self, uriKey, downloaded = 0):
        """
        """
        self.downloadRows[uriKey]['downloaded'] = self.recalcMem(downloaded)
        self.downloadRows[uriKey]['textEdit'].setText("Downloading: <i>'%s'</i><br><br>%sMB out of %sMB<br>"%(self.abbreviateFile(uriKey),  
                                                                                                      self.downloadRows[uriKey]['downloaded'], 
                                                                                                      self.downloadRows[uriKey]['size']))
        self.downloadRows[uriKey]['progressBar'].setValue((self.downloadRows[uriKey]['downloaded']/self.downloadRows[uriKey]['size']) * 100)
        

        
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


    
        


    def recalcMem(self, size):
        """ For toggling between MB display and byte
            display.
        """
        if (self.memDisplay.lower() == 'mb'):
            return math.ceil(self.MODULE.utils.bytesToMB(size) * 100)/100
        return size      



    
    def setDownloadFileSize(self, uriKey, size):
        """ Descriptor
        """
        if size:
            self.downloadRows[uriKey]['size'] = size
            self.downloadRows[uriKey]['progressBar'].setMinimum(0)
            self.downloadRows[uriKey]['progressBar'].setMaximum(100)
            #3size = self.recalcMem(size)
            #self.lines[2].setText(self.lines[2].text.replace('[Unknown total]', str(size)))



            
    def updateText(self, downloadedBytes):
        """ Updates the progress bar in the popup accordingly with 
            'downloadedBytes' argument.
        """

        #-------------------
        # Format the downloaded bytes to human-readable and
        # display.
        #-------------------        
        if downloadedBytes > 0:
            self.downloadedBytes = int(downloadedBytes)
            size = self.downloadedBytes
            #
            # Memory display
            #
            size = self.recalcMem(size)
            #
            # Update display
            #
            self.lines[2].setText('%s MB out '%(str(size)) + self.lines[2].text.split('out')[1][1:])


            
        #-------------------
        # If we know the size of downloaded files, change
        # that label accordingly.
        #-------------------
        if self.downloadFileSize:
            #
            # Calculate download pct
            #
            pct = float(float(self.downloadedBytes) / float(self.downloadFileSize))
            #
            # Output to Python command prompt
            #print "%s %s Downloaded: %s\tDownloadSize: %s\tPct: %s"%(self.MODULE.utils.lf(), self.lines[0].text, self.downloadedBytes , self.downloadFileSize, pct)
            #
            #
            # Update progress bar
            #
            self.progBar.setValue(pct * 100)
            

        
        
        
    

