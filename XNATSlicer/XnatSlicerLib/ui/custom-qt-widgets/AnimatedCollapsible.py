from __main__ import qt, ctk

import os
import sys
import shutil


from HoverButton import *




comment = """
AnimatedCollapsible is a subclass of ctk.ctkExpandableWidget. 
AnimatedCollapsible is designed around the premise of animating
when the user clicks on its title button.

Much like other QT widgets, the user can call 'setWidget'
to apply contents to the inside of the widget.  Other parameters, 
such as animation times and widgetsize, can also be set by the user.

TODO:        
"""




class AnimatedCollapsible(ctk.ctkExpandableWidget):
    """ Descriptor above.
    """
    
    def __init__(self, parent, title, maxHeight = 1000, minHeight = 60):
        """ Init function.
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
        self.minHeight = minHeight
        self.maxHeight = maxHeight



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
        self.animDuration = 300


        
        #-------------------- 
        # Set the size policy
        #--------------------
        self.setSizePolicy(qt.QSizePolicy.Ignored, qt.QSizePolicy.MinimumExpanding)


        
        #----------------
        # Set the animation's easing curve.  See:
        # http://harmattan-dev.nokia.com/docs/library/html/qt4/qeasingcurve.html
        # for more options.
        #----------------
        self.easingCurve = qt.QEasingCurve(2);


        
        #----------------
        # Set the minimum hieght
        #----------------
        self.setMinimumHeight(self.minHeight)
        

        
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
        self.toggleButton.setDefaultStyleSheet('#animatedCollapsibleToggleButton {border: 1px solid transparent; background-color: white; margin-left: 5px; text-align: left; padding-left: 5px;}')
        self.toggleButton.setHoverStyleSheet('#animatedCollapsibleToggleButton {border: 1px solid rgb(200,200,200); background-color: white; border-radius: 2px; margin-left: 5px; text-align: left; padding-left: 5px;}')
        self.configureButton(True)
     

        
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
        self.frame.setStyleSheet('#animateCollapsibleFrame {margin-top: 9px; border: 2px solid lightgray; padding-top: 5px; padding-left: 2px; padding-right: 2px; padding-bottom: 2px}')

        
        
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
        self.onAnimate = None
        self.onCollapse = None
        self.onExpand = None
        self.ContentsWidgets = []


        
        #----------------
        # Set the default states after creation.
        #----------------
        self.toggleButton.connect('toggled(bool)', self.setChecked)
        self.toggled = True



        #----------------
        # Set the stretch height.
        #
        # NOTE: This is different from the maximumHeight,
        # it's a target height that the user sets so that
        # the collapsible will stretch as far as self.stretchHeight
        # dictates once its expanded.  If we didn't have this 
        # variable, the the widget would have a sendentary height
        # within a layout, not stretching to the layout's
        # maximum extents.
        #
        #
        # TODO: Ideally this parameter would be more of a percentage
        # but setting stylesheet percentages is not possible, becase
        # we are manipulating the .maximumHeight' property of the widget 
        # during the animation.
        # Need to determine a more elegant way of of setting the 'stretch'
        # height to '100%' or equivalent.
        #----------------
        self.stretchHeight = None

            
        

    def suspendAnimationDuration(self, suspend):
        """ Suspends the animation length by converting
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


            
        
    def setAnimationDuration(self, duration):
        """ As stated.
        """
        self.animDuration = duration;
        



    def configureButton(self, toggled):
        """ Modifies the arrow character of the button
            title to match the 'toggled' state and also
            sets its text to 'self.title.'
        """
        arrowChr = self.downArrowChar if toggled else self.rightArrowChar
        self.toggleButton.setText(arrowChr + '  ' + self.title)
        self.toggleButton.setFixedHeight(17)
        self.toggleButton.setMinimumWidth(10)
        self.toggleButton.setMaximumWidth(110)

  

        

    def setWidget(self, widget):
        """ Similar to the 'setWidget' function
            of a QWidget: sets the internal contents
            of the collapsible.
        """
        self.ContentsWidgets = [widget]
        layout = qt.QHBoxLayout()
        layout.addWidget(widget)
        layout.setContentsMargins(0,0,0,0)
        self.frame.setLayout(layout)

        
            
        
    def setOnCollapse(self, callback):
        """ Sets the callback for AFTER widget
            is collapsed.
        """
        self.onCollapse = callback



        
    def setOnExpand(self, callback):
        """ Sets the callback for AFTER the 
            widget's expansion.
        """
        self.onExpand = callback



        
    def setOnAnimate(self, callback):
        """ Sets the callback for DURING the
            widget's animation.
        """
        self.onAnimate = callback
       
                


    def setSizeGripVisible(self, visible):
        """ Sets the size grip in the bottom-right
            corner of the screen visible or hidden.
        """
        if not visible:
            self.sizeGrip.hide()
        else:
            self.sizeGrip.show()


            

    def hideContentsWidgets(self):
        """ As stated.
        """
        if self.ContentsWidgets:
            for contentsWidget in self.ContentsWidgets:
                contentsWidget.hide()



            
    def showContentsWidgets(self):
        """ As stated.
        """
        if self.ContentsWidgets:
            for contentsWidget in self.ContentsWidgets:
                contentsWidget.show()
        


            
    def onAnimateMain(self, variant):
        """ Function during main animation
            sequence.  Calls the user-inputted 'onAnimate'
            callback.
        """
        if self.onAnimate:
            self.onAnimate()
            self.setFixedHeight(variant.height())

            


        
    def onAnimationFinished(self):
        """ Callback function when the animation
            finishes.  Also calls the user-inputted
            'onExpand' callback or 'onCollapse' callbacks
            depending on the toggle state of the widget.
        """

        #---------------- 
        # Call the animate function one last time.
        #---------------- 
        self.onAnimateMain(qt.QSize(self.geometry.width(), self.geometry.height()))


        
        #---------------- 
        # If the widget is in a 'toggled' state.
        #---------------- 
        if self.toggled:
            
            #
            # Set its height to either 'stretchHeight'
            # or 'maxHeight.  For an explanation of 'stretchHeight'
            # see it's declaration in the __init__ function.
            #
            if self.stretchHeight:
                self.setMaximumHeight(self.stretchHeight)
            else:
                self.setMaximumHeight(self.maxHeight)
                
            self.setMinimumHeight(self.minHeight)
                
            #
            # Show the internal contents
            #
            self.showContentsWidgets()

            #
            # Run the the 'onExpand' callback.
            #
            if self.onExpand:
                self.onExpand()

                

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
            if self.onCollapse:
                self.onCollapse()

    


    def setMaxHeight(self, height):
        """ As stated.
        """
        self.maxHeight = height


        

    def setMinHeight(self, height):
        """ As stated.
        """
        self.minHeight = height


        

    def setStretchHeight(self, height):
        """ As stated.  See declaration of 
            self.stretchHeight in the __init__
            function for explanation of that variable.
        """
        self.stretchHeight = height
        self.setMaximumHeight(height)
        

        
        
    def setChecked(self, toggled, animDuration = None):
        """ Constructs an executes an animation for the widget
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
        self.configureButton(toggled)	


        
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
        anim.setEasingCurve(self.easingCurve)


        
        #----------------
        # Set the start/end values depending on
        # the toggle state.
        #----------------
        if self.toggled:

            #
            # Establish the 'toggled'/expanded animation sizes.
            #	
            startSize = qt.QSize(self.geometry.width(), self.collapsedHeight)
            endSize = qt.QSize(self.geometry.width(), self.maxHeight)  
            self.setMaximumHeight(self.collapsedHeight)
            self.setMinimumHeight(self.collapsedHeight)


        else:

            #
            # Establish the 'untoggled'/collapsed animation sizes.
            #	
            startHeight = self.geometry.height()
            startSize = qt.QSize(self.geometry.width(), startHeight)
            endSize = qt.QSize(self.geometry.width(), self.collapsedHeight)  
            self.setMaximumHeight(startHeight)
            self.setMinimumHeight(startHeight)

            #
            # Hide the internal contents for better
            # visual clarity.
            #
            self.hideContentsWidgets()
            


        #---------------- 
        # Set the start/end animation values.
        #----------------            
        anim.setStartValue(startSize)
        anim.setEndValue(endSize)            


        
        #---------------- 
        # Set callback during animation.
        #----------------
        anim.valueChanged.connect(self.onAnimateMain)



        #---------------- 
        # Connect the 'finished()' signal of the animation
        # to the finished callback...
        #----------------
        anim.connect('finished()', self.onAnimationFinished)


        
        #---------------- 
        # Add main animation to queue and  
        # start animation.
        #----------------       
        self.animations.addAnimation(anim)
        self.animations.start()


        
        

