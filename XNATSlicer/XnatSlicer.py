import imp, os, inspect, sys, slicer

#
# Widget path needs to be globally recognized by Python.
# Appending to global path.
#
MODULE_PATH = os.path.normpath(os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe()))[0])))
#
# Inlcude testing folders.
#
sys.path.append(os.path.join(MODULE_PATH, 'Testing'))
#
# Include lib folder.
#
LIB_PATH = os.path.join(MODULE_PATH, "XnatSlicerLib")
sys.path.append(LIB_PATH)
#
# Include ui folder.
#
sys.path.append(os.path.join(LIB_PATH, 'ui'))
#
# Include ui-settings folder.
#
sys.path.append(os.path.join(LIB_PATH, 'ui/settings-widgets'))
#
# Include ui-custom-widgets folder.
#
sys.path.append(os.path.join(LIB_PATH, 'ui/custom-qt-widgets'))
#
# Include utils folder.
#
sys.path.append(os.path.join(LIB_PATH, 'utils'))
#
# Include io folder.
#
sys.path.append(os.path.join(LIB_PATH, 'io'))


from XnatGlobals import *
from XnatFileInfo import *
from XnatFolderMaker import *
from XnatLoadWorkflow import *
from XnatUtils import *
from XnatScenePackager import *
from XnatSessionManager import *
from XnatTimer import *
from XnatSettingsFile import *
from XnatTreeView import *
from XnatSearchBar import *
from XnatIo import *
from XnatLoginMenu import *
from XnatButtons import *
from XnatViewer import *
from XnatView import *
from XnatPopup import *
from XnatDicomLoadWorkflow import *
from XnatSceneLoadWorkflow import *
from XnatFileLoadWorkflow import *
from XnatAnalyzeLoadWorkflow import *
from XnatSlicerTest import *
from XnatError import *
from XnatSettings import *
from XnatHostSettings import *
from XnatTreeViewSettings import *
from XnatMetadataSettings import *
from XnatDetailsSettings import *
from XnatNodeDetails import *
from XnatMetadataManager import *
from AnimatedCollapsible import *
from VariableItemListWidget import *




comment = """
XnatSlicer.py contains the central classes for managing 
all of the XnatSlicer functions and abilities.  XnatSlicer.py
is the point where the module talks to Slicer, arranges the gui, and
registers it to the Slicer modules list.  It is where all of the 
XnatSlicerLib classes and methods converge.

TODO:
"""




class XnatSlicer:
  """ The class that ultimately registers the module
      with Slicer.
  """
  
  def __init__(self, parent):
      """ Init function.
      """

      #--------------------------------
      # Registers the title and relevant information
      # parameters to Slicer
      #--------------------------------
      parent.title = "XNATSlicer"
      parent.categories = ["XNATSlicer"]
      parent.dependencies = []
      parent.contributors = ["Sunil Kumar (Moka Creative, LLC), Dan Marcus (WashU-St. Louis), Steve Pieper (Isomics)"] 
      parent.helpText = """ The XNATSlicer 1.0"""
      parent.acknowledgementText = """Sunil Kumar for the Neuroinformatics Research Group - sunilk@mokacreativellc.com""" 
      self.parent = parent


      
      #--------------------------------
      # Add this test to the SelfTest module's list for discovery when the module
      # is created.  Since this module may be discovered before SelfTests itself,
      # create the list if it doesn't already exist.
      #--------------------------------
      try:
          slicer.selfTests
      except AttributeError:
          slicer.selfTests = {}
          slicer.selfTests['XnatSlicer'] = self.runTest
          
      def runTest(self):
          tester = XnatSlicerTest()
          tester.runTest()



          

class XnatSlicerWidget:
    """  The class that manages all of the XNATSlicer-specific
         libraries.
    """
    
    def __init__(self, parent = None):
        """ Init function.
        """
        if not parent:
            self.parent = slicer.qMRMLWidget()
            self.parent.setLayout(qt.QVBoxLayout())
            self.parent.setMRMLScene(slicer.mrmlScene)
        else:
            self.parent = parent
        if not parent:
            self.setup()
            self.parent.show()



        #--------------------------------
        # Init Xnat GLOBALS
        #--------------------------------
        self.GLOBALS = XnatGlobals() 


        
        #--------------------------------
        # Init Xnat Utils
        #--------------------------------
        self.utils = XnatUtils(self)   


        #--------------------------------
        # Xnat IO
        #--------------------------------
        self.XnatIo = XnatIo()

        

        #--------------------------------
        # Construct all needed directories
        # if not there...
        #--------------------------------
        self.utils.constructNecessaryModuleDirectories()

        
        
        #--------------------------------
        # Set the layout
        #--------------------------------
        self.layout = self.parent.layout()

        
        
        #--------------------------------
        # Collapse the 'Data Probe' button.
        #--------------------------------
        dataProbeButton = slicer.util.findChildren(text='Data Probe')[0]
        dataProbeButton.setChecked(False)


        
        #--------------------------------
        # Xnat settingsFile
        #--------------------------------
        self.XnatSettingsFile = XnatSettingsFile(slicer.qMRMLWidget(), self.GLOBALS.LOCAL_URIS['settings'], self)


        
        #--------------------------------
        # Login Menu
        #--------------------------------
        self.XnatLoginMenu = XnatLoginMenu(parent = self.parent, MODULE = self)
        self.XnatLoginMenu.loadDefaultHost()   
        def showHost(*arg):
            self.XnatSettingsWindow.showWindow(self.XnatHostSettings.tabTitle)
        self.XnatLoginMenu.setOnManageHostsButtonClicked(showHost)


        
        #--------------------------------
        # Xnat xnatSettingsWindow
        #--------------------------------        
        self.XnatSettingsWindow = XnatSettingsWindow(parent = None, MODULE = self)
        
        #
        # Add XnatHostSettings (communicates to XnatSettings)
        # to xnatSettingsWindow
        #
        self.XnatHostSettings = XnatHostSettings('XNAT Hosts', self)
        self.XnatSettingsWindow.addSetting(self.XnatHostSettings.title, widget = self.XnatHostSettings)
        
        #
        # Add XnatMetadataSettings (communicates to XnatTreeView)
        # to xnatSettingsWindow
        #
        self.XnatMetadataSettings = XnatMetadataSettings('XNAT Metadata', self)
        self.XnatSettingsWindow.addSetting(self.XnatMetadataSettings.title, widget = self.XnatMetadataSettings)
        
        #
        # Add XnatTreeViewSettings (communicates to XnatTreeView)
        # to xnatSettingsWindow
        #
        self.XnatTreeViewSettings = XnatTreeViewSettings('Tree View Settings', self)
        self.XnatSettingsWindow.addSetting(self.XnatTreeViewSettings.title, widget = self.XnatTreeViewSettings)
        
        #
        # Add XnatDetailsSettings (communicates to XnatTreeView)
        # to xnatSettingsWindow
        #
        self.XnatDetailsSettings = XnatDetailsSettings('Details Settings', self)
        self.XnatSettingsWindow.addSetting(self.XnatDetailsSettings.title, widget = self.XnatDetailsSettings)



        #--------------------------------
        # SearchBar
        #--------------------------------
        self.XnatSearchBar = XnatSearchBar(MODULE = self)

        
      
        #--------------------------------
        # Viewer
        #--------------------------------
        self.XnatView = XnatTreeView(MODULE = self)  

        
        
        #--------------------------------
        # Node Details
        #--------------------------------
        self.XnatNodeDetails = XnatNodeDetails(MODULE = self) 
        
        #
        # Link a node click to populate XnatNodeDetails.
        #
        self.XnatView.addNodeChangedCallback(self.XnatNodeDetails.setXnatNodeText)


        
        #--------------------------------
        # Xnat Buttons
        #--------------------------------
        self.XnatButtons = XnatButtons(self.parent, MODULE=self)  
        
        
        
        #--------------------------------
        # Popups
        #--------------------------------
        self.XnatDownloadPopup = XnatDownloadPopup(MODULE = self)
        #self.uploadPopup = XnatDownloadPopup(MODULE = self)

                
        
        #--------------------------------
        # LoadWorkflows
        #--------------------------------
        self.XnatSceneLoadWorkflow = XnatSceneLoadWorkflow(self)
        self.XnatFileLoadWorkflow = XnatFileLoadWorkflow(self)
        self.XnatDicomLoadWorkflow = XnatDicomLoadWorkflow(self)
        self.XnatAnalyzeLoadWorkflow = XnatAnalyzeLoadWorkflow(self)
        



        #--------------------------------
        # Xnat Folder Maker
        #--------------------------------
        self.XnatFolderMaker = XnatFolderMaker(self.parent, self)



        
        #--------------------------------
        # Init gui
        #--------------------------------
        self.initGUI()
        
        
        
        #--------------------------------
        # Listeners/observers from gui
        #--------------------------------
        slicer.mrmlScene.AddObserver(slicer.mrmlScene.EndCloseEvent, self.sceneClosedListener)
        slicer.mrmlScene.AddObserver(slicer.mrmlScene.EndImportEvent, self.sceneImportedListener)



        #--------------------------------
        # Tester
        #--------------------------------
        self.tester = XnatSlicerTest(self)



        #--------------------------------
        # Clean the temp dir
        #--------------------------------
        self.cleanCacheDir(200)

      

      
    def onReload(self, moduleName = "XnatSlicer"):
      """ Generic reload method for any scripted module.
          ModuleWizard will subsitute correct default moduleName.
          Provided by Slicer.
      """
      
      widgetName = moduleName + "Widget"

      

      #--------------------------------
      # Reload the source code:
      # - set source file path
      # - load the module to the global space
      #--------------------------------
      filePath = eval('slicer.modules.%s.path' % moduleName.lower())
      p = os.path.dirname(filePath)
      if not sys.path.__contains__(p):
        sys.path.insert(0,p)
      fp = open(filePath, "r")
      globals()[moduleName] = imp.load_module(
          moduleName, fp, filePath, ('.py', 'r', imp.PY_SOURCE))
      fp.close()


      
      #--------------------------------
      # Rebuild the widget:
      # - find and hide the existing widget
      # - create a new widget in the existing parent
      #--------------------------------
      parent = slicer.util.findChildren(name='%s Reload' % moduleName)[0].parent()
      for child in parent.children():
        try:
          child.hide()
        except AttributeError:
          pass


        
      #--------------------------------  
      # Remove spacer items.
      #--------------------------------
      item = parent.layout().itemAt(0)
      while item:
        parent.layout().removeItem(item)
        item = parent.layout().itemAt(0)


        
      #--------------------------------
      # Create new widget inside existing parent.
      #--------------------------------
      globals()[widgetName.lower()] = eval('globals()["%s"].%s(parent)' % (moduleName, widgetName))
      globals()[widgetName.lower()].setup()



      
    def onReloadAndTest(self, moduleName = "ScriptedExample"):
        """ Also provided by Slicer.  Runs the tests on the
            reload.
        """
        try:
            self.onReload()
            evalString = 'globals()["%s"].%sTest()' % (moduleName, moduleName)
            tester = eval(evalString)
            tester.runTest()
        
        except Exception, e:
            import traceback
            traceback.print_exc()
            qt.QMessageBox.warning(slicer.util.mainWindow(), 
                                   "Reload and Test", 'Exception!\n\n' + str(e) + "\n\nSee Python Console for Stack Trace")
    


        
    def sceneClosedListener(self, caller, event):
        """Actions for when the user closes a scene from the GUI.
        """ 
        #print("'Close Scene' called. Resetting Xnat session data.")    
        self.XnatView.sessionManager.clearCurrentSession()  



        
    def sceneImportedListener(self, caller, event): 
        """Actions for when the user imports a scene from the GUI.
           NOTE: This technically is not used, as the user must refer to files from an 
           XNAT location. Nonetheless, it is implemented in the event that it is needed.
        """
        if self.XnatView.lastButtonClicked == None:
            #print("'Import Data' called. Resetting Xnat session data.")
            self.XnatView.sessionManager.clearCurrentSession() 
    

            
            
    def initGUI(self):  
        """ As stated.
        """
                
        #--------------------------------
        # Make Main Collapsible Button
        #--------------------------------
        mainCollapsibleButton = ctk.ctkCollapsibleButton()
        mainCollapsibleButton.text = "XNATSlicer"


        
        #--------------------------------
        # Make Collapsible boxes: login, tools, viewer, details.
        #--------------------------------
        self.collapsibles = {}
        self.collapsibles['login'] = AnimatedCollapsible(self.parent, 'Login', 60, 60)
        self.collapsibles['tools'] = AnimatedCollapsible(self.parent, 'Tools', 60, 60)
        self.collapsibles['viewer'] = AnimatedCollapsible(self.parent, 'Viewer')
        self.collapsibles['viewer'].setSizeGripVisible(True)
        self.collapsibles['details'] = AnimatedCollapsible(self.parent, 'Details')
        
        #
        # Set collapsibles onAnimate callback to Update XNATSlicer's 
        # layout when they are animating.
        #
        def onAnimatedCollapsibleAnimate():
            self.mainLayout.update()
        for key, collapsible in self.collapsibles.iteritems():
            collapsible.setOnAnimate(onAnimatedCollapsibleAnimate)


            
        #--------------------------------
        # DEFINE: Main layout
        #--------------------------------        
        self.mainLayout = qt.QVBoxLayout()


        
        #--------------------------------
        # Set LOGIN Group Box.
        #--------------------------------    
        self.collapsibles['login'].setWidget(self.XnatLoginMenu)


        
        #--------------------------------
        # Set VIEWER Group Box.
        #--------------------------------
        self.XnatViewer = XnatViewer(self)
        self.collapsibles['viewer'].setWidget(self.XnatViewer)



        #--------------------------------
        # Set DETAILS Group Box.
        #-------------------------------- 
        #
        # Add detauls layout to group box.
        #
        self.collapsibles['details'].setWidget(self.XnatNodeDetails)


        

        
        #--------------------------------
        # Set TOOLS Group Box.
        #-------------------------------- 
        #
        # Add tools layout to group box.
        #
        self.collapsibles['tools'].setWidget(self.XnatButtons.toolsWidget) 

 

        
        #--------------------------------
        # Add collapsibles to main layout.
        #--------------------------------
        keys = ['login', 'viewer', 'details', 'tools']
        for key in keys:
            self.mainLayout.addWidget(self.collapsibles[key])


        
        #--------------------------------
        # Add main layout to main collapsible button.
        #-------------------------------- 
        self.mainLayout.addStretch(3000)
        mainCollapsibleButton.setLayout(self.mainLayout)
        

        
        #--------------------------------
        # Closes the collapsible group boxes except
        # the login.  We set the animLength of each
        # collapsible to 0 to avoid awkard load animations
        #--------------------------------
        for key, collapsible in self.collapsibles.iteritems():
            collapsible.suspendAnimationDuration(True)
            if key == 'login':
                for child in collapsible.ContentsWidgets:
                    child.hide()
                collapsible.setChecked(True)
            else:
                collapsible.setChecked(False)
                collapsible.setEnabled(False)
            collapsible.suspendAnimationDuration(False)
            

            
        #--------------------------------
        # Add main Collapsible button to layout registered
        # to Slicer.
        #--------------------------------
        self.layout.addWidget(mainCollapsibleButton)
        
        #
        # NOTE: Showing the collapsibles beforehhand creates flickering 
        # when opening Slicer, hence we show them only
        # after they have been added to the layout.
        #
        for key, collapsible in self.collapsibles.iteritems():
            collapsible.show()
        
        

        #--------------------------------
        # Event Connectors
        #-------------------------------- 
        #
        # Login Menu event.
        #
        self.XnatLoginMenu.loginButton.connect('clicked()', self.onLoginButtonClicked)
        #
        # Button event.
        #
        self.XnatButtons.buttons['io']['load'].connect('clicked()', self.onLoadClicked)
        self.XnatButtons.buttons['io']['save'].connect('clicked()', self.onSaveClicked)
        self.XnatButtons.buttons['io']['delete'].connect('clicked()', self.onDeleteClicked)
        self.XnatButtons.buttons['io']['addProj'].connect('clicked()', self.XnatFolderMaker.show)
        self.XnatButtons.buttons['settings']['settings'].connect('clicked()', self.XnatSettingsWindow.showWindow)
        #
        # Sort Button event.
        #
        for key, button in self.XnatTreeViewSettings.buttons['sort'].iteritems():
            button.connect('clicked()', self.onFilterButtonClicked)
        #
        # Test button event.
        #
        # NOTE: Disabling this for now.
        # TODO: Implement a testing suite.
        #
        #self.XnatButtons.buttons['io']['test'].connect('clicked(boolean*)', self.onTestClicked)
        self.XnatButtons.buttons['io']['test'].setEnabled(False)
        #
        # Search Bar event.
        #
        self.XnatSearchBar.connect(self.XnatView.searchEntered)



        
    def cleanCacheDir(self, maxSize):
        """ Empties contents of the temp directory based upon maxSize
        """
        import math
        folder = self.GLOBALS.CACHE_URI
        folder_size = 0


        
        #--------------------------------
        # Loop through files to get file sizes.
        #--------------------------------
        for (path, dirs, files) in os.walk(folder):
          for file in files:
            folder_size += os.path.getsize(os.path.join(path, file))
        #print ("XnatSlicer Data Folder = %0.1f MB" % (folder_size/(1024*1024.0)))


        
        #--------------------------------
        # If the folder size exceeds limit, remove contents.
        #--------------------------------
        folder_size = math.ceil(folder_size/(1024*1024.0))
        if folder_size > maxSize:
            self.utils.removeFilesInDir(folder)    




                
    def beginXnat(self):
        """ Opens the view class linked to the Xnat REST API.
            Runs a test for the relevant libraries (i.e. SSL)
            before allowing the login process to begin.
        """

        #--------------------
        # Can SSL be imported?
        #--------------------
        print("XnatSlicer Module: Checking if SSL is installed...")
        try:      
            import ssl
            httplib.HTTPSConnection
            print("XnatSlicer Module: SSL is installed!")

            

        #--------------------
        # If not, kick back OS error
        #--------------------
        except Exception, e:
            strs = "XnatSlicer cannot operate on this system as SSL is not installed."
            #print("XnatSlicer Module: %s"%(strs))
            qt.QMessageBox.warning(slicer.util.mainWindow(), "No SSL", "%s"%(strs))
            return
                

        
        #--------------------
        # Init XnatIo.
        #--------------------
        self.XnatIo.setup(MODULE = self, 
                                    host = self.XnatSettingsFile.getAddress(self.XnatLoginMenu.hostDropdown.currentText), 
                                    user = self.XnatLoginMenu.usernameLine.text, password=self.XnatLoginMenu.passwordLine.text)

        

        #--------------------
        # Begin communicator
        #--------------------
        self.XnatView.begin()





    def calculateCollapsibleTargetHeights(self, state):
        """ Determines the target heights for the various
            collapsibles to animate to by quickly expanding
            the collapsibles, recording their geometries, then
            quickly compressing them.  The user should not 
            notice this calculation.
        """

        #--------------------
        # Expand the collapsibles 
        # if the login to XNAT was successful.
        #--------------------
        targetHeights = {}
        if state == 'onLoginSuccessful':
            
            targetGeometries = {}

            #
            # Expand the collapsibles except 'login',
            # supending the animation length.
            #
            for key, collapsible in self.collapsibles.iteritems():
                collapsible.suspendAnimationDuration(True)
                if key != 'login':
                    collapsible.setChecked(True)
                else:
                    collapsible.setChecked(False)

            #
            # Record the geometries of the collapsibles.
            #
            for key, collapsible in self.collapsibles.iteritems():
                targetGeometries[key] = collapsible.geometry


            #
            # Compress the collapsibles, but expand 'login'.
            # Make sure animations are suspendedn.
            #
            for key, collapsible in self.collapsibles.iteritems():
                collapsible.hide()
                if key != 'login':
                    collapsible.setChecked(False)
                else:
                    collapsible.setChecked(True)
                collapsible.setEnabled(True)
                collapsible.suspendAnimationDuration(False)
                collapsible.show()
            

            #
            # Get the total height of the XnatSlicer
            # widget.
            #
            widgetLength = 0           
            for key, geom in targetGeometries.iteritems():
                #aprint "GO", key, geom, geom.top()
                targetHeights[key] = geom.height()
                if geom.top() > widgetLength:
                    widgetLength = geom.top()


            #
            # Modify some of the target geometries:
            # we want the Viewer collapsible to be 
            # slightly larger than the Details collapsible.
            #        
            viewerDifference = 75
            targetHeights['details'] = widgetLength - targetGeometries['details'].top() - viewerDifference
            targetHeights['viewer'] = targetGeometries['viewer'].height() + viewerDifference


            return targetHeights


            

    def onLoginSuccessful(self):
        """ Enables the relevant collapsible 
            group boxes. 
        """

        heights = self.calculateCollapsibleTargetHeights('onLoginSuccessful')

        
        #--------------------
        # Creat animation chain callbacks.
        #-------------------- 
        def expandViewer():
            self.collapsibles[ 'viewer' ].setMaxHeight(heights['viewer'])
            self.collapsibles[ 'viewer' ].setChecked(True)
            self.collapsibles[ 'viewer' ].setEnabled(True)

        
        def expandDetails():
            self.collapsibles[ 'details' ].setMaxHeight(heights['details'])
            self.collapsibles[ 'details' ].setChecked(True)
            self.collapsibles[ 'details' ].setEnabled(True)
       

        
        def expandTools():
            self.collapsibles[ 'tools' ].setChecked(True)
            self.collapsibles[ 'tools' ].setEnabled(True)

      
            
        #--------------------
        # Callback: Clear the animation Chain when
        # the animation chain is finished.
        #--------------------
        def clearChain(): 
            for key, collapsible in self.collapsibles.iteritems():
                collapsible.setOnExpand(None)
                collapsible.setOnCollapse(None)
                if key != 'tools' and key != 'login':
                    #collapsible.setMaxHeight(1000)
                    collapsible.setFixedHeight(heights[key])
                    collapsible.setStretchHeight(1000)
                   


        #--------------------
        # Apply the callbacks to the collapsibles.
        #--------------------               
        self.collapsibles['viewer'].setOnExpand(expandDetails)
        self.collapsibles['details'].setOnExpand(expandTools)                
        self.collapsibles['tools'].setOnExpand(clearChain)
        self.collapsibles['login'].setOnCollapse(expandViewer)

            
        
        #--------------------
        # Fire off the animation chain,
        # first by compressing the 'Login'
        # collapsible.
        #--------------------              
        self.collapsibles['login'].setChecked(False)


        
        
    def onLoginFailed(self):
        """ Disable the relevant collapsible 
            group boxes. 
        """

        #--------------------
        # Minimize and enable the others.
        # Create an animation chain.
        #-------------------- 
        def collapseViewer():
            self.collapsibles[ 'viewer' ].setChecked(False)
            self.collapsibles[ 'viewer' ].setEnabled(False)
        self.collapsibles['login'].setOnExpand(collapseViewer)

        
        def collapseDetails():
            self.collapsibles[ 'details' ].setChecked(False)
            self.collapsibles[ 'details' ].setEnabled(False)
        self.collapsibles['viewer'].setOnCollapse(collapseDetails)

        
        def collapseTools():
            self.collapsibles[ 'tools' ].setChecked(False)
            self.collapsibles[ 'tools' ].setEnabled(False)
        self.collapsibles['details'].setOnCollapse(collapseTools)

        

        #--------------------
        # Clear the animation Chain when finished
        #--------------------
        def clearChain(): 
            for key, collapsible in self.collapsibles.iteritems():
                collapsible.setOnExpand(None)
                collapsible.setOnCollapse(None)
        self.collapsibles['tools'].setOnCollapse(clearChain)


        
        #--------------------
        # Minimize the login group box.
        # Fires off a chain of animations.
        #--------------------      
        self.collapsibles['login'].setChecked(True)


            

    def onLoginButtonClicked(self):
        """ Event function for when the login button is clicked.
            Steps below.
        """        

        #--------------------
        # Store the current username in settings
        #--------------------
        self.XnatSettingsFile.setCurrUsername(self.XnatLoginMenu.hostDropdown.currentText, self.XnatLoginMenu.usernameLine.text)

        
        #--------------------
        # Clear the current XnatView.
        #--------------------
        self.XnatView.clear()


        #--------------------
        # Derive the XNAT host URL by mapping the current item in the host
        # dropdown to its value pair in the settings.  
        #--------------------
        if self.XnatSettingsFile.getAddress(self.XnatLoginMenu.hostDropdown.currentText):
            self.currHostUrl = qt.QUrl(self.XnatSettingsFile.getAddress(self.XnatLoginMenu.hostDropdown.currentText))
            #
            # Call the 'beginXnat' function from the MODULE.
            #
            self.loggedIn = True
            self.beginXnat()
        else:
            print "%s The host '%s' doesn't appear to have a valid URL"%(self.utils.lf(), self.XnatLoginMenu.hostDropdown.currentText) 
            pass  




    def onDeleteClicked(self, button=None):
        """ Starts Delete workflow.
        """  

        xnatDeleteWorkflow = XnatDeleteWorkflow(self, self.XnatView.getCurrItemName())
        xnatDeleteWorkflow.beginWorkflow()



            
    def onSaveClicked(self):        
        """ Starts Save workflow.
        """     
        
        self.lastButtonClicked = "save" 
        self.XnatView.setEnabled(False)
        saver = XnatSaveWorkflow(self)
        saver.beginWorkflow()


        

    def onTestClicked(self):        
        """ Starts Save workflow.
        """     
        self.lastButtonClicked = "test" 
        self.XnatView.setEnabled(True)
        self.tester.runTest()


        
        
    def onLoadClicked(self):
        """ Starts Load workflow.
        """
        
        self.lastButtonClicked = "load"
        self.XnatView.setEnabled(False)
        loader = XnatLoadWorkflow(self)
        loader.beginWorkflow()






    def onFilterButtonClicked(self):
        """ As stated.  Handles the toggling of filter
            buttons relative to one another. O(4n).
        """


        try:
            self.XnatButtons.buttons['filter']
        except Exception, e:
            return
        #-----------------
        # Count down buttons
        #------------------
        checkedButtons = 0
        buttonLength = len(self.XnatButtons.buttons['filter'])
        for key in self.XnatButtons.buttons['filter']:
           currButton = self.XnatButtons.buttons['filter'][key]
           if currButton.isChecked():
               checkedButtons += 1

               
               
        #-----------------
        # If there are no down buttons, apply the ['all']
        # filter and return.
        #------------------
        if checkedButtons == 0:
            for key in self.XnatButtons.buttons['filter']:
                self.XnatButtons.buttons['filter'][key].setDown(False)
                self.XnatButtons.buttons['filter'][key].setChecked(False)
            self.currentlyToggledFilterButton = ''
            self.XnatView.loadProjects(['all'])
            return
 

        
        #-----------------
        # If a new button has been clicked
        # then set it as the self.currentlyToggledFilterButton. 
        #------------------
        for key in self.XnatButtons.buttons['filter']:
            currButton = self.XnatButtons.buttons['filter'][key]
            if currButton.isChecked() and self.currentlyToggledFilterButton != currButton:
                self.currentlyToggledFilterButton = currButton
                break

            
                
        #-----------------
        # Un-toggle previously toggled buttons.
        #-----------------
        for key in self.XnatButtons.buttons['filter']:
            currButton = self.XnatButtons.buttons['filter'][key]
            if currButton.isChecked() and self.currentlyToggledFilterButton != currButton:
                currButton.setDown(False)

                

        #-----------------
        # Apply method
        #------------------
        for key in self.XnatButtons.buttons['filter']:
            if self.currentlyToggledFilterButton == self.XnatButtons.buttons['filter'][key]:
                self.XnatView.loadProjects([self.currentlyToggledFilterButton.text.lower()])
