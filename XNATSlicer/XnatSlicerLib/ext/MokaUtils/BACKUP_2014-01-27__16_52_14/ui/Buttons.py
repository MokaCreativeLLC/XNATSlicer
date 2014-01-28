from __main__ import vtk, ctk, qt, slicer

import os

from Workflow_Load import *
from Workflow_Save import *
from Workflow_Delete import *

from XnatSlicerGlobals import *
from XnatSlicerUtils import *



comment = """
Buttons is the class that handles all of the buttons 
(and thier events)  to call on the various 
XnatWorkflows and filters.  This includes 'load/download', 
'delete', 'save/upload', 'create folder' and 'filter' UI elements.
It utilizes the UI file 'ButtonsUI' to generate the QT Widgets
that are used for the buttons.

TODO : 
"""




class Buttons(object):
    """ Creates buttons for the GUI and calls respective workflows.
    """
    
    def __init__(self, parent = None, MODULE = None):
        """  Create buttons
        """

        #--------------------
        # Public vars.
        #--------------------
        self.parent = parent
        self.MODULE = MODULE


        #--------------------
        # Buttons dictionary...for use by 
        # other classes.
        #--------------------
        self.buttons = {}


        
        #--------------------
        # IO Buttons (Save, Load, Delete, Add Project)
        #--------------------
        self.buttons['io'] = {}
        self.buttons['io'] = makeButtons_io(self)


        
        #--------------------
        # Filter Button onClicks
        #--------------------
        self.currentlyToggledFilterButton = None


            
        #--------------------
        # Testing button
        #--------------------
        self.setEnabled('test', True)



        #--------------------
        # Make Load / Save Button Layout.
        #--------------------
        self.loadSaveButtonLayout = qt.QVBoxLayout()
        self.loadSaveButtonLayout.addWidget(self.buttons['io']['load'])#, 2, 0)
        self.loadSaveButtonLayout.addWidget(self.buttons['io']['save'])#, 0, 0) 



        #--------------------
        # Make tool Button Layout.
        #--------------------
        self.toolsLayout = qt.QHBoxLayout()
        self.toolsLayout.addWidget(self.buttons['io']['delete'])
        self.toolsLayout.addSpacing(15)
        self.toolsLayout.addWidget(self.buttons['io']['addFolder'])
        self.toolsLayout.addSpacing(15)
        self.toolsLayout.addWidget(self.buttons['io']['test'])
        self.toolsLayout.addStretch()



        #--------------------
        # Add the settings button.
        #--------------------
        self.buttons['settings'] = {}
        self.buttons['settings']['settings'] = XnatSlicerUtils.generateButton(iconOrLabel = 'gear.png', 
                                                                                toolTip = "Open settings window.", 
                                                                                font = XnatSlicerGlobals.LABEL_FONT,
                                                                                size = XnatSlicerGlobals.BUTTON_SIZE_SMALL, 
                                                                                enabled = True)
        self.buttons['settings']['settings'].setToolTip('Open XNATSlicer settings.')
        self.toolsLayout.addWidget(self.buttons['settings']['settings'])


        self.toolsWidget = qt.QWidget()
        self.toolsWidget.setLayout(self.toolsLayout)
           



    def getButtonList(self, keys):
        """ Returns a list of buttons as provided by
            key.
        """
        buttonArr = []


        
        #--------------------
        # Convert 'keys' to list if it isn't one.
        #--------------------
        if isinstance(keys, basestring):
            keys = [keys]


            
        #--------------------
        # Loop through buttons, add to array
        #--------------------
        for groupName, buttonGroup in self.buttons.iteritems():
            for buttonId in buttonGroup:
                for key in keys:
                    if buttonId.lower() == key.lower():
                        buttonArr.append(buttonGroup[buttonId])


        return buttonArr
        
        
        
    def setEnabled(self, buttonKey = None, enabled = True):
        """ Sets a button enabled or disabled as part of QT
        """
        
        #--------------------
        # If button is specified, apply 'setEnambed' to 
        # it.
        #--------------------
        if buttonKey:
            self.buttons['io'][buttonKey].setEnabled(enabled)



        #--------------------
        # Otherwise apply 'setEnabled' to all buttons.
        #--------------------
        else:
            for k,b in self.buttons.iteritems():
                b.setEnabled(enabled)




            
#*************************************
#            
#  UI METHODS
#
#*************************************
            






def makeButtons_io(Buttons):
    """ Creates buttons specifically pertaining to XNAT IO.  This
        includes 'load', 'save', 'delete', 'addFolder' and 'test'.
    """
    buttons = {}
    buttons = {}


    buttons['load'] = XnatSlicerUtils.generateButton(iconOrLabel = 'load.png', 
                                               toolTip = "Load file, image folder or scene from Xnat to Slicer.", 
                                               font = XnatSlicerGlobals.LABEL_FONT,
                                               size = XnatSlicerGlobals.BUTTON_SIZE_SMALL, 
                                               enabled = False)
    buttons['load'].setToolTip('Load folder or file from XNAT instance.')
    
    
    
    buttons['save'] = XnatSlicerUtils.generateButton(iconOrLabel = 'save.png', 
                                               toolTip ="Upload current scene to Xnat.", 
                                               font = XnatSlicerGlobals.LABEL_FONT,
                                               size = XnatSlicerGlobals.BUTTON_SIZE_SMALL,
                                               enabled = False)
    buttons['save'].setToolTip('Save scene to XNAT instance.')
    
    
    
    buttons['delete'] = XnatSlicerUtils.generateButton(iconOrLabel = 'delete.png', 
                                                 toolTip = "Delete Xnat file or folder.", 
                                                 font = XnatSlicerGlobals.LABEL_FONT,
                                                 size = XnatSlicerGlobals.BUTTON_SIZE_SMALL, 
                                                 enabled = False)
    buttons['delete'].setToolTip('Delete file from XNAT instance.')
    
    
    
    buttons['addFolder'] = XnatSlicerUtils.generateButton(iconOrLabel = 'addproj.png', 
                                                  toolTip = "Add Project, Subject, or Experiment to Xnat.", 
                                                  font = XnatSlicerGlobals.LABEL_FONT,
                                                  size = XnatSlicerGlobals.BUTTON_SIZE_SMALL, 
                                                  enabled = False)
    buttons['addFolder'].setToolTip('Add project, subject or experiment to XNAT instance.')
    
    
    
    buttons['test'] = XnatSlicerUtils.generateButton(iconOrLabel = 'test.png', 
                                               toolTip = "Run XNATSlicer tests...", 
                                               font = XnatSlicerGlobals.LABEL_FONT,
                                               size = XnatSlicerGlobals.BUTTON_SIZE_SMALL, 
                                               enabled = False)
    buttons['test'].setToolTip('Run testing suite (COMING SOON).')
    
    
    return buttons




