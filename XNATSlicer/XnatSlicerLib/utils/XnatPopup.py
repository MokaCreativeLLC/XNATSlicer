from __main__ import vtk, qt, ctk, slicer



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



class XnatPopup(object):
    """ Popup class for XNAT-relevant interactions
    """
    
    def __init__(self, MODULE, title = "XnatPopup", modality = 1):
        """ Init function.
        """
        self.MODULE = MODULE
        self.spacer = qt.QLabel("\n\n\n")

        self.window = qt.QWidget()
        self.window.windowTitle = title
                
        self.window.setWindowModality(modality)
        self.window.hide()
        
        self.layout = qt.QFormLayout()
        self.window.setLayout(self.layout)
        self.window.hide()


        
        
    def show(self, position = True):
        """ Generic show function.  Repositions the
            popup to be cenetered within the slicer app.
        """
        self.window.show()
        
        if position:
            self.window.show()
            mainWindow = slicer.util.mainWindow()
            screenMainPos = mainWindow.pos
            x = screenMainPos.x() + mainWindow.width/2 - self.window.width/2
            y = screenMainPos.y() + mainWindow.height/2 - self.window.height/2
            self.window.move(qt.QPoint(x,y))
        
        self.window.raise_()
        

        
        
    def hide(self):
        self.window.hide()



        

        
class XnatDownloadPopup(XnatPopup):
    """ Subclass of the XnatPopup class pertaining
        specifically to downloading files.
    """

    def __init__(self, MODULE, title = "Xnat Download", memDisplay = "MB"):
        """ Init funnction.
        """
        super(XnatDownloadPopup, self).__init__(MODULE = MODULE, title = title)


        self.currFilename = ''
        #-------------------
        # Params
        #-------------------
        self.memDisplay = memDisplay
        self.downloadFileSize = None



        #-------------------
        # Window size
        #-------------------
        self.window.setFixedWidth(500)


        
        #-------------------
        # Line text
        #-------------------
        self.textDisp = ['', '', '[Unknown amount] ' +  self.memDisplay + ' out of [Unknown total] ' + self.memDisplay]
        self.lines = [qt.QLabel('') for x in range(0, len(self.textDisp))]
        


        #-------------------
        # Prog bar
        #-------------------
        self.progBar = qt.QProgressBar(self.window)
        self.progBar.setFixedHeight(17)



        #-------------------
        # Cancel button
        #-------------------
        self.cancelButton = qt.QPushButton()
        self.cancelButton.setText("Cancel")
        self.cancelButton.connect('pressed()', self.MODULE.XnatIo.cancelDownload)
        self.cancelButton.setFixedWidth(60)
        


        #-------------------
        # Add widgets to layout
        #-------------------
        for l in self.lines:
            self.layout.addRow(l)
        self.layout.addRow(self.progBar)



        #-------------------
        # Cancel row
        #-------------------
        cancelRow = qt.QHBoxLayout()
        cancelRow.addStretch()
        cancelRow.addWidget(self.cancelButton)
        cancelRow.addSpacing(37)
        self.layout.addRow(cancelRow)


        self.downloadCount = 1
        self.totalDownloads = 1


        self.checkFileNameNotExtension = False
        
        #-------------------
        # Clear all
        #-------------------
        self.reset()


        
        
    def reset(self, animated = True):
        """ Resets tracked parameters such as 
            the progress bar and the labels.
        """
        self.lines[0].setText(self.textDisp[0])
        self.lines[1].setText(self.textDisp[1])
        self.lines[2].setText(self.textDisp[2])


        self.progBar.setMinimum(0)

        

        #-------------------
        # If we don't want it animated, we
        # set the max to a very high number.
        #-------------------
        if animated == False:
            self.progBar.setMaximum(100000000000000)


            
        #-------------------
        # Otherise, the 
        # prog bar animates if max and min are 0
        #-------------------
        else:
            self.progBar.setMaximum(0)
      

        self.downloadFileSize = 0
        self.downloadedBytes = 0

        


    def setText(self, line1, line2, line3 = None):
        """ As stated.
        """
        #line1 = '[%s of %s] %s'%(self.downloadCount+1, self.totalDownloads, line1)
        self.lines[0].setText(line1)
        self.lines[1].setText(self.abbreviateFile(line2))
        if not line3:
            self.lines[2].setText('')
        else:
            self.lines[2].setText(line3)
            

            
    def setTotalDownloads(self, totalDownloads):
        """ As stated.
        """
        self.downloadCount = 0
        self.totalDownloads = totalDownloads


        
    def addDownloadFileCount(self):
        """ As stated.
        """
        self.downloadCount += 1
        

    def abbreviateFile(self, filename):
        """
        """
        maxLen = 55
        return filename if len(filename) < maxLen else '...' + filename[-1 * (maxLen-3):]


    
    def setCheckFileNameNotExtension(self, val):
        """
        """
        self.checkFileNameNotExtension = val


        
    def setDownloadFileName(self, filename):
        """ As stated.
        """
        print "SET DOWNLOAD FILENAME", filename          
        if filename != self.currFilename:

            if self.checkFileNameNotExtension:
                #print "SET CHECK FILENAME",  self.currFilename.rsplit('.', 1)[0] , filename.rsplit('.', 1)[0]
                if self.currFilename.rsplit('.', 1)[0] != filename.rsplit('.', 1)[0]:
                    self.addDownloadFileCount()
            else:
                self.addDownloadFileCount()

            self.currFilename = filename    
            self.lines[1].setText("'%s'"%(self.abbreviateFile(filename)))
            downloadStat = '[%s of %s]'%(self.downloadCount, self.totalDownloads)
            self.lines[0].setText(downloadStat + " Downloading:") 

        


    def recalcMem(self, size):
        """ For toggling between MB display and byte
            display.
        """
        if (self.memDisplay.lower() == 'mb'):
            return self.MODULE.utils.bytesToMB(size) 
        return size      



    
    def setDownloadFileSize(self, size):
        """ Descriptor
        """
        if size:
            self.downloadFileSize = size
            self.progBar.setMinimum(0)
            self.progBar.setMaximum(100)
            size = self.recalcMem(size)
            self.lines[2].setText(self.lines[2].text.replace('[Unknown total]', str(size)))



            
    def update(self, downloadedBytes):
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
            

        
        
        
    

