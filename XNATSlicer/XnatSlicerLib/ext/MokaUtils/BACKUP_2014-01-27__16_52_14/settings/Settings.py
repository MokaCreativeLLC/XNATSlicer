# application
from __main__ import qt

# external
from Xnat import *
from MokaUtils import *

# module
from XnatSlicerGlobals import *
from AnimatedCollapsible import *
from VariableItemListWidget import *
from MetadataEditorSet import *


        
class Settings(qt.QScrollArea):
    """ 
    Settings is a parent class to the various 
    component settings that exist within the SettingsWindow: 
    Settings_View_Tree, Settings_Details, Settings_Metadata,
    HostSettings, etc.  It contains a number of generic functions
    for managing generic variables and creating generic interactors
    (especially Settings_Metadata objects).
    
    Settings inherits from qt.QScrollArea.  
    """


    EVENT_TYPES = [
        'FONTSIZECHANGED'
    ]


    def __init__(self, SettingsFile, title = None):
        """ Init function.
        """
                    


        #--------------------
        # Call parent init.
        #--------------------
        qt.QScrollArea.__init__(self)

     
        if not title:
            title = self.__class__.__name__.replace('Settings_', '');
        
        self.sectionSpacing = 5
        self.metadataToSetting = {}
        self.defaultSelectedMetadata = {}
        self.tabTitle = title
        self.sectionLabels = []


        
        #--------------------
        # Set stylesheet.
        #--------------------
        self.setObjectName('xnatSetting')
        self.setStyleSheet('#xnatSetting {height: 100%; width: 100%; border: 1px solid gray;}')


        
        #--------------------
        # NOTE: This fixes a scaling error that occurs with the scroll 
        # bar.  When we inherit from a QWidget.  
        #--------------------
        self.verticalScrollBar().setStyleSheet('width: 15px')


        
        #--------------------
        # The label
        #--------------------
        self.label = qt.QLabel(title)


        
        #--------------------
        # Layout for widget frame.
        #--------------------
        self.frame = qt.QFrame()
        self.frame.setObjectName('settingFrame')
        self.frame.setStyleSheet("#settingFrame {background: white;}")



        #--------------------
        # Layout for the entire widget.
        #--------------------
        self.masterLayout = qt.QVBoxLayout()
        self.masterLayout.setContentsMargins(10,10,10,10)



        #--------------------
        # Define the MetadataEditorSets dictionary.
        # Subclasses will then call on 'createMetadataEditorSets'
        # to add to this dictionary.
        #--------------------
        self.MetadataEditorSets = {}


        self.__SettingsFile = SettingsFile
        self.__xnatHosts = []
        self.__currXnatHost = ''
        
        self.Events = MokaUtils.Events(self.EVENT_TYPES)
        print "\n\nSETTINGS FILE INTERACTOR"
        print self.__class__.__name__
        print self.EVENT_TYPES



        self.setup()



    def setup(self):
        """
        """
        pass



    @property
    def xnatHosts(self):
        return self.__xnatHosts



    @xnatHosts.setter
    def xnatHosts(self, xnatHosts):
        """
        @param xnatHosts: The XNAT hosts to set.
        @type xnatHosts: list(str)
        """
        if not xnatHosts is list:
            raise Exception('\'xnatHosts\' argument must be a list of strings.')
        self.__xnatHosts = xnatHosts



    @property
    def currXnatHost(self):
        return self.__currXnatHost




    @currXnatHost.setter
    def currXnatHost(self, currXnatHost):
        """
        @param xnatHost: The XNAT hosts to set.
        @type xnatHost: str
        """
        if not isinstance(currXnatHost, basestring):
            raise Exception('\'xnatHost\' argument must be a string.')
        self.__currXnatHost = currXnatHost




    @property
    def SettingsFile(self):
        return self.__SettingsFile




        
    @property
    def title(self):
        """ The title of the XnatSetting.
        """
        return self.label.text
        


        
    def syncWithSettingsFile(self):
        """
        
        """
        pass
        



    def __syncEditorSetCheckBoxes(self, checkBoxes):
        #
        # Get the current host from the hostDropdown
        # as part of the login menu.
        #
        savedMetadataItems = self.SettingsFile.getSetting(self.currXnatHost, 
                                                          self.checkedLevelTag)
        #
        # Loop through the items and check accordingly.
        #
        for checkBox in checkBoxes:
            if chcekBox.text() in savedMetadataItems:
                checkBox.setCheckState(2) 



    def __setMetadataEditorCallbacks(self, _MetadataEditor):
        """
        """        
        for key, editorSet in self.MetadataEditorSets.iteritems():
            for level, editor in editorSet.customMetadataEditors.iteritems():
                editor.Events('UPDATE', self.__syncEditorSetCheckBoxes)
            for level, editor in editorSet.defaultMetadataEditors.iteritems():
                editor.Events('UPDATE', self.__syncEditorSetCheckBoxes)





    def createMetadataEditorSets(self, *args):
        """ 
        Creates any number of metadata managers as 
        specified by *args, which are string keys that 
        are used to identify the metadata managers in
        the MetadataEditorSets dictionary.
        """
        for arg in args:
            self.MetadataEditorSets[arg] = MetadataEditorSet(self.SettingsFile)

            #
            # This assigns the XnatSetting's class name (which will be 
            # a subclass of Settings) to the metadataCheckedTags,
            # which are ultimately stored in the SettingsFile.
            #
            self.metadataToSetting[arg] = self.__class__.__name__ + \
                                                 "_%s_"%(arg) 
            self.MetadataEditorSets[arg].setOnMetadataCheckedTag(
                self.metadataToSetting[arg])
            self.defaultSelectedMetadata[arg] = None




    
    def applyDefaultsIfNeeded(self, defaultsDict):
        """ 
        Per metadata manager that exists in every 
        XnatSetting, allows the arguments in *args to 
        specify the default contents and select
        states of the metadata within every XnatSetting.
        """
            
        #--------------------
        # Loop through all available XNAT hosts
        # and query the SettingsFile for metadata
        # objects that are defined there.
        #--------------------
        xnatHosts = list(self.SettingsFile.getHostsDict().keys())
        for xnatHost in xnatHosts:
            for xnatLevel in Xnat.path.DEFAULT_LEVELS:
                for key, tagItem in self.metadataToSetting.iteritems():

                    #
                    # Construct the metadatatag by 
                    # XNAT level (projects, subjects, etc...)
                    #
                    levelTag = tagItem + xnatLevel
                    savedMetadataItems = \
                        self.SettingsFile.getSetting(xnatHost, levelTag)

                    #
                    # If there are no 'savedMetadataItems', from
                    # set settings file (perLevel), go ahead and save the
                    # defaults as per 'defaultSelectedMetadata'
                    #
                    if len(savedMetadataItems) == 0:
                        if defaultsDict[key]:
                            defaultSelectedMetadata = \
                                defaultsDict[key][xnatLevel] 
                            tagDict = {levelTag : defaultSelectedMetadata}
                            self.SettingsFile.setSetting(xnatHost, tagDict)
                            


                        
        
        

    def complete(self):
        """ 
        A necessary function that's for
        wrapping up every XnatSetting __init__ function.
        It makes the layout's contents display correctly.
        
        NOTE: Ideally this would not have to happen, but updating
        the widget's frame dynamically (after it has been 
        applied via setWidget) and then adding widgets, doesn't
        update at all.
        """
                
        #--------------------
        # Manipulate collapsibles and set
        # the widget to the frame.
        #--------------------
        self.masterLayout.addStretch()
        self.frame.setLayout(self.masterLayout)
        for key, manager in self.MetadataEditorSets.iteritems():
            if manager.collapsibles:
                for key in manager.collapsibles:
                    manager.collapsibles[key].show() 
                    manager.collapsibles[key].setChecked(False) 
                    

        self.setWidget(self.frame)

        




    def addSection(self, title, qobject):
        """ Adds a section to the Settings by
            creating a label, the title of which is specified
            in the 'title' argument, and then adding the 
            relevant qobject to the masterLayout.
        """

        #--------------------
        # Add label title and spacing.
        #--------------------        
        self.sectionLabels.append(qt.QLabel('<b>%s</b>'%(title), self))
        self.masterLayout.addWidget(self.sectionLabels[-1])
        self.masterLayout.addSpacing(self.sectionSpacing)


        #--------------------
        # Add the qobject.
        #-------------------- 
        if 'layout' in qobject.className().lower():
            self.masterLayout.addLayout(qobject)
        else:
            self.masterLayout.addWidget(qobject)


        
        
    def addSpacing(self, spacing = 10):
        """ Adds a spacing element to the
            masterLayout.
        """
        self.masterLayout.addSpacing(spacing) 
        



    def addFontSizeDropdown(self, title = "Font Size:" ):
        """ Adds a fontSize dropdown to the layout
            of the XnatSetting.  The subclass then
            needs to specify how to connect the events
            of the dropdown.
        """
        try:
            self.fontDropdowns.append(qt.QComboBox())
            self.fontDropdowns[-1].addItems([str(i) for i in range(8, 21)])
            self.fontDropdowns[-1].setFixedWidth(100)
            self.addSection(title, self.fontDropdowns[-1])



        #--------------------
        # If there's no 'fontDropdowns' variable
        # then we create one and call the function again.
        #--------------------
        except Exception, e:
            self.fontDropdowns = []
            self.addFontSizeDropdown(title)
