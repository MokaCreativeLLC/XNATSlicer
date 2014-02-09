# application
from __main__ import qt

# external
from MokaUtils import *



    
class CheckBoxSetting(object):
    """ 
    Class for Settings widgets that aim to make use of CheckBoxes.
    This class manages events and SettingsFile syncing in a generic way.
    """

    def getCheckBoxStorageTag(self, checkBoxKey):
        """
        Returns a string of a constructed storage tag key.

        @param checkBoxKey:  The key to construct the tag from.
        @type checkBoxKey: str
        
        @return: The check box storage hey.
        @rtype: str
        """
        return self.__class__.__name__ + '_' + \
            self.CHECKBOXES[checkBoxKey]['tag']



    def __dummy(self, *args):
        """
        Dummy function for checkboxes in case their state is queried another 
        way.
        """
        pass



    def createCheckBoxes(self):
        """
        As stated.
        """
        assert hasattr(self, 'CHECKBOXES'), \
                "%s needs a CHECKBOXES variable"%(self.__class__.__name__)

        for key, val in self.CHECKBOXES.iteritems():
            storeTag = self.getCheckBoxStorageTag(key)
            self.EVENT_TYPES.append(self.CHECKBOXES[key]['event'])
            self.CHECKBOXES[key]['widget'] = qt.QCheckBox(val['desc'])
            self.DEFAULTS[storeTag] = val['checked']
            self.CHECKBOXES[key]['widget'].connect('clicked(bool)',
                                                   self.__syncFileTo)
            self.Events.onEvent(self.CHECKBOXES[key]['event'], self.__dummy)
            self.addSyncCallback_ToFile(storeTag,  self.__syncToFile)
            self.addSyncCallback_FileTo(storeTag, self.__syncFileTo)
            
            
        #
        # Add to widget
        #
        self.masterLayout.addWidget(self.CHECKBOXES[key]['widget'])
        self.masterLayout.addStretch()




    def __syncToFile(self):
        """
        Method specific to syncing the Setting's checkboxes to the SettingsFile.
        """
        #MokaUtils.debug.lf()
        for key, val in self.CHECKBOXES.iteritems():
            storeTag = self.getCheckBoxStorageTag(key)
            setting = self.SettingsFile.getSetting(self.currXnatHost, storeTag)
            checked = 2 if 'True' in setting[0] else 0
            #MokaUtils.debug.lf(storeTag, setting, checked)
            self.CHECKBOXES[key]['widget'].setCheckState(checked)
            try:
                self.Events.runEventCallbacks(self.CHECKBOXES[key]['event'], 
                                              checked)
            except Exception, e:
                #MokaUtils.debug.lf(str(e))
                pass
        self.updateUI()
    


    def __syncFileTo(self, checked):
        """
        Method specific to syncing the SettingsFile to the Setting's checkboxes.
        Also the callback function for when a checkbox is toogled.

        @param checked: The checked state of the CheckBox.
        @type checked: str
        """
        for key, val in self.CHECKBOXES.iteritems():
            storeTag = self.getCheckBoxStorageTag(key)
            self.SettingsFile.setSetting(self.currXnatHost, 
                    {storeTag: str(self.CHECKBOXES[key]['widget'].isChecked())})
            self.Events.runEventCallbacks(self.CHECKBOXES[key]['event'], 
                                          checked)
