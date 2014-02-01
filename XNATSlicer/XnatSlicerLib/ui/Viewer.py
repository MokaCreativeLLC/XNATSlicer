from __main__ import qt, slicer




comment = """
Viewer is a class that holds the various widgets allowing
for viewing and interacting with XNAT.  These widgets include:
SearchBar, View (View_Tree) and the load/save buttons
from Buttons.  One of the main reasons it exists is to allow
for the 'No Search Results Found' label to be displayed on top
of the View in a user-friendly way (stacked widget).

Viewer inherits from QWidget.

TODO:
"""




class Viewer(qt.QWidget):
    """ Descriptor above.
    """

    def __init__(self, MODULE = None):
        """ Init function.
        """

        super(Viewer, self).__init__(self)
        self.MODULE = MODULE

        

        #--------------------
        # Make label to display when no search
        # results are found.
        #--------------------       
        self.noSearchResultsFound = qt.QLabel("<i>No results found.</i>", self)
        self.noSearchResultsFound.setStyleSheet('color: gray; margin-left: 150px; text-align: center')


        
        #--------------------
        # Make a stackedLayout and stackedWidget
        # of the View and the 'noSearchResultsFound'
        # label.  We create a 'stackedWidget' because we need
        # a widget to feed into the viewerLayout, which is a 
        # QGridLayout. We then set the index to the View --
        # the View will call 'setNoResultsWidgetVisible'
        # if there are no search results.
        #--------------------          
        self.stackedLayout = qt.QStackedLayout(self)
        self.stackedLayout.addWidget(self.noSearchResultsFound)
        self.stackedLayout.addWidget(self.MODULE.View)
        self.stackedLayout.setCurrentIndex(1)
        self.stackedLayout.setStackingMode(1)
        self.stackedWidget = qt.QWidget(self)
        self.stackedWidget.setLayout(self.stackedLayout)


        
        #--------------------
        # Make main layout.
        #-------------------- 
        self.viewerLayout = qt.QGridLayout()  
        self.viewerLayout.addWidget(self.MODULE.SearchBar, 0, 0, 1, 1)        
        self.viewerLayout.addWidget(self.stackedWidget, 2, 0)
        self.viewerLayout.addLayout(self.MODULE.Buttons.loadSaveButtonLayout, 2, 1)
        self.setLayout(self.viewerLayout)




    def setNoResultsWidgetVisible(self, visibile):
        """ Reveals the 'noSearchResultsFound' object
            when there are no search results from the
            SearchBar.
        """
        if visibile:
            self.stackedLayout.setCurrentIndex(0)
        else:
            self.stackedLayout.setCurrentIndex(1) 
        


        
