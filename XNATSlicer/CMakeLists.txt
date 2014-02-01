#-----------------------------------------------------------------------------
set(MODULE_NAME XNATSlicer)

#-----------------------------------------------------------------------------
set(MODULE_PYTHON_SCRIPTS
XnatSlicer.py
XnatSlicerLib/ext/MokaUtils/MokaUtils.py
XnatSlicerLib/ext/Xnat/Xnat.py
XnatSlicerLib/io/Loader.py
XnatSlicerLib/io/Loader_Analyze.py
XnatSlicerLib/io/Loader_Dicom.py
XnatSlicerLib/io/Loader_Mrb.py
XnatSlicerLib/io/Workflow_Delete.py
XnatSlicerLib/io/Workflow_Load.py
XnatSlicerLib/io/Workflow_Save.py
XnatSlicerLib/settings/FontSetting.py
XnatSlicerLib/settings/MetadataEditorSetting.py
XnatSlicerLib/settings/Settings.py
XnatSlicerLib/settings/Settings_Cache.py
XnatSlicerLib/settings/Settings_Details.py
XnatSlicerLib/settings/Settings_Hosts.py
XnatSlicerLib/settings/Settings_Metadata.py
XnatSlicerLib/settings/Settings_View.py
XnatSlicerLib/settings/SettingsFile.py
XnatSlicerLib/ui/Buttons.py
XnatSlicerLib/ui/FolderMaker.py
XnatSlicerLib/ui/LoginMenu.py
XnatSlicerLib/ui/MetadataEditor.py
XnatSlicerLib/ui/MetadataEditor_Custom.py
XnatSlicerLib/ui/MetadataEditor_Default.py
XnatSlicerLib/ui/MetadataEditorSet.py
XnatSlicerLib/ui/NodeDetails.py
XnatSlicerLib/ui/Popup.py
XnatSlicerLib/ui/SaveDialog.py
XnatSlicerLib/ui/SearchBar.py
XnatSlicerLib/ui/SettingsWindow.py
XnatSlicerLib/ui/View.py
XnatSlicerLib/ui/View_Tree.py
XnatSlicerLib/ui/Viewer.py
XnatSlicerLib/ui/custom-qt-widgets/AnimatedCollapsible.py
XnatSlicerLib/ui/custom-qt-widgets/FingerTabWidget.py
XnatSlicerLib/ui/custom-qt-widgets/HoverButton.py
XnatSlicerLib/ui/custom-qt-widgets/VariableItemListWidget.py
XnatSlicerLib/utils/Error.py
XnatSlicerLib/utils/FileInfo.py
XnatSlicerLib/utils/ScenePackager.py
XnatSlicerLib/utils/SessionManager.py
XnatSlicerLib/utils/SlicerUtils.py
XnatSlicerLib/utils/Timer.py
XnatSlicerLib/utils/XnatSlicerGlobals.py
XnatSlicerLib/utils/XnatSlicerUtils.py  )

set(MODULE_PYTHON_RESOURCES
  Resources/Icons/addproj.png
  Resources/Icons/delete.png
  Resources/Icons/eye.png
  Resources/Icons/gear.png
  Resources/Icons/load.png
  Resources/Icons/save.png
  Resources/Icons/search.png
  Resources/Icons/test.png
  Resources/Icons/wrench.png
  Resources/Icons/x.png
  Resources/Icons/XNATSlicer-MarketIcon.png
  Resources/Images/DeveloperDesc_MainPanel.png
  Resources/Images/UserDesc_MainPanel.png
  Resources/Images/XNATSlicer-MainIcon.png
  )

#-----------------------------------------------------------------------------
slicerMacroBuildScriptedModule(
  NAME ${MODULE_NAME}
  SCRIPTS "${MODULE_PYTHON_SCRIPTS}"
  RESOURCES "${MODULE_PYTHON_RESOURCES}"
  )

#-----------------------------------------------------------------------------
if(BUILD_TESTING)

  # this will regiester the unittest subclass in the main script
  # as a ctest (note that it is also usable as a runtime test).
  slicer_add_python_unittest(SCRIPT ${MODULE_NAME}.py)

  # additional build-time testing goes in here
  add_subdirectory(Testing)
endif()
