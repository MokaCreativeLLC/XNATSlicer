#-----------------------------------------------------------------------------
set(MODULE_NAME XNATSlicer)

#-----------------------------------------------------------------------------
set(MODULE_PYTHON_SCRIPTS
  XnatSlicer.py
  XnatSlicerLib/io/XnatAnalyzeLoadWorkflow.py
  XnatSlicerLib/io/XnatDeleteWorkflow.py
  XnatSlicerLib/io/XnatDicomLoadWorkflow.py
  XnatSlicerLib/io/XnatFileLoadWorkflow.py
  XnatSlicerLib/io/XnatIo.py
  XnatSlicerLib/io/XnatLoadWorkflow.py
  XnatSlicerLib/io/XnatSaveWorkflow.py
  XnatSlicerLib/io/XnatSceneLoadWorkflow.py
  XnatSlicerLib/ui/custom-qt-widgets/AnimatedCollapsible.py
  XnatSlicerLib/ui/custom-qt-widgets/FingerTabWidget.py
  XnatSlicerLib/ui/custom-qt-widgets/HoverButton.py
  XnatSlicerLib/ui/custom-qt-widgets/VariableItemListWidget.py
  XnatSlicerLib/ui/settings-widgets/XnatDetailsSettings.py
  XnatSlicerLib/ui/settings-widgets/XnatHostSettings.py
  XnatSlicerLib/ui/settings-widgets/XnatMetadataEditor.py
  XnatSlicerLib/ui/settings-widgets/XnatMetadataSettings.py
  XnatSlicerLib/ui/settings-widgets/XnatSettings.py
  XnatSlicerLib/ui/settings-widgets/XnatTreeViewSettings.py
  XnatSlicerLib/ui/XnatButtons.py
  XnatSlicerLib/ui/XnatFolderMaker.py
  XnatSlicerLib/ui/XnatLoginMenu.py
  XnatSlicerLib/ui/XnatMetadataManager.py
  XnatSlicerLib/ui/XnatNodeDetails.py
  XnatSlicerLib/ui/XnatSaveDialog.py
  XnatSlicerLib/ui/XnatSearchBar.py
  XnatSlicerLib/ui/XnatSettingsWindow.py
  XnatSlicerLib/ui/XnatTreeView.py
  XnatSlicerLib/ui/XnatView.py
  XnatSlicerLib/ui/XnatViewer.py
  XnatSlicerLib/utils/XnatError.py
  XnatSlicerLib/utils/XnatFileInfo.py
  XnatSlicerLib/utils/XnatGlobals.py
  XnatSlicerLib/utils/XnatMrmlParser.py
  XnatSlicerLib/utils/XnatPopup.py
  XnatSlicerLib/utils/XnatScenePackager.py
  XnatSlicerLib/utils/XnatSessionManager.py
  XnatSlicerLib/utils/XnatSettingsFile.py
  XnatSlicerLib/utils/XnatTimer.py
  XnatSlicerLib/utils/XnatUtils.py
  )

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
