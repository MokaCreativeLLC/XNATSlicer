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
        ccSection = MokaUtils.string.toCamelCase(section)
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
        self.addSyncMethod_ToFile(ccSection, self.__syncToFile)
        self.addSyncMethod_FileTo(ccSection, self.__syncFileTo)


        #--------------------
        # Add to UI and store
        #--------------------
        self.MetadataEditorSets[ccSection] = editorSet
        self.addSection(section, 
                        self.MetadataEditorSets[ccSection])






    def __updateUI(self):
        """

        Deprecated?
        """
        for key, manager in self.MetadataEditorSets.iteritems():
            if manager.collapsibles:
                for key in manager.collapsibles:
                    manager.collapsibles[key].show() 
                    manager.collapsibles[key].setChecked(False) 





    def __setEditorCallbacks(self, editorSet):
        """
        """        
        for editor in editorSet.allEditors:
            editor.Events.onEvent('UPDATE', \
                                  self.__syncToFile)
            editor.Events.onEvent('ITEMCLICKED', \
                                  self.__syncFileTo)




    def __syncFileTo(self, editor):
        """
        """

        editorSection, storageTag, customStorageTag, \
        savedItems, customItems = self.__getStoredItems(editor) 
        
        checkedItems = [box.text() for box in editor.getCheckedBoxesOnly()]

        MokaUtils.debug.lf("CHECKED ITEMS", checkedItems)

        tagDict = {storageTag : checkedItems}
        self.SettingsFile.setSetting(self.currXnatHost, tagDict)

                
        try:
            self.MODULE.View.refreshColumns()
        except Exception, e:
            print "\n\nNEED TO UPDATE VIEW COLUMNS!!!!!!!!"




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
                self.DEFAULTS[section][self.getStorageTag(section, level)] = \
                                                                           item



    def __getStoredItems(self, editor):
        """
        """
        editorSection = self.__findMetadataEditorSection(editor)
        if not editorSection:
            raise Exception('Unable to locate provided editor!')

        
        storageTag = self.getStorageTag(editorSection, editor.xnatLevel)
        customStorageTag = \
                    self.getCustomStorageTag(editorSection, editor.xnatLevel)

        savedItems = self.SettingsFile.getSetting(self.currXnatHost, 
                    self.getStorageTag(editorSection, editor.xnatLevel))

        customItems = self.SettingsFile.getSetting(self.currXnatHost, 
                    self.getCustomStorageTag(editorSection, editor.xnatLevel))

        
        MokaUtils.debug.lf("editorSection: ", editorSection)
        MokaUtils.debug.lf("storageTag: ", storageTag)
        MokaUtils.debug.lf("customStorageTag: ", customStorageTag)
        MokaUtils.debug.lf("Saved items: ", savedItems)
        MokaUtils.debug.lf("Custom items: ", customItems, '\n\n')

        return editorSection,storageTag,customStorageTag,savedItems,customItems




    def __findMetadataEditorSection(self, editor):
        """
        """
        for section, editorSet in self.MetadataEditorSets.iteritems():
            if editorSet.hasEditor(editor):
                return section
        



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
        savedItems, customItems = self.__getStoredItems(editor) 


        #--------------------
        # Sync the checked boxes
        #--------------------
        editor.setCheckedOnly(savedItems)


        #--------------------
        # Sync the custom lists.
        #--------------------
        if 'Custom' in editor.__class__.__name__:
            editor.listItemsOnly(customItems)

        slicer.app.processEvents()

