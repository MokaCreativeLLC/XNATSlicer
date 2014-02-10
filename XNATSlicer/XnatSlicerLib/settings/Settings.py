# application
from __main__ import qt, slicer

# external
from MokaUtils import *

# module
from XnatSlicerGlobals import *

        

class Settings(qt.QScrollArea):
    """ 
    Settings is a parent class for the various Setting types 
    for the module.
    """

    SECTION_SPACING = 5
    EVENT_TYPES = [
        'UPDATEUI',
        'SETTINGS_FILE_MODIFIED'
    ]



    def __init__(self, SettingsFile, title = None):
        """ 
        @param SettingsFile: The SettingsFile to associate with.
        @type SettingsFile: SettingsFile

        @param title: The optional title of the setting.  (Utilizes 
            the class name otherwise).
        @type title: str
        """

        super(Settings, self).__init__(self)


        #--------------------
        # title
        #--------------------
        if not title:
            title = self.__class__.__name__.replace('Settings_', '');
        self.title = title
        

        #--------------------
        # Events
        #--------------------
        self.EVENT_TYPES = list(set(Settings.EVENT_TYPES + self.EVENT_TYPES))
        self.Events = MokaUtils.Events(self.EVENT_TYPES)
        #MokaUtils.debug.lf(self.__class__.__name__, self.EVENT_TYPES)


        #--------------------
        # 'private' vars
        #--------------------
        self.__xnatHosts = []
        self.__currXnatHost = None
        self.__SettingsFile = SettingsFile


        #--------------------
        # 'protected' / public vars
        #--------------------
        self.sectionLabels = []
        self.syncCallbacks_ToFile = {}
        self.syncCallbacks_FileTo = {}
        self.DEFAULTS = {}


        #--------------------
        # further inits...
        #--------------------
        self.__initUI()
        self.setup()
        self.updateUI()




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
            raise Exception('\'xnatHosts\' argument '+
                            'must be a list of strings.')
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





    def __initUI(self):
        """
        As stated.
        """

        #--------------------
        # Stylesheet.
        #--------------------
        self.setObjectName('xnatSetting')
        self.setStyleSheet('#xnatSetting {height: 100%; width: 100%; ' +  
                           'border: 1px solid gray;}')


        #--------------------
        # NOTE: This fixes a scaling error that occurs with the scroll 
        # bar.  When we inherit from a QWidget.  
        #--------------------
        self.verticalScrollBar().setStyleSheet('width: 15px')


        #--------------------
        # The label
        #--------------------
        self.label = qt.QLabel(self.title)


        #--------------------
        # Layout for widget frame.
        #--------------------
        self.__resetFrame()


        #--------------------
        # Layout for widget frame.
        #--------------------
        self.masterLayout = qt.QVBoxLayout()
        self.masterLayout.setContentsMargins(10,10,10,10)




    def __resetFrame(self):
        """
        As stated.  Necessary because frames do not dynamically 
        update when their contents updates.
        """
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(1)
        self.frame = qt.QFrame()
        self.frame.setObjectName('settingFrame')
        self.frame.setStyleSheet("#settingFrame {background: white;}")
        self.frame.setMinimumWidth(600)
        self.frame.setFixedWidth(600)
        if hasattr(self, 'masterLayout'):
            self.frame.setLayout(self.masterLayout)
        slicer.app.processEvents()




    def setup(self):
        """
        Inherited by subclass, if needed.
        """
        pass




    def __storeSyncCallback(self, callbackDict, section, callback):
        """
        Stores a sync callback.

        @param callbackDict:
        @type callbackDict:

        @param section
        @type section:

        @param callback:
        @type callback:
        """
        if not section in callbackDict:
            callbackDict[section] = []
        callbackDict[section].append(callback)




    def addSyncCallback_ToFile(self, section, method):
        """
        """
        self.__storeSyncCallback(self.syncCallbacks_ToFile, section, method)




    def addSyncCallback_FileTo(self, section, method):
        """
        """
        self.__storeSyncCallback(self.syncCallbacks_FileTo, section, method)




        
    def syncToFile(self):
        """
        """
        #MokaUtils.debug.lf('Begin SyncToFile!', self.__class__.__name__)
        if not self.currXnatHost:
            #MokaUtils.debug.lf('No host!', self.__class__.__name__)
            return

        if hasattr(self, 'DEFAULTS'):
            self.applyDefaultsIfNeeded()

        for syncType, methods in self.syncCallbacks_ToFile.iteritems():
            for method in methods:
                method()

        slicer.app.processEvents()
        #self.updateUI()                                                       



    @property
    def storageTagPrefix(self):
        """
        """
        return (self.__class__.__name__ + '_').replace('Settings_', '')


                

    def getStorageTag(self, *suffixArgs):
        """
        """
        returnStr = self.storageTagPrefix
        for suffixArg in suffixArgs:
            suffixArg = MokaUtils.string.removeNonAlphanumeric(suffixArg)
            suffixArg = '_'.join(MokaUtils.string.splitAtCaps(suffixArg))
            returnStr += '_' + suffixArg
            returnStr = returnStr.replace(' ', '')
        return returnStr.lower()




    def getCustomStorageTag(self, *suffixArgs):
        """
        """
        returnStr = self.getStorageTag('custom', *suffixArgs)
        #MokaUtils.debug.lf(returnStr)
        return returnStr
                                    


    def writeSettingIfEmpty(self, settingTag, tagValue):
        """
        """
        if not self.SettingsFile.tagExists(self.currXnatHost, settingTag):
            tagDict = {settingTag : tagValue}
            self.SettingsFile.setSetting(self.currXnatHost, tagDict)
            #MokaUtils.debug.lf('Writing: ', tagDict, \
            #                   " to SetingsFile in host: ", \
            #                   self.currXnatHost) 


    
    def applyDefaultsIfNeeded(self):
        """ 
        """
            
        #MokaUtils.debug.lf('Apply defaults!\n\n')
        for key, keyValue in self.DEFAULTS.iteritems():
            #MokaUtils.debug.lf(key, keyValue)
            if not isinstance(keyValue, dict):
                self.writeSettingIfEmpty(key, keyValue)
            else:
                for subKey, subKeyValue in keyValue.iteritems():
                    self.writeSettingIfEmpty(subKey, subKeyValue)
                
 


    def updateUI(self):
        """ 
        A necessary function that's for
        wrapping up every XnatSetting __init__ function.
        It makes the layout's contents display correctly.
        
        NOTE: Ideally this would not have to happen, but updating
        the widget's frame dynamically (after it has been 
        applied via setWidget) and then adding widgets, doesn't
        update at all.
        """
                
        self.Events.runEventCallbacks('UPDATEUI')
        self.__resetFrame()
        self.setWidget(self.frame)




    def addSection(self, title, qWidgetOrLayout = None):
        """ 
        Adds a section to the Settings by
        creating a label, the title of which is specified
        in the 'title' argument, and then adding the 
        relevant qWidgetOrLayout to the masterLayout.

        @param title: The title of the section.
        @type title: str

        @param qWidgetOrLayout: The qt Object to add to the section.
        @param qWidgetOrLayout: qt.QWidget or qt.QLayout
        """

        #--------------------
        # Add label title and spacing.
        #--------------------        
        self.sectionLabels.append(qt.QLabel('<b>%s</b>'%(title), self))
        self.masterLayout.addWidget(self.sectionLabels[-1])
        self.masterLayout.addSpacing(self.SECTION_SPACING)


        #--------------------
        # Add the qWidgetOrLayout.
        #-------------------- 
        if qWidgetOrLayout:
            if 'layout' in qWidgetOrLayout.className().lower():
                self.masterLayout.addLayout(qWidgetOrLayout)
            else:
                self.masterLayout.addWidget(qWidgetOrLayout)


        self.updateUI()


        
        
    def addSpacing(self, spacing = 10):
        """ Adds a spacing element to the
            masterLayout.
        """
        self.masterLayout.addSpacing(spacing) 
        



