# external
from Xnat import *
from MokaUtils import *

# module
from MetadataEditorSet import *



    
class MetadataEditorSetting(object):
    """ 
    Class for Setting widgets that aim to make use of the MetadataEditor class.
    This class manages events SettingsFile syncing in a generic way.
    """
    DEFAULT_METADATA = Xnat.metadata.DEFAULT_TAGS
    EVENT_TYPES = ['UPDATE', 'ITEMCLICKED']
            

    def createMetadataEditorSets(self, 
                                 section, 
                                 itemType, 
                                 editVisible = True,
                                 customEditVisible = False):
        """ 
        Creates any number of metadata managers as specified by arguments.
        
        @param section: The section to categorize the editor.
        @type section: str

        @param itemType: The item type of the editor (checkboxes or labels).
        @type itemType: str

        @param editVisible: Whether the editing buttons are visible in the 
            editor.
        @type editVisible: bool

        @param customEditVisible: Whether the custom editing buttons are visible
            in the editor.
        @type customEditVisible: bool        
        """

        if not hasattr(self, 'MetadataEditorSets'):
            self.MetadataEditorSets = {}


        self.EVENT_TYPES = list(set(MetadataEditorSetting.EVENT_TYPES + 
                                    self.EVENT_TYPES))

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
        Closes all of the collabsible frames of the editor.
        """
        for key, _set in self.MetadataEditorSets.iteritems():
            if _set.collapsibles:
                for key in _set.collapsibles:
                    _set.collapsibles[key].show() 
                    _set.collapsibles[key].setChecked(False) 

        


    def __updateUI(self):
        """
        Placeholder.
        """
        return






    def __addCustomItem(self, editor):
        """
        Propagates the addtion of a custom item to the provided MetadataEditor
        in the argument.

        @param editor: The MetadataEditor to make the changes to.  
        @type editor: MetadataEditor
        """

        editorSection, storageTag, customStorageTag, \
            savedItems, customItems = self.getStoredMetadata(editor) 
        lineText = editor.lineEdit.text
        if not lineText in savedItems and not lineText in customItems:
            tagDict = {customStorageTag : \
                       [lineText] + customItems}
            self.SettingsFile.setSetting(self.currXnatHost, tagDict)
            editor.lineEdit.clear()
            #MokaUtils.debug.lf()
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
        Propagates the removal of a custom item to the provided MetadataEditor
        in the argument.

        @param editor: The MetadataEditor to make the changes to.  
        @type editor: MetadataEditor
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
        Applies event callbacks to the given MetadataEditorSet.

        @param editorSet: The MetadataEditorSet to make the changes to.  
        @type editorSet: MetadataEditorSet
        """        
        for editor in editorSet.allEditors:
            editor.Events.onEvent('UPDATE', self.__syncToFile)
            editor.Events.onEvent('ITEMCLICKED', self.__syncFileTo)

            if 'Custom' in editor.__class__.__name__:
                editor.Events.onEvent('ADDCLICKED', self.__addCustomItem)
                editor.Events.onEvent('REMOVECLICKED', self.__removeCustomItem)




    def __constructDefaults(self, section = 'metadata'):
        """
        Constructs the default settings for the widget.

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
        Gets the stored metadata from the given arguments.

        @param editorOrEditorSection: The metadata editor to derive the 
            XNAT level and section from OR the editor section string.
        @type editorOrEditorSection: MetadataEditor | str

        @param level:  The XNAT level of the section to refer to.
        @type level: str

        @param itemsOnly: Whether to return the stored items only (as opposed
           to the section, and other metadata surrounding the items).
        @type itemsOnly: bool

        @return: A tuple potentially containing the following (depending on the
            itemsOnly argument): 
            - The tag used to retrieve the metadata from the SettingsFile.
            - The custom storage tag used to retrieve the meadata from the 
            Settings file.
            - The saved non-custom metadata items in the SettingsFile.
            - The saved custom metadata items in the SettingsFile.
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
        Determines the 'section' of the provided metadata editor.

        @param editor: The MetadataEditor to find the section of.  
        @type editor: MetadataEditor
        """
        for section, editorSet in self.MetadataEditorSets.iteritems():
            if editorSet.hasEditor(editor):
                return section
        




    def linkToSetting(self, localSetKey, Setting, linkedSetKey):
        """
        Links the current setting to another setting (used for propagating
        custom metadata items into other editors) by storing it.

        @param localSetKey:  The key to associate the linked setting with.
        @type localSetKey: str

        @param Setting: The setting to link to.
        @type Setting: Setting

        @param linkedSetKey: The set within the linked setting to link to.
        @type linkedSetKey: str
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
        Syncs the provided editor to the SettingsFile.

        @param editor: The MetadataEditor to sync the SettingsFile to.  
        @type editor: MetadataEditor
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
        Syncso the SettingsFile to the provided editor.

        @param editor: The MetadataEditor to sync the SettingsFile to.  
        @type editor: MetadataEditor
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

