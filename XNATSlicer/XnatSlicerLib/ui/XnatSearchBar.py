from __main__ import vtk, ctk, qt, slicer

import os
import sys
import shutil



comment = """
XnatSearchBar constructs the UI components for the search
bar. It should be noted that the XnatSearchBar class does
not contain the methods for conducting a search on an XNAT 
host, rather it allows the user to connect the 'returnPressed'
signal of the searchLine to a search method of their choice.

TODO:        
"""



class XnatSearchBar(qt.QFrame):
    """ Descriptor above.
    """
    
    def __init__(self, MODULE):
        """ Init function.
        """

        #--------------------------------
        # Call parent __init__
        #--------------------------------       
        super(XnatSearchBar, self).__init__(self)



        #--------------------------------
        # Class vars.
        #--------------------------------        
        self.MODULE = MODULE
        self.prevText = None
        self.defaultSearchText = 'Search projects, subjects and experiments...'


        
        #--------------------------------
        # The search box (qt.QLineEdit)
        #--------------------------------
        self.searchLine = qt.QLineEdit()
        

        
        #--------------------------------
        # The search button
        #--------------------------------
        self.button = qt.QPushButton('')
        self.button.setIcon(qt.QIcon(os.path.join(self.MODULE.GLOBALS.LOCAL_URIS['icons'], 'x.png')) )
        size = qt.QSize(26,26)
        self.button.setFixedSize(size)
        self.button.connect('clicked()', self.onClearButtonClicked)
      

        
        #--------------------------------
        # Search Layout
        #--------------------------------
        self.searchLayout = qt.QHBoxLayout()        
        self.searchLayout.addWidget(self.searchLine)
        self.searchLayout.addWidget(self.button)



        #--------------------------------
        # Set the layout.
        #--------------------------------       
        self.setLayout(self.searchLayout)


        
        #--------------------------------
        # AESTHETICS
        #--------------------------------  
        #
        # Widget aesthetics
        #
        self.setStyleSheet('border: 1px solid rgb(160,160,160); border-radius: 3px;')
        self.setFixedHeight(22)
        #
        # Search box aesthetics
        #
        self.searchLine.setStyleSheet("border: none")
        #
        # Button aesthetics
        #
        self.button.setStyleSheet("border: none")
        self.button.setFixedHeight(20)
        #
        # Layout aesthetics
        #
        self.searchLayout.setContentsMargins(0,0,0,0)

        

        #--------------------------------
        # Event filter (for clearing and 
        # inputting default text).
        #--------------------------------
        self.searchLine.installEventFilter(self)



        #--------------------------------
        # Clear the search line at first.
        #--------------------------------
        self.onClearButtonClicked()


        
    def eventFilter(self, ob, event):
        """ Event filter to for searchLine events.
        """
        if event.type() == qt.QEvent.FocusIn:
            self.onSearchLineFocused()


            
        #--------------------------------
        # If we focus out of the the 
        # search line, and there's no text,
        # we apply the 'clear' method.
        #--------------------------------
        elif event.type() == qt.QEvent.FocusOut:
            if len(self.searchLine.text.strip(' ')) == 0:
                self.onClearButtonClicked()
            

                

    def applyTextStyle(self, mode):
        """ Applies a stylistic change to text depending on the
            'mode' argument specified.  Empty searchLines are 
            italicized.
        """
        if mode == 'empty':
            self.searchLine.setFont(self.MODULE.GLOBALS.LABEL_FONT_ITALIC) 
            palette = qt.QPalette();
            color = qt.QColor(150,150,150)
            palette.setColor(6, color);
            self.searchLine.setPalette(palette);
            self.searchLine.update()
            self.searchLine.setFont(self.MODULE.GLOBALS.LABEL_FONT_ITALIC) 
            self.searchLine.setObjectName("searchLine")
            self.searchLine.setStyleSheet("#searchLine {color: lightgray; border: none}")
        
        elif mode == 'not empty':
            self.searchLine.setStyleSheet("#searchLine {color: rgb(20,40, 200); border: none}")
            self.searchLine.setFont(self.MODULE.GLOBALS.LABEL_FONT) 
            palette = qt.QPalette();
            color = qt.QColor(0,0,0)
            palette.setColor(6, color);
            self.searchLine.setPalette(palette);


            
        
    def onSearchLineFocused(self):
        """ Signal method for when the user interacts with the 
            searchLine.  We reapply the default text if the user
            clears the search line or deletes all the way to the 
            0 cursor position.
        """


        #print "SEARCH LINE FOCUSED"
        #--------------------------------
        # Clear the default string in the searchLine
        # once the user clicks on the line
        #--------------------------------
        if self.defaultSearchText in str(self.searchLine.text): 
            self.applyTextStyle('not empty')
            self.searchLine.setText('')


            
        #--------------------------------
        # Store the previous text.
        #--------------------------------
        self.prevText = self.searchLine.text
            

            

    def onClearButtonClicked(self):
        """ Callback function for when the clear button is clicked.
            Applies the default text in the searchLine and awaits the
            user to click ont the searchLine so it can clear it by linking
            the 'cursorPositionChanged' signal to 'onSearchBoxCursorPositionChanged'
            function.
        """

        
        self.searchLine.setText(self.defaultSearchText)
        self.applyTextStyle('empty')
        self.prevText = None
        
        try:
            self.MODULE.XnatViewer.setNoResultsWidgetVisible(False)
            self.MODULE.XnatView.filter_all()
            self.MODULE.XnatView.defaultFilterFunction()
            self.MODULE.XnatView.refreshColumns()
        except Exception, e:
            #print self.MODULE.utils.lf(), str(e)
            pass


        

    def getText(self):
        """ As stated.  Generic method for classes that access
            the XnatSearchBar without going into the depth of 
            the widget
        """
        return self.searchLine.text.strip()



    
    def getButton(self):
        """ Returns the button of the XnatSearchBar, which
            is the 'clear' button.
        """
        return self.button


    

    def getSearchLine(self):
        """ As stated.
        """
        return self.searchLine


    

    def connect(self, function):
        """ For external classes to link the 'returnPressed' signal
            to a given function.  In this case, it's a search method
            provided by the XnatView class (and subclasses) and
            the XnatIo class.
        """
        self.searchLine.connect("returnPressed()", function)
    
