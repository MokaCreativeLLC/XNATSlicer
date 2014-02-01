from __main__ import qt




comment = """
HoverButton is a customized QWidget where the
user can set the style of the button upon hovering.

TODO:
"""




class HoverButton (qt.QPushButton):
    """ Descriptor above.
    """
    
    def __init__(self, parent = None):
        """ Init function.
        """

        #--------------------
        # Call parent init.
        #--------------------
        if parent:
            super(HoverButton, self).__init__(parent)
        else:    
            super(HoverButton, self).__init__(self)


            
        #--------------------
        # Install the event filter to 
        # interpret the hovers.
        #--------------------
        self.installEventFilter(self)


        
        #--------------------
        # Track the stylesheets for
        # the hover/not-hovered states.
        #--------------------
        self.defaultStyleSheet = None
        self.hoverStyleSheet = None
        



    def setDefaultStyleSheet(self, styleSheet):
        """ Set stylesheet for when the mouse is
            not hovering over the button.
        """
        self.defaultStyleSheet = styleSheet
        self.setStyleSheet(styleSheet)
        

        
        
    def setHoverStyleSheet(self, styleSheet):
        """ Set stylesheet for when the mouse is
            hovering over the button.
        """
        self.hoverStyleSheet = styleSheet

        

        
    def eventFilter(self, widget, event):
        """ Event filter function inherited from
            QObject.  Specifically targets the 'Enter'
            and 'Leave' events for hovering purposes.
        """
        if event.type() == qt.QEvent.Enter:
            self.onHoverEnter()

        elif event.type() == qt.QEvent.Leave:
            self.onHoverLeave()


    

    def onHoverEnter(self):
        """ Callback when the mouse begins 
            hovering over the button: applies the
            'hoverStyleSheet'.
        """
        self.setStyleSheet(self.hoverStyleSheet)
        


        
    def onHoverLeave(self):
        """ Callback when the mouse leaves 
            hovering over the button: applies the
            'defaultStyleSheet'.
        """
        self.setStyleSheet(self.defaultStyleSheet)


        
        


