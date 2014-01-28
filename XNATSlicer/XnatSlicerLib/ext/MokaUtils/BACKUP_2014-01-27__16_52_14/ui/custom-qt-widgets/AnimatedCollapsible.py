# python
import os
import sys
import shutil

# application
from __main__ import qt, ctk

# module
from HoverButton import *




class AnimatedCollapsible(ctk.ctkExpandableWidget):
    """ 
    AnimatedCollapsible is a subclass of ctk.ctkExpandableWidget. 
    AnimatedCollapsible is designed around the premise of animating
    when the user clicks on its title button.
    
    Much like other QT widgets, the user can call 'setWidget'
    to apply contents to the inside of the widget.  Other parameters, 
    such as animation times and widgetsize, can also be set by the user.
   
    """


    EVENT_TYPES = [
        'collapseStart',
        'collapsing',
        'collapseEnd',
        'expandStart',
        'expanding',
        'expandEnd',
        'collapsed',
        'expanded',
        'animate',
    ] 

    
    def __init__(self, parent, title):
        """ 
        Init function.
        """

        if parent:
            super(AnimatedCollapsible, self).__init__(parent)
        else:
            super(AnimatedCollapsible, self).__init__(self)



        #--------------------
        # We want to grab the sizeGrip right off
        # the bat so we can control its visibility.
        #--------------------
        self.sizeGrip = self.children()[0]
        self.sizeGrip.hide()
        #self.setSizeGripInside(False)

        
        #--------------------
        # We hide the module first because
        # it creates a flikering on loadup
        #--------------------
        self.hide()


        
        #-------------------- 
        # Set the arrow characters, 
        # described accordingly.
        #--------------------    
        self.rightArrowChar = u'\u25b8'
        self.downArrowChar = u'\u25be'


        
        #-------------------- 
        # Set Collapsed Height
        #-------------------- 
        self.collapsedHeight = 30



        #-------------------- 
        # Set the min/max heights.
        #-------------------- 
        self.minExpandedHeight = 60
        self.maxExpandedHeight = 1000



        #-------------------- 
        # Set the toggleButton's height and width
        #-------------------- 
        self.toggleHeight = 16
        self.toggleWidth = 80



        #-------------------- 
        # Make sure the widget is 100% its parent's width.
        #--------------------        
        self.setStyleSheet('width: 100%')


        
        #-------------------- 
        # Set the animation duration
        #--------------------
        self.animDuration = 250


        
        #-------------------- 
        # Set the size policy
        #--------------------
        self.setSizePolicy(qt.QSizePolicy.Ignored, qt.QSizePolicy.MinimumExpanding)
        

        
        #----------------
        # Set the animation's easing curve.  See:
        # http://harmattan-dev.nokia.com/docs/library/html/qt4/qeasingcurve.html
        # for more options.
        #----------------
        self.__easingCurve = qt.QEasingCurve(6);


        
        #----------------
        # Set the minimum hieght
        #----------------
        self.setMinimumHeight(self.minExpandedHeight)
        

        
        #----------------
        # set the Title
        #----------------       
        self.title = title


        
        #----------------
        # Make the toggle button
        #----------------
        self.toggleButton = HoverButton(self)
        self.toggleButton.hide()
        self.toggleButton.setParent(self)
        self.toggleButton.setFixedHeight(self.toggleHeight)
        self.toggleButton.setCheckable(True)
        self.toggleButton.setObjectName('animatedCollapsibleToggleButton')


        buttonDefault = '#animatedCollapsibleToggleButton '
        buttonDefault += '{border: 1px solid transparent; '
        buttonDefault += 'background-color: white; margin-left: '
        buttonDefault += '5px; text-align: left; padding-left: 5px;}'
        self.toggleButton.setDefaultStyleSheet(buttonDefault)

        buttonHover = '#animatedCollapsibleToggleButton {'
        buttonHover += 'border: 1px solid rgb(200,200,200); '
        buttonHover += 'background-color: white; border-radius: 2px; '
        buttonHover += 'margin-left: 5px; text-align: left; padding-left: 5px;}'
        self.toggleButton.setHoverStyleSheet(buttonHover)
        self.__modifyToggleButton(True)
     

        
        #----------------
        # Make the internal 'frame' and set the style
        # accordingly.
        #----------------
        self.frame = qt.QFrame(self)
        #
        # Prevent style sheet inheritance from 
        # inner contents
        #
        self.frame.setObjectName('animateCollapsibleFrame')

        frameStyle = '#animateCollapsibleFrame '
        frameStyle += '{margin-top: 9px; border: '
        frameStyle += '2px solid lightgray; border-radius: 4px; padding-top: 5px; '
        frameStyle += 'padding-left: 2px; padding-right: 2px; padding-bottom: 2px}'
        self.frame.setStyleSheet(frameStyle)

        
        
        #----------------
        # Stack the button on top of the frame via a 
        # QStackedLayout
        #----------------
        self.stackedLayout = qt.QStackedLayout()
        self.stackedLayout.addWidget(self.toggleButton)
        self.stackedLayout.addWidget(self.frame)
        


        #----------------
        # To make sure the button is on top.
        #----------------
        self.stackedLayout.setCurrentIndex(0)
        self.stackedLayout.setStackingMode(1)



        #----------------
        # Set the sayout
        #----------------        
        self.setLayout(self.stackedLayout)


        
        #----------------
        # Init the animation group and callbacks.
        #----------------  
        self.animations = qt.QParallelAnimationGroup()
        self.__eventCallbacks = {}
        for key in AnimatedCollapsible.EVENT_TYPES:
            self.__eventCallbacks[key] = []
        self.__contents = []


        
        #----------------
        # Set the default states after creation.
        #----------------
        self.toggleButton.connect('toggled(bool)', self.setChecked)
        self.toggled = True


        self.sizeGrip.installEventFilter(self)
        self.installEventFilter(self)



        
    def eventFilter(self, ob, event):
        """ 
        Event filter to for searchLine events.
        """
        str(event)
        pass
        #print event
        #if event.type() == qt.QEvent.FocusIn:
            #print "CLICK!"




    def onEvent(self, eventKey, callback):
        """
        Adds a callback for a given event.  
        Callbacks are strored internally as a dictionary of arrays.
        
        @param event: The event descriptor for the callbacks stored.  Refer
        to AnimatedCollapsible.EVENT_TYPES for the list.
        @type event: string
        
        @param callback: The callback function to enlist.
        @type callback: function
        
        @raise: Error if 'event' argument is not a valid event type.
        """
        if not eventKey in self.EVENT_TYPES:
            raise Exception("AnimatedCollapsible (onEvent): invalid event type '%s'"%(eventKey))
        self.__eventCallbacks[eventKey].append(callback)
                    

        

    def clearEvents(self, eventKey = None):
        """
        Clears the event callbacks associated with the 'eventKey' argument.  
        If 'eventKey' is not specified, clears all of the event callbacks.
        
        @param eventKey: The event key to clear.
        @type eventKey: string
        """
        
        if not eventKey:
            for key in self.EVENT_TYPES:
                self.__eventCallbacks[key] = []
            return
        if not eventKey in self.EVENT_TYPES:
            raise Exception("AnimatedCollapsible (clearEvent): invalid event type '%s'"%(eventKey))
        else:
            self.__eventCallbacks[eventKey] = []




    def __runCallbacks(self, eventKey, *args):
        """
        @param eventKey: The event key to clear.
        @type eventKey: string
        """
        if not eventKey in self.EVENT_TYPES:
            raise Exception("AnimatedCollapsible (runCallbacks): invalid event type '%s'"%(eventKey))
        else:
            for callback in self.__eventCallbacks[eventKey]:
                if args:
                    callback(*args)
                else:
                    callback()

        

    
    def isExpanded(self):
        """
        @return: Whether the collapsible is expanded or not.
        @rtype: boolean
        """
        return self.toggled

        


    def setContents(self, widget):
        """ 
        Similar to the 'setWidget' function
        of a QWidget: sets the internal contents
        of the collapsible.
        """
        self.__contents = [widget]
        layout = qt.QHBoxLayout()
        layout.addWidget(widget)
        layout.setContentsMargins(0,0,0,0)
        self.frame.setLayout(layout)




    def getContents(self):
        """ 
        """
        return self.__contents
        



    def setEasingCurve(self, easingCurve):
        """
        Sets the animation easing curve.

        @param easingCurve: The easing curve to set.
        @type easingCurve: qt.QEasingCurve
        """
        self.__easingCurve = easingCurve




    def setCollapsedHeight(self, height):
        """
        Sets the collapsed height.

        @param height: The height to set.
        @type height: number
        """
        self.collapsedHeight = height




    def setMaxExpandedHeight(self, height, applyImmediately = False):
        """ 
        
        
        @param height: The height to set.
        @type height: number

        @param applyImmediately: The whether to apply the height changes immediately using the 
            'ctk.CollapsibleButton.setMaximumHeight' function.  This usually is needed only
            when the collapsible is in the 'expanded' state.
        @type applyImmediately: boolean
        """
        self.maxExpandedHeight = height
        if applyImmediately:
            self.setMaximumHeight(height)


        

    def setMinExpandedHeight(self, height, applyImmediately = False):
        """ 
        As stated.

        @param height: The height to set.
        @type height: number

        @param applyImmediately: The whether to apply the height changes immediately using the 
            'ctk.CollapsibleButton.setMinimumHeight' function.  This usually is needed only
            when the collapsible is in the 'expanded' state.
        @type applyImmediately: boolean
        """
        self.minExpandedHeight = height
        if applyImmediately:
            self.setMinimumHeight(height)

            
        
        
    def setChecked(self, toggled, animDuration = None):
        """ 
        Constructs an executes an animation for the widget
        once the title button is toggled.
        """

        #---------------- 
        # We need to set the button state in case
        # this method is programatically called.
        #----------------         
        self.toggleButton.setChecked(toggled)


        
        #---------------- 
        # Track whether collapsible was toggled.
        #---------------- 
        self.toggled = toggled


        
        #---------------- 
        # Define the animation duration.
        #----------------        
        if not animDuration: 
            animDuration = self.animDuration


            
        #---------------- 
        # Clear animation
        #---------------- 
        self.animations.clear()



        #---------------- 
        # For safety, set the width of
        # the widget to '100%'
        #----------------   
        self.setStyleSheet('width: 100%')


        
        #---------------- 
        # Modify button text to match the toggled
        # state (down arrow or right arrow) 
        #----------------       
        self.__modifyToggleButton(toggled)	


        
        #----------------
        # Make the animation object
        #----------------
        anim = qt.QPropertyAnimation(self, 'size')


        
        #----------------
        # Set the duration
        #----------------
        anim.setDuration(animDuration)	


        
        #----------------
        # Set the easing curve
        #----------------
        anim.setEasingCurve(self.__easingCurve)


        
        

        #----------------
        # Set the start/end values depending on
        # the toggle state.
        #----------------
        if self.toggled:

            self.__runCallbacks('expandStart')


            #
            # Establish the 'toggled'/expanded animation sizes.
            #	            
            startSize = qt.QSize(self.geometry.width(), self.collapsedHeight)
            endSize = qt.QSize(self.geometry.width(), self.maxExpandedHeight)  
            self.setMaximumHeight(self.collapsedHeight)
            self.setMinimumHeight(self.collapsedHeight)
  


        else:

            self.__runCallbacks('collapseStart')


            #
            # Establish the 'untoggled'/collapsed animation sizes.
            #	
            startHeight = self.geometry.height()

            #
            # Save original stretch height
            #
            self.setMaximumHeight(startHeight)

            
            startSize = qt.QSize(self.geometry.width(), startHeight)
            endSize = qt.QSize(self.geometry.width(), self.collapsedHeight)  
            self.setMaximumHeight(startHeight)
            self.setMinimumHeight(startHeight)

            #
            # Hide the internal contents for better
            # visual clarity.
            #
            self.__hideContents()
            


        #---------------- 
        # Set the start/end animation values.
        #----------------            
        anim.setStartValue(startSize)
        anim.setEndValue(endSize)            


        
        #---------------- 
        # Set callback during animation.
        #----------------
        anim.valueChanged.connect(self.__onAnimate)



        #---------------- 
        # Connect the 'finished()' signal of the animation
        # to the finished callback...
        #----------------
        anim.connect('finished()', self.__onAnimEnd)


        
        #---------------- 
        # Add main animation to queue and  
        # start animation.
        #----------------       
        self.animations.addAnimation(anim)
        self.animations.start()




    def setSizeGripVisible(self, visible):
        """ 
        Sets the size grip in the bottom-right
        corner of the screen visible or hidden.
        """
        if visible:
            self.sizeGrip.show()
        else:
            self.sizeGrip.hide()



        
    def setAnimLength(self, duration):
        """ 
        As stated.
        """
        self.animDuration = duration;



    def suspendAnim(self, suspend = False):
        """ 
        Suspends the animation length by converting
        the duration to 0, saving the previous state.
        When the user sets the 'suspend' argument to 
        'False' then the previous animation state is 
        restored.
        """
        if suspend:
            self.originalAnimDuration = self.animDuration
            self.animDuration = 0    
        else:
            self.animDuration = self.originalAnimDuration




    def __modifyToggleButton(self, toggled):
        """ 
        Modifies the arrow character of the button
        title to match the 'toggled' state and also
        sets its text to 'self.title.'
        """
        arrowChr = self.downArrowChar if toggled else self.rightArrowChar
        self.toggleButton.setText(arrowChr + '  ' + self.title)
        self.toggleButton.setFixedHeight(17)
        self.toggleButton.setMinimumWidth(10)
        self.toggleButton.setMaximumWidth(110)




    def __onAnimate(self, variant):
        """ 
        Function during main animation
        sequence.  Calls the user-inputted 'onAnimate'
        callback.
        """
        self.__runCallbacks('animate')
        self.setFixedHeight(variant.height())

            


        
    def __onAnimEnd(self):
        """ 
        Callback function when the animation
        finishes.  Also calls the user-inputted
        'onExpand' callback or 'onCollapse' callbacks
        depending on the toggle state of the widget.
        """

        #---------------- 
        # Call the animate function one last time.
        #---------------- 
        self.__onAnimate(qt.QSize(self.geometry.width(), self.geometry.height()))


        
        #---------------- 
        # If the widget is in a 'toggled' state.
        #---------------- 
        if self.toggled:
            
            #
            # Set its height to either 'stretchHeight'
            # or 'expandedHeight.  For an explanation of 'stretchHeight'
            # see it's declaration in the __init__ function.
            #
            self.setMaximumHeight(self.maxExpandedHeight)
                
            self.setMinimumHeight(self.minExpandedHeight)
                
            #
            # Show the internal contents
            #
            self.__showContents()

            #
            # Run the the 'onExpand' callback.
            #
            self.__runCallbacks('expanded')
            self.__runCallbacks('expandEnd')

                

        #---------------- 
        # Otherwise if it is 'collapsed'
        #---------------- 
        else:
                        
            #
            # Set the height to 'self.collapsedHeight'.
            #
            self.setFixedHeight(self.collapsedHeight)
            
            #
            # Run callbacks
            #
            self.__runCallbacks('collapsed')
            self.__runCallbacks('collapseEnd')


    def __hideContents(self):
        """ 
        As stated.
        """
        if self.__contents:
            for contentsWidget in self.__contents:
                contentsWidget.hide()



            
    def __showContents(self):
        """ 
        As stated.
        """
        if self.__contents:
            for contentsWidget in self.__contents:
                contentsWidget.show()
