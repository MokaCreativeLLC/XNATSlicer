from __main__ import qt

import os
import glob
import sys




comment = """
FingerTabWidget is a subclass of QWidget that allows for the creation
and display of finger-tabbed pages.  Finger tabs are horizontally layed out tabs
on the left of a given widget.

TODO:
"""




class FingerTabWidget(qt.QWidget):
    """ Descriptor above.
    """
    
    def __init__(self, parent, *args, **kwargs):
        """ Init function.
        """

        super(FingerTabWidget, self).__init__(parent)

        
        
        #--------------------
        # Define sizing parameters.
        #--------------------          
        self.marginVal = 5
        self.currentIndex = 0
        self.tabWidth = 120


    
        #--------------------
        # Make and style 'tabColumn', which is a qFrame.
        #--------------------  
        self.tabColumn = qt.QFrame(self)
        self.tabColumn.setFixedWidth(self.tabWidth)
        self.tabColumn.setObjectName('tabColumn')
        self.tabColumn.setStyleSheet('#tabColumn {background:#E8E8E8 ; height: 4000px;' + 
                                     'border-right-width: 1px;  border-right-color: gray;' + 
                                     'border-right-style: solid; margin-top: 5px;' +  
                                     'margin-left: 5px; margin-bottom: 5px}')



        #--------------------
        # Define the layout of the 'tabColumn' qFrame, 
        # set the layout to the 'tabColumn' qFrame.
        #--------------------  
        self.tabColumnLayout = qt.QVBoxLayout()
        self.tabColumnLayout.setContentsMargins(0,0,0,0)
        self.tabColumnLayout.setSpacing(0)
        self.tabColumnLayout.addStretch()
        self.tabColumn.setLayout(self.tabColumnLayout)

        

        #--------------------
        # Define the 'innerWindowLayout'.
        #--------------------  
        self.innerWindowLayout = qt.QStackedLayout()
        self.innerWindowLayout.setStackingMode(1)
        self.innerWindowLayout.setSpacing(0)
        self.innerWindowLayout.setContentsMargins(0,0,0,0)


        
        #--------------------
        # Define the 'widgetStack' object, which takes
        # the whole span of the window.
        #--------------------  
        self.widgetStack = qt.QWidget(self)
        self.widgetStack.setObjectName("widgetStack")
        self.widgetStack.setStyleSheet("#widgetStack{ border: none; background: transparent}")



        #--------------------
        # The layout for the 'widgetStack' is 
        # 'widgetStackLayout', which is an HBoxLayout.  We set 
        # a left spacing the length of the tabs-1 to accomodate for the border
        # and tabs of the widget.
        #--------------------  
        self.widgetStackLayout = qt.QHBoxLayout()
        self.widgetStackLayout.setContentsMargins(0,self.marginVal,self.marginVal,self.marginVal)
        self.widgetStackLayout.addSpacing(self.tabWidth - 1)
        self.widgetStack.setLayout(self.widgetStackLayout)



        #--------------------
        # Define the 'tabPageStack', add to the widgetStackLayout.
        #
        # NOTE: The 'tabPageStack' is the stacked layout were all
        # of the tab pages reside.
        #--------------------         
        self.tabPageStack = qt.QStackedLayout()
        self.widgetStackLayout.addLayout(self.tabPageStack)

        
        
        #--------------------
        # Define the tabButtons as part of a 
        # button group, for easier event listening.
        #
        # Set their styles as well.
        #--------------------    
        self.buttonGroup = qt.QButtonGroup(self)
        self.buttonGroup.connect('buttonClicked(QAbstractButton*)', self.onTabClicked)
        self.tabButtons = []
        self.tabWidgets = []
        self.tabObjectName = 'fingerTab'
        self.tabToggledStyle =  '#fingerTab {border: 1px solid gray;    border-right-width: 1px;  border-right-color: white; background-color: white;}'
        self.tabUntoggledStyle ='#fingerTab {border: 1px solid #D0D0D0; border-right-width: 1px;  border-right-color: gray;  background-color: #C0C0C0;}'
        self.tabToggledFont = qt.QFont('Arial', 12, 100, False)
        self.tabUntoggledFont = qt.QFont('Arial', 12, 25, False)


        
        #--------------------
        # Add 'tabColumn' and 'widgetStack' to 'innerWindowLayout'.  Set the current
        # index of the widgetStack (this will allow for the black
        # borders between the tabs and the windows to connect).
        #--------------------  
        self.innerWindowLayout.addWidget(self.tabColumn)
        self.innerWindowLayout.addWidget(self.widgetStack)
        self.innerWindowLayout.setCurrentIndex(1)

        

        #--------------------
        # Set 'mainWidgetLayout' to hold the 'innerWindowLayout'.
        # The 'mainWidgetLayout' exists because subclasses of 
        # 'FingerTabWidget' and others that use it can add
        # further rows to the window (such as 'Done' and 'Cancel'
        # buttons).
        #--------------------  
        self.mainWidgetLayout = qt.QVBoxLayout()
        self.mainWidgetLayout.setContentsMargins(5,5,5,5)
        self.mainWidgetLayout.addLayout(self.innerWindowLayout)


        
        #--------------------
        # Set the primary layout to the 'mainWidgetLayout'
        #--------------------
        self.setLayout(self.mainWidgetLayout)

        

        
    def onTabClicked(self, tab):
        """ Event function for when a user clicks on the tab.
            Steps described below.
        """

        #--------------------
        # Set the tab's style depending on its
        # checked state.
        #--------------------
        if tab.checked:
            tab.setStyleSheet(self.tabToggledStyle)
            tab.setFont(self.tabToggledFont)
        else:
            tab.setStyleSheet(self.tabUntoggledStyle)



        #--------------------
        # Uncheck all of the other tabs
        # that are not the one provided in 
        # the argument of this function.
        #--------------------            
        for tabWidget in self.tabButtons:
            if tabWidget != tab:
                tabWidget.setChecked(False)
                tabWidget.setStyleSheet(self.tabUntoggledStyle)
                tabWidget.setFont(self.tabUntoggledFont)



                
        #--------------------
        # Find the index
        # value of the the 'tab' and 
        # match it to the tabPageStack's 
        # current index.
        #--------------------      
        ind = -1
        for i in range(0, len(self.tabButtons)):
            if self.tabButtons[i] == tab:
                ind = i
                break


            

        #--------------------
        # Track the index and set the 
        # tabPageStack to view the index.
        #--------------------  
        self.currentIndex = ind
        self.tabPageStack.setCurrentIndex(ind)
        



    def setTabFont(self, font):
        """ As stated.
        """
        for tab in self.tabButtons:
            tab.setFont(font)


            

    def setCurrentIndex(self, index):
        """ Programatically sets the current
            index both in terms of the active buttons
            and the active tab page.
        """
        self.currentIndex = index
        self.tabButtons[index].setChecked(True)
        self.onTabClicked(self.tabButtons[index])

        
        
                
    def makeTabButton(self, tabName):
        """ As stated.
        """
        button = qt.QPushButton(tabName, self)
        button.setFixedWidth(self.tabWidth - self.marginVal)
        button.setFixedHeight(25)
        button.setObjectName(self.tabObjectName)
        button.setStyleSheet(self.tabUntoggledStyle)
        button.setCheckable(True)
        return button



    

    def addTab(self, innerContentsWidget, tabName):
        """ Creates a tab button and an inner contents widget
            to add to the tabPage stack. The arguments are 'innerContentsWidget' 
            which is the inner contents and the 'tabName.'
        """

        
        #--------------------
        # Make the tabButton and add it to the 'tabColumnLayout'
        #--------------------  
        tabButton = self.makeTabButton(tabName)
        self.tabColumnLayout.insertWidget(len(self.tabButtons), tabButton)

        

        #--------------------
        # Track both the new tabButton and the 
        # 'innerContentsWidget'
        #-------------------- 
        self.tabButtons.append(tabButton)
        self.tabWidgets.append(innerContentsWidget)
        


        #--------------------
        # Add the new tabButton to the
        # 'buttonGroup' parameter.
        #-------------------- 
        self.buttonGroup.addButton(tabButton)


        
        #--------------------
        # Add the 'innerContentsWidget' to the 'tabPageStack'
        #--------------------  
        self.tabPageStack.addWidget(innerContentsWidget)



        #--------------------
        # Reset the layout and set the current index 
        # to the top tab.
        #-------------------- 
        self.setLayout(None)
        self.setLayout(self.innerWindowLayout)
        self.innerWindowLayout.setCurrentIndex(0)
