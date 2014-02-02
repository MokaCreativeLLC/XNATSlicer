# external
from Xnat import *
from MokaUtils import *

# module
from XnatSlicerGlobals import *
from MetadataEditorSet import *



    
class MetadataEditorSetting(object):
    """ 
    
    """
  
    DEFAULT_METADATA = Xnat.metadata.DEFAULT_TAGS
    EVENT_TYPES = ['UPDATE', 'ITEMCLICKED']
            

    def createMetadataEditorSets(self, 
                                 section, 
                                 itemType, 
                                 editVisible = True,
                                 customEditVisible = False):
        """ 
        Creates any number of metadata managers as 
        specified by *args, which are string keys that 
        are used to identify the metadata managers in
        the MetadataEditorSets dictionary.
        """

        self.EVENT_TYPES = list(set(MetadataEditorSetting.EVENT_TYPES + 
                                    self.EVENT_TYPES))

        if not hasattr(self, 'MetadataEditorSets'):
            self.MetadataEditorSets = {}


        #--------------------
        # The editor 
        #--------------------
        ccSection = section #MokaUtils.string.toCamelCase(section)
        editorSet = MetadataEditorSet(self.SettingsFile)    
        editorSet.setEditButtonsVisible(editVisible)
        editorSet.setCustomEditVisible(customEditVisible)
        editorSet.setItemType(itemType)


        #--------------------
        # Callbacks
        #--------------------
        self.__setEditorCallbacks(editorSet)
        self.Events.onEvent('UPDATEUI', self.__updateUI)


        #--------------------
        # Defaults
        #--------------------
        self.__constructDefaults(ccSection)


        #--------------------
        # Add sync methods
        #--------------------
        self.addSyncCallback_ToFile(ccSection, self.__syncToFile)
        self.addSyncCallback_FileTo(ccSection, self.__syncFileTo)


        #--------------------
        # Add to UI and store
        #--------------------
        self.MetadataEditorSets[ccSection] = editorSet
        self.addSection(section, 
                        self.MetadataEditorSets[ccSection])

    
        self.__linkedSettings = None
        self.__closeCollapsibles()

        


        
    def __closeCollapsibles(self):
        """
        """
        for key, _set in self.MetadataEditorSets.iteritems():
            if _set.collapsibles:
                for key in _set.collapsibles:
                    _set.collapsibles[key].show() 
                    _set.collapsibles[key].setChecked(False) 

        


    def __updateUI(self):
        """
        Deprecated?
        """
        return






    def __addCustomItem(self, editor):
        """
        """

        editorSection, storageTag, customStorageTag, \
            savedItems, customItems = self.getStoredMetadata(editor) 
        lineText = editor.lineEdit.text
        if not lineText in savedItems and not lineText in customItems:
            tagDict = {customStorageTag : \
                       [lineText] + customItems}
            self.SettingsFile.setSetting(self.currXnatHost, tagDict)
            editor.lineEdit.clear()
            MokaUtils.debug.lf()
            self.Events.runEventCallbacks('SETTINGS_FILE_MODIFIED', 
                                          self.__class__.__name__)

        else:
            tagType = 'Custom' if lineText in customItems else 'Default'
            msg = "'%s' already exists in %s tags."%(lineText, tagType)
            editor.takenBox = qt.QMessageBox(1, "Add Metadata", msg)
            editor.takenBox.show()
            editor.lineEdit.selectAll()






    def __removeCustomItem(self, editor):
        """
        """

        editorSection, storageTag, customStorageTag, \
            savedItems, customItems = self.getStoredMetadata(editor) 

        currItem = editor.listWidget.currentItem()
        currItemText = currItem.text().lower().strip()

        #--------------------
        # Remove the selected item  
        #--------------------        
        updatedMetadataItems = []
        for item in customItems:
            if item.lower().strip() == currItemText:
                editor.listWidget.removeItemWidget(
                    editor.listWidget.currentItem())
            else:
                updatedMetadataItems.append(item)

        #--------------------
        # Write items.
        #--------------------  
        tagDict = {customStorageTag : \
                   updatedMetadataItems}
        self.SettingsFile.setSetting(self.currXnatHost, tagDict)

        #print "NEED TO PROPAGATE CUSTOM METADATA REMOVE!"
        #MokaUtils.debug.lf()
        self.Events.runEventCallbacks('SETTINGS_FILE_MODIFIED', 
                                      self.__class__.__name__)
        #self.MODULE.SettingsWindow.updateSettingWidgets()


        
        


    def __setEditorCallbacks(self, editorSet):
        """
        """        
        for editor in editorSet.allEditors:
            editor.Events.onEvent('UPDATE', self.__syncToFile)
            editor.Events.onEvent('ITEMCLICKED', self.__syncFileTo)

            if 'Custom' in editor.__class__.__name__:
                editor.Events.onEvent('ADDCLICKED', self.__addCustomItem)
                editor.Events.onEvent('REMOVECLICKED', self.__removeCustomItem)




    def __constructDefaults(self, section = 'metadata'):
        """
        @param section: The section for referring to the default.
        @type section: str
        """
        #MokaUtils.debug.lf("\n\n ", savedItems)
        section = MokaUtils.string.toCamelCase(section)
        if hasattr(self, 'DEFAULT_METADATA'):
            self.DEFAULTS[section] = {}
            for level, item in self.DEFAULT_METADATA.iteritems():
                if level == 'LABELS':
                    continue
                self.DEFAULTS[section]\
                    [self.getStorageTag(section, level)] = item




    def getStoredMetadata(self, editorOrEditorSection, level = None, 
                          itemsOnly = False):
        """
        """
        if isinstance(editorOrEditorSection, MetadataEditor):
            editor = editorOrEditorSection
            editorSection = self.__findMetadataEditorSection(editor)
            xnatLevel = editor.xnatLevel
            assert editorSection, 'Unable to locate provided editor!'


        elif isinstance(editorOrEditorSection, basestring):
            assert (editorOrEditorSection in self.MetadataEditorSets), \
                "Invalid editorSection: %s, %s"%(editorOrEditorSection, 
                                             self.MetadataEditorSets)
            assert level, "Invalid level: %s.  Options are: %s"%(level)
            editorSection = editorOrEditorSection
            xnatLevel = level

        
        storageTag = self.getStorageTag(editorSection, xnatLevel)
        customStorageTag = \
                    self.getCustomStorageTag(editorSection, xnatLevel)
        savedItems = self.SettingsFile.getSetting(self.currXnatHost, 
                    self.getStorageTag(editorSection, xnatLevel))
        customItems = self.SettingsFile.getSetting(self.currXnatHost, 
                    self.getCustomStorageTag(editorSection, xnatLevel))

        
        #MokaUtils.debug.lf(self.__class__.__name__)
        #MokaUtils.debug.lf("editorSection: ", editorSection)
        #MokaUtils.debug.lf("storageTag: ", storageTag)
        #MokaUtils.debug.lf("customStorageTag: ", customStorageTag)
        #MokaUtils.debug.lf("Saved items: ", savedItems)
        #MokaUtils.debug.lf("Custom items: ", customItems, '\n\n')

        if itemsOnly:
            return list(set(savedItems) | set(customItems))

        return editorSection, storageTag, customStorageTag, \
               savedItems,customItems




    def __findMetadataEditorSection(self, editor):
        """
        """
        for section, editorSet in self.MetadataEditorSets.iteritems():
            if editorSet.hasEditor(editor):
                return section
        




    def linkToSetting(self, localSetKey, Setting, linkedSetKey):
        """
        """
        assert isinstance(Setting, MetadataEditorSetting), "linkToSetting " + \
            "setting must inherit from MetadataEditorSetting!"
        if not self.__linkedSettings:
            self.__linkedSettings = {}
        self.__linkedSettings[localSetKey] = {'setting': Setting, \
                                              'setkey': linkedSetKey}

        #print \n\n
        #MokaUtils.debug.lf(self.__class__.__name__)
        #MokaUtils.debug.lf(self.__linkedSettings)




    def __syncFileTo(self, editor):
        """
        """

        editorSection, storageTag, customStorageTag, \
        savedItems, customItems = self.getStoredMetadata(editor) 
        checkedItems = [box.text() for box in editor.getCheckedBoxesOnly()]

        if 'Custom' in editor.__class__.__name__:
            tagDict = {customStorageTag : checkedItems}
        else:
            tagDict = {storageTag : checkedItems}

        self.SettingsFile.setSetting(self.currXnatHost, tagDict)


        #MokaUtils.debug.lf("CHECKED ITEMS", checkedItems)
        self.Events.runEventCallbacks('SETTINGS_FILE_MODIFIED', 
                                      self.__class__.__name__)
        




    def __syncToFile(self, editor = None):
        """
        """

        #--------------------
        # If no editor, run on all editors.
        #--------------------
        if not editor:
            for key, editorSet in self.MetadataEditorSets.iteritems():
                editorSet.loopEditors(self.__syncToFile)
            return


        #--------------------
        # Get the stored items based on the 
        # generated tag
        #--------------------
        editorSection, storageTag, customStorageTag, \
        savedItems, customItems = self.getStoredMetadata(editor) 
 
        #MokaUtils.debug.lf('SyncToFile!', self.__class__.__name__, 
        #                   savedItems, customItems, '\n\n')
        #--------------------
        # Sync the checked boxes
        #--------------------
        editor.setCheckedOnly(savedItems)


        #--------------------
        # Sync the custom lists.
        #--------------------
        if 'Custom' in editor.__class__.__name__:
            if self.__linkedSettings:
                _Setting = self.__linkedSettings[editorSection]['setting']
                _setKey = self.__linkedSettings[editorSection]['setkey']
                _editor = _Setting.MetadataEditorSets[_setKey]. \
                              customMetadataEditors[editor.xnatLevel]
                _editorSection, _storageTag, _customStorageTag, \
                _savedItems, _customItems = _Setting.getStoredMetadata(_editor)
                
                editor.listItemsOnly(_customItems, 'checkbox')
                
                #
                # To accommodate the case of deleting a checked
                # custom item.
                #
                updatedCustomItems = []
                for item in customItems:
                    if item in _customItems:
                       updatedCustomItems.append(item)
        
                tagDict = {customStorageTag : updatedCustomItems}
                self.SettingsFile.setSetting(self.currXnatHost, tagDict)       
                

                editor.setCheckedOnly(updatedCustomItems)
                #print "\n\n"
                #MokaUtils.debug.lf("Custom items retreived: ", _customItems ,
                #                   "stored", customItems,
                #                   self.__class__.__name__, editor.xnatLevel)
            else:
                editor.listItemsOnly(customItems)

        slicer.app.processEvents()

