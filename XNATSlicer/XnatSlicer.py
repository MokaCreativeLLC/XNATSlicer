# python
import imp
import os
import inspect
import sys
import math
import copy
import httplib # to test for SSL installation
from collections import OrderedDict

# Acquire Module path.
MODULE_PATH = os.path.normpath(
  os.path.realpath(
    os.path.abspath(
      os.path.split(
        inspect.getfile( inspect.currentframe()))[0])))

# Add Lib Paths
LIB_PATH = os.path.join(MODULE_PATH, "XnatSlicerLib")
sys.path.append(LIB_PATH)
sys.path.append(os.path.join(MODULE_PATH, 'Testing'))
sys.path.append(os.path.join(LIB_PATH, 'ext/Xnat'))
sys.path.append(os.path.join(LIB_PATH, 'ext/MokaUtils'))
sys.path.append(os.path.join(LIB_PATH, 'ext/urllib3'))
sys.path.append(os.path.join(LIB_PATH, 'ui'))
sys.path.append(os.path.join(LIB_PATH, 'settings'))
sys.path.append(os.path.join(LIB_PATH, 'ui/custom-qt-widgets'))
sys.path.append(os.path.join(LIB_PATH, 'utils'))
sys.path.append(os.path.join(LIB_PATH, 'io'))

# application
import slicer

# external
from Xnat import *
from MokaUtils import *

# module - io
from Workflow_Delete import *
from Workflow_Save import *
from Workflow_Load import *

# module - utils
import XnatSlicerGlobals
from XnatSlicerUtils import *
from SettingsFile import *
from Timer import *
from Error import *

# module - ui
from Viewer import *
from View_Tree import *
from SearchBar import *
from LoginMenu import *
from Buttons import *
from NodeDetails import *
from AnimatedCollapsible import *

# module - settings
from FolderMaker import *
from Settings_Hosts import *
from Settings_Cache import *
from Settings_Metadata import *
from Settings_Details import *
from Settings_View import *



class XnatSlicer:
  """ 
  Interfaces with Slicer.
  This is not to be confused with the actual XnatSlicerWidget class
  which is below this one.
  """
  
  def __init__(self, parent):
      """ 
      @param parent: The parent widget to attach to.
      @type parent: qt.QWidget
      """

      #--------------------------------
      # Registers the title and relevant information
      # parameters to Slicer
      #--------------------------------
      parent.title = "XNATSlicer"
      parent.categories = ["XNATSlicer"]
      parent.dependencies = []
      parent.contributors = ["Sunil Kumar (Moka Creative, LLC), " + \
        "Dan Marcus (WashU-St. Louis), Steve Pieper (Isomics)"] 
      parent.helpText = """XNATSlicer 2.1"""
      parent.acknowledgementText = "Sunil Kumar for the Neuroinformatics " + \
        "Research Group at WashU-St.Louis (sunilk@mokacreativellc.com)"
      self.parent = parent

      #--------------------------------
      # Add this test to the SelfTest module's list for 
      # discovery when the module is created.
      # Since this module may be discovered before SelfTests itself,
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
    """  
    XnatSlicer.py contains the central classes for managing 
    all of the XnatSlicer functions and abilities.  XnatSlicer.py
    is the point where the module talks to Slicer, arranges the gui, and
    registers it to the Slicer modules list.  It is where all of the 
    XnatSlicerLib classes and methods converge.
    """

    COLLAPSIBLE_KEYS = [
      'login', 
      'viewer', 
      'details', 
      'tools'
    ]
    
    def __init__(self, parent = None):
        """ 
        Init function.
        @param parent: The parent widget to attach to.
        @type parent: qt.QWidget
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

        self.XnatIo = None 
        self.layout = self.parent.layout()

        XnatSlicerUtils.constructNecessaryModuleDirectories()

        self.__collapseDataProbe()
        self.__initComponents()
        self.__addObservers()



      
    def onReload(self, moduleName = "XnatSlicer"):
      """ 
      This is a generic reload method for any scripted module.
      ModuleWizard will subsitute correct default moduleName.
      Provided by Slicer.

      @param moduleName: 
      @type moduleName: string
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
      parent = slicer.util.findChildren(name='%s Reload' % moduleName)[0].\
               parent()
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
      globals()[widgetName.lower()] = eval('globals()["%s"].%s(parent)' % \
                                           (moduleName, widgetName))
      globals()[widgetName.lower()].setup()



      
    def onReloadAndTest(self, moduleName = "ScriptedExample"):
        """ 
        Also provided by Slicer.  Runs the tests on the
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
                            "Reload and Test", 'Exception!\n\n' + \
                            str(e) + "\n\nSee Python Console for Stack Trace")
    


    def __addObservers(self):
      """
      """
      slicer.mrmlScene.AddObserver(slicer.mrmlScene.EndCloseEvent, 
                                   self.__sceneClosedListener)



    def __initComponents(self):
      """
      """
      self.__initSettingsFile()
      self.__initSettings()
      self.__initLoginMenu()
      self.__initSearchBar()
      self.__initView()
      self.__initNodeDetails()
      self.__initButtons()
      self.__initFolderMaker()
      self.__initGui()
      self.__initTester()


        

    def __initView(self):
      """
      """
      self.View = View_Tree(self, self.Settings['VIEW'])  



    def __initSearchBar(self):
      """
      """
      self.SearchBar = SearchBar(MODULE = self)



    def __initSettingsFile(self):
      """
      """
      self.SettingsFile = SettingsFile(slicer.qMRMLWidget(), 
                    XnatSlicerGlobals.LOCAL_URIS['settings'], self)
      

    def __initNodeDetails(self):
      """
      """
      self.NodeDetails = NodeDetails(self.Settings['DETAILS'])
      self.__setNodeDetailsCallbacks()
        


    def __initButtons(self):
      """
      """
      self.Buttons = Buttons(self.parent, MODULE=self)  
        
        

    def __initFolderMaker(self):
      """
      """
      self.FolderMaker = FolderMaker(None, self.View)
      self.FolderMaker.Events.onEvent('folderAdded', self.__onFolderAdded)



    def __initTester(self):
      """
      """
      #self.tester = XnatSlicerTest(self)


        
    def __sceneClosedListener(self, caller, event):
        """
        Actions for when the user closes a scene from the GUI.

        @param caller: The object calling the event.
        @type caller: vtk.vtkObject
        @param event: The unsigned long int value of the vent.
        @type event: number
        """ 
        #print("'Close Scene' called. Resetting Xnat session data.")    
        self.View.sessionManager.clearCurrentSession()  


            
            
    def __initGui(self):  
        """ 
        Initializes the GUI of the XNATSlicer widget.
        """
                
        #--------------------------------
        # Make Main Collapsible Button
        #--------------------------------
        self.mainCollapsibleButton = ctk.ctkCollapsibleButton()
        self.mainCollapsibleButton.text = "XNATSlicer"


        
        #--------------------------------
        # Make Collapsible boxes: login, tools, viewer, details.
        #--------------------------------
        self.collapsibles = {}
        self.collapsibleHeights = {}
        self.collapsibleHeights['login'] = 60
        self.collapsibleHeights['tools'] = 60
        self.collapsibleHeights['details'] = 110
        self.collapsibles['login'] = AnimatedCollapsible(self.parent, 'Login')
        self.collapsibles['login'].setMaxExpandedHeight(\
                                              self.collapsibleHeights['login'])

        self.collapsibles['tools'] = AnimatedCollapsible(self.parent, 'Tools')
        self.collapsibles['tools'].setMaxExpandedHeight(\
                                            self.collapsibleHeights['tools'])

        self.collapsibles['viewer'] = AnimatedCollapsible(self.parent, 'Viewer')
        self.collapsibles['viewer'].setSizeGripVisible(True)
        self.collapsibles['viewer'].setMinExpandedHeight(120)

        self.collapsibles['details'] = AnimatedCollapsible(\
                                                  self.parent, 'Details')
        self.collapsibles['details'].setMaxExpandedHeight(\
                                            self.collapsibleHeights['details'])

            
        #--------------------------------
        # DEFINE: Main layout
        #--------------------------------  
        self.__mainLayout = None
                
        
        #--------------------------------
        # Set LOGIN Group Box.
        #--------------------------------    
        self.collapsibles['login'].setContents(self.LoginMenu)


        
        #--------------------------------
        # Set VIEWER Group Box.
        #--------------------------------
        self.Viewer = Viewer(self)
        self.collapsibles['viewer'].setContents(self.Viewer)
        self.collapsibles['details'].setContents(self.NodeDetails)
        self.collapsibles['tools'].setContents(self.Buttons.toolsWidget) 

 
        #--------------------------------
        # Add collapsibles to main layout.
        #--------------------------------
        self.__resetMainLayout(True)
        

        
        #--------------------------------
        # Closes the collapsible group boxes except
        # the login.  We set the animLength of each
        # collapsible to 0 to avoid awkard load animations
        #--------------------------------
        for key, collapsible in self.collapsibles.iteritems():
            collapsible.suspendAnim(True)
            if key == 'login':
                for child in collapsible.getContents():
                    child.hide()
                collapsible.setChecked(True)
            else:
                collapsible.setChecked(False)
                collapsible.setEnabled(False)
            collapsible.suspendAnim(False)
            

            
        #--------------------------------
        # Add main Collapsible button to layout registered
        # to Slicer.
        #--------------------------------
        self.layout.addWidget(self.mainCollapsibleButton)
        
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
        self.LoginMenu.loginButton.connect('clicked()', 
                            self.onLoginButtonClicked)
        #
        # Button event.
        #
        self.Buttons.buttons['io']['load'].connect('clicked()', 
            self.onLoadClicked)
        self.Buttons.buttons['io']['save'].connect('clicked()', 
            self.onSaveClicked)
        self.Buttons.buttons['io']['delete'].connect('clicked()', 
            self.onDeleteClicked)
        self.Buttons.buttons['io']['addFolder'].connect('clicked()', 
            self.FolderMaker.show)
        self.Buttons.buttons['settings']['settings'].connect('clicked()', 
            self.SettingsWindow.showWindow)

        #
        # Test button event.
        #
        # NOTE: Disabling this for now.
        # TODO: Implement a testing suite.
        #
        self.Buttons.buttons['io']['test'].setEnabled(False)
        #
        # Search Bar event.
        #
        self.SearchBar.connect(self.View.searchEntered)




    def __checkSSLInstalled(self):
      """
      """
      try:      
        import ssl
        httplib.HTTPSConnection
        return True
        #MokaUtils.debug.lf("XnatSlicer Module: SSL is installed!")
      except Exception, e:
            return False



    def __showSSLError(self):
      """
      """
      strs = "XnatSlicer cannot operate on this version of " + \
             "Slicer because SSL is not installed."
      strs += "Please download the latest version of Slicer from " + \
              "http://www.slicer.org ."
      #print("XnatSlicer Module: %s"%(strs))
      qt.QMessageBox.warning(slicer.util.mainWindow(), 
                             "No SSL", "%s"%(strs))



    def __checkDicomDBExists(self):
      """
      """
      if not slicer.dicomDatabase:
        return False
      return True




    def __showDicomDBError(self):
      """
      """
      self.dicomDBMessage = qt.QMessageBox (2, "Setup error", 
                                            "XNATSlicer cannot " + 
                                            "proceed without a DICOM " + 
                                            "database.  XNATSlicer will " + 
                                            "now open the DICOM module " +  
                                            "so you can set one up.")
      self.dicomDBMessage.connect('buttonClicked(QAbstractButton*)', 
                                  SlicerUtils.showDicomDetailsPopup)
      self.dicomDBMessage.show()

                


    def __jsonError(self, host, user, response):
      """
      """
      return Error(host, user, response)
    



    def beginXnat(self):
        """ 
        Opens the View class to allow for user interaction.
        Runs a test for the relevant libraries (i.e. SSL)
        before allowing the login process to begin.
        """

        if not self.__checkSSLInstalled():
          self.__showSSLError()
          return

          
        if not self.__checkDicomDBExists():
          self.__showDicomDBError()
          return
        
        #--------------------
        # Init XnatIo.
        #--------------------
        self.XnatIo = Xnat.io(\
        self.SettingsFile.getAddress(self.LoginMenu.hostDropdown.currentText), 
                    self.LoginMenu.usernameLine.text,
                    self.LoginMenu.passwordLine.text)

        self.XnatIo.onEvent('jsonError', self.__jsonError)        

        #--------------------
        # Begin communicator
        #--------------------
        self.View.begin()



    def __putFolderAndSelect(self, xnatUri, sel = True):
      """
      As stated.
      @param xnatUri: The XNAT uri indicating the added folder.
      @type xnatUri: str
      """
      self.XnatIo.putFolder(xnatUri)
      slicer.app.processEvents()
      if not sel:
        return
      self.View.selectItem_byUri(xnatUri.split('?')[0])
      slicer.app.processEvents()



    def __onFolderAdded(self, xnatUri):
      """
      Callback when a folder is added via the FolderMaker class.
      @param xnatUri: The XNAT uri indicating the added folder.
      @type xnatUri: str
      """
      pathDict = XnatSlicerUtils.getXnatPathDict(xnatUri)
      projName = pathDict['projects']
      #MokaUtils.debug.lf(pathDict, projName)
      if not self.View.projectExists(projName):
        #MokaUtils.debug.lf("Project", projName, "does not exist!")
        self.__putFolderAndSelect('projects/' + projName, False)
      self.__putFolderAndSelect(xnatUri)



    def __onAnimatedCollapsibleAnimate(self):
      """
      """
      self.__mainLayout.update()



    def __resetMainLayout(self, createNew = True):
        """
        """

        #--------------------
        # reset main layout
        #-------------------- 
        if createNew:
          self.__mainLayout = qt.QVBoxLayout() 
          for key in self.COLLAPSIBLE_KEYS:
            self.__mainLayout.addWidget(self.collapsibles[key])
          self.mainCollapsibleButton.setLayout(self.__mainLayout)
        
        #--------------------
        # Update mainLayout when animating
        #--------------------
        for key, collapsible in self.collapsibles.iteritems():
            collapsible.onEvent('animate', self.__onAnimatedCollapsibleAnimate)
            



    def __calcTargetHeights(self, state):
        """ 
        Determines the target heights for the various
        collapsibles to animate to by quickly expanding
        the collapsibles, recording their geometries, then
        quickly compressing them.  The user should not 
        notice this calculation.

        @param state: The state to base the height calculations
            on.  Anything that isn't '__expandCollapsibles' will 
            default not be calculated (failed states don't require
            calculation).
        @type state: string
        """

        targetHeights = {}
        marginTops = self.__mainLayout.contentsMargins().top() * \
                     (len(self.collapsibles) + 1)
        parentHeight = self.mainCollapsibleButton.geometry.height() - \
                       marginTops
        collapsedHeight = self.collapsibles['login'].collapsedHeight
        nonFixedHeights = parentHeight - self.collapsibleHeights['tools'] - \
                          collapsedHeight 


        if state == 'loginSuccessful':
          remainderHeight = parentHeight - self.collapsibleHeights['tools'] - \
                            collapsedHeight - self.collapsibleHeights['details']
          for key, collapsible in self.collapsibles.iteritems():
            if key in self.collapsibleHeights:
              if key != 'login':
                targetHeights[key] = self.collapsibleHeights[key]
            else:
              if key == 'viewer':
                targetHeights[key] = (remainderHeight)
          
                
        if state == 'viewerMax' or state == 'detailsMax':
          unfixedHeight = parentHeight - collapsedHeight * 3
          targetHeights['viewer'] = unfixedHeight
        
            
  
        return targetHeights

            


    def __setTargetHeights(self, heights, applyImmediately = False):
        """ 
        @param heights: The target heights. 
        @type heights: dict 
        """
        for key, collapsible in self.collapsibles.iteritems():
          if key in heights:
            self.collapsibles[key].setMaxExpandedHeight(heights[key], 
                                                        applyImmediately)




    def __configTargetHeights(self, state, applyImmediately = False):
        """
        """
        heights = self.__calcTargetHeights(state)
        self.__setTargetHeights(heights, applyImmediately)




    def __printCollapsibleHeights(self, msg = "Collapsible heights:"):
        """
        """
        for key, collapsible in self.collapsibles.iteritems():
          print msg, key, "GEOM", collapsible.geometry.height(), "HINT", \
            collapsible.sizeHint.height()




    def __storeLoginHost(self):
      """
      """
      for key in self.__loggedIn:
        self.__loggedIn[key] = False
      self.__loggedIn[self.LoginMenu.currHostName] = True
      self.__setSettingsWindowLoggedIn()
      

        


          
    def onLoginSuccessful(self, callback = None):
      """
      """
      self.__filterToggled()
      self.__syncSettingsToCurrHost()
      self.__expandCollapsibles(callback)
      self.__storeLoginHost()




      
    def __expandCollapsibles(self, callback = None):
        """ 
        Enables the relevant collapsible 
        group boxes for the user to interact with: 
        Viewer, Details and Tools

        @param callback: The callback to run when the animation is finished.
        @type callback: function
        """

        self.__configTargetHeights('loginSuccessful')
        
        
        #--------------------
        # Create animation chain callbacks.
        #-------------------- 
        def expandViewer():
            slicer.app.processEvents()
            self.collapsibles[ 'viewer' ].setChecked(True)
            self.collapsibles[ 'viewer' ].setEnabled(True)

        def expandDetails():
            slicer.app.processEvents()
            self.collapsibles[ 'details' ].setChecked(True)
            self.collapsibles[ 'details' ].setEnabled(True)
       
        def expandTools():
            slicer.app.processEvents()
            self.collapsibles[ 'tools' ].setChecked(True)
            self.collapsibles[ 'tools' ].setEnabled(True)

      
            
        #--------------------
        # Callback: Clear the animation Chain when
        # the animation chain is finished.
        #--------------------
        def clearChain(): 
          for key, collapsible in self.collapsibles.iteritems():
            collapsible.clearEvents()
            if key == 'viewer' or key == 'details':
              collapsible.toggleButton.setEnabled(False)
              
          self.__configTargetHeights('viewerMax', True)




          if callback: callback()
          self.__resetMainLayout(False)


        #--------------------
        # Apply the callbacks to the collapsibles.
        #--------------------               
        self.collapsibles['viewer'].onEvent('expanded', expandDetails)
        self.collapsibles['details'].onEvent('expanded', expandTools)           
        self.collapsibles['tools'].onEvent('expanded', clearChain)
        self.collapsibles['login'].onEvent('collapsed', expandViewer)

        
        #--------------------
        # Fire off the animation chain.
        #--------------------              
        self.collapsibles['login'].setChecked(False)



        
    def onLoginFailed(self, callback = None):
      """
      """
      for key in self.__loggedIn:
        self.__loggedIn[key] = False
      self.__contractCollapsibles(callback)
      self.__setSettingsWindowLoggedOut()
        



    def __contractCollapsibles(self, callback = None):
        """ 
        Disables and collapses the interactible widgets.

        @param callback: The callback to run when the animation is finished.
        @type callback: function
        """

        if not hasattr(self, 'collapsibles'):
          return

        #--------------------
        # Minimize and enable the others.
        # Create an animation chain.
        #-------------------- 
        def collapseViewer():
            self.collapsibles[ 'viewer' ].setChecked(False)
            self.collapsibles[ 'viewer' ].setEnabled(False)
        self.collapsibles['login'].onEvent('expanded', collapseViewer)

        
        def collapseDetails():
            self.collapsibles[ 'details' ].setChecked(False)
            self.collapsibles[ 'details' ].setEnabled(False)
        self.collapsibles['viewer'].onEvent('collapsed', collapseDetails)

        
        def collapseTools():
            self.collapsibles[ 'tools' ].setChecked(False)
            self.collapsibles[ 'tools' ].setEnabled(False)
        self.collapsibles['details'].onEvent('collapsed', collapseTools)

        

        #--------------------
        # Clear the animation Chain when finished
        #--------------------
        def clearChain(): 
            for key, collapsible in self.collapsibles.iteritems():
                collapsible.clearEvents()
            if callback: callback()

        self.collapsibles['tools'].onEvent('collapsed', clearChain)


        
        #--------------------
        # Re-open the login only if it is closed.
        #--------------------   
        if not self.collapsibles['login'].toggled:    
            self.collapsibles['login'].setChecked(True)
        else:
            self.collapsibles['viewer'].setChecked(False)


            

    def onLoginButtonClicked(self):
        """ 
        Event function for when the login button is clicked.
        """        


        #--------------------
        # Don't re-login if we're already logged into the host.
        #--------------------
        if self.LoginMenu.hostDropdown.currentText in self.__loggedIn and \
           self.__loggedIn[self.LoginMenu.hostDropdown.currentText]:
          self.__loggedIn[self.LoginMenu.hostDropdown.currentText] = False
          self. __contractCollapsibles(self.onLoginButtonClicked)
          return


        #--------------------
        # Store the current username in settings
        #--------------------
        self.SettingsFile.setCurrUsername(self.LoginMenu.hostDropdown.\
                                currentText, self.LoginMenu.usernameLine.text)

        
        #--------------------
        # Clear the current View.
        #--------------------
        self.View.clear()


        #--------------------
        # Derive the XNAT host URL by mapping the current item in the host
        # dropdown to its value pair in the settings.  
        #--------------------
        if self.SettingsFile.\
           getAddress(self.LoginMenu.hostDropdown.currentText):

            self.currHostUrl = \
                  qt.QUrl(self.SettingsFile.\
                          getAddress(self.LoginMenu.hostDropdown.currentText))
            #
            # Call the 'beginXnat' function from the MODULE.
            #
            self.beginXnat()
        else:
            print MokaUtils.lf("The host '%s' doesn't appear to" + 
                  " have a valid URL"%(self.LoginMenu.hostDropdown.currentText))
            pass  




    def onDeleteClicked(self, button=None):
        """ 
        Starts Delete workflow (i.e. Workflow_Delete)
        """  

        xnatWorkflow_Delete = Workflow_Delete(self)
        xnatWorkflow_Delete.beginWorkflow()



            
    def onSaveClicked(self):        
        """ 
        Starts Save workflow (i.e Workflow_Save)
        """     
        
        self.lastButtonClicked = "save" 
        saver = Workflow_Save(self)
        saver.beginWorkflow()


        

    def onTestClicked(self):        
        """ 
        Starts Test workflow.
        """     
        self.lastButtonClicked = "test" 
        self.View.setEnabled(True)
        #self.tester.runTest()


        
    def onLoadClicked(self):
        """ 
        Starts Load workflow (i.e. Workflow_Load).
        """
        
        self.lastButtonClicked = "load"
        self.Workflow_Load = Workflow_Load(self)

        url = self.View.getXnatUri()
        if url.startswith('/'):
            url = url[1:]
        if url.startswith('projects'):
            url = self.SettingsFile.getAddress(self.LoginMenu.\
                            hostDropdown.currentText) + '/data/archive/' + url

        self.Workflow_Load.beginWorkflow(url)




    def __collapseDataProbe(self):
        """
        """
        #--------------------------------
        # Collapse the 'Data Probe' button.
        #--------------------------------
        dataProbeButton = slicer.util.findChildren(text='Data Probe')[0]
        dataProbeButton.setChecked(False)




    @property
    def Settings(self):
        """
        """
        return self.__Settings




    def __initSettings(self):
        """
        """

        
        #-------------------
        # SettingWindow
        #-------------------       
        self.SettingsWindow = SettingsWindow(parent = None, MODULE = self)
        

        #-------------------
        # Create settings
        #-------------------
        self.__Settings = XnatSlicerWidget.__createSettings(self.SettingsFile)


        #-------------------
        # Add settings widget to the window
        #-------------------
        for key, Setting in self.Settings.iteritems():
          self.SettingsWindow.addSetting(Setting.title, widget = Setting)


        self.__setSettingsCallbacks()


 
    
    def __showCustomWindow(self, button, xnatLevel):
        """
        Opens the 'Metadata' tab of the settings window
        and expands the relevant collapsible for editing
        of custom metadata types.
        """
        
        self.SettingsWindow.setTab(self.Settings['METADATA'].title) 
        collapsibles =  self.Settings['METADATA'].\
                        MetadataEditorSets['XNAT Metadata'].\
                        collapsibles
        for level, collapsible in collapsibles.iteritems():
          if level == xnatLevel:
            collapsible.setChecked(True)
          else:
            collapsible.setChecked(False)
          



    def __syncSettingsToFile(self, *args):
      """
      As stated.
      """
      isFontChange = args and 'FONT_SIZE_CHANGED' in args
      isHostChange = args and self.Settings['HOSTS'].__class__.__name__ in args

      #MokaUtils.debug.lf(args[0])
      for key, Setting in self.Settings.iteritems():
        Setting.syncToFile()
        slicer.app.processEvents()
      #try:
      if hasattr(self, 'NodeDetails'):
        self.NodeDetails.updateFromSettings()

      if hasattr(self, 'View'):
        self.View.updateFromSettings()

      if hasattr(self, 'LoginMenu') and isHostChange: 
        self.__syncToHostChanges(args[1], args[2])

      #except Exception, e:
      #  print (MokaUtils.debug.lf(str(e)))
      #  pass




    def __syncToHostChanges(self, hostChangeEvent, hostName):
      """
      Sync function for various changes to Settings_Hosts.

      @param hostChangEvent: The host change event.
      @type hostChangeEvent: str

      @param hostName: The name of the host that the operation was performed on.
      @type hostName: str
      """
      #MokaUtils.debug.lf(hostChangeEvent, hostName, 
      # self.LoginMenu.currHostName)
      
      hostCopy = copy.copy(self.LoginMenu.currHostName)
      isHostAdded = True if hostChangeEvent == 'HOST_ADDED' else False
      isHostDeleted = True if hostChangeEvent == 'HOST_DELETED' else False
      isHostModified = True if hostChangeEvent == 'HOST_MODIFIED' else False
      currLoginHost = self.currLoginHost()
      currHostChanged = self.LoginMenu.currHostName == hostName

      if not currLoginHost or (currLoginHost 
                               and isHostDeleted 
                               and currHostChanged):
        self.LoginMenu.updateFromSettings()
      else:
        self.LoginMenu.Events.suspendEvents(True)
        self.LoginMenu.updateFromSettings()
        self.LoginMenu.setHost(hostCopy)
        self.LoginMenu.Events.suspendEvents(False)




    def __setSettingsCallbacks(self):
        """
        """

        self.SettingsFile.Events.onEvent('SETTINGS_FILE_RESTORED',
                                         self.__syncSettingsToFile)

        for key, Setting in self.Settings.iteritems():
          Setting.Events.onEvent('SETTINGS_FILE_MODIFIED', \
                                 self.__syncSettingsToFile)

          if hasattr(Setting, 'MetadataEditorSets'):
            for setKey, _set in Setting.MetadataEditorSets.iteritems():
              _set.Events.onEvent('editCustomClicked', self.__showCustomWindow)
          

          if key == 'VIEW':
                                  
            #
            # Sort Button event.
            #
            #for key, button \
            #    in self.__Settings['VIEW'].buttons['sort'].iteritems():
              #button.connect('clicked()', self.onFilterButtonClicked)

            self.__Settings['VIEW'].Events.onEvent('FILTERTOGGLED',
                                 self.__filterToggled)

            self.__Settings['VIEW'].linkToSetting(Settings_View.LABEL_METADATA,
                                  self.Settings['METADATA'], 'XNAT Metadata')



          if key == 'DETAILS':

            self.__Settings['DETAILS'].linkToSetting(\
                      Settings_Details.LABEL_METADATA, 
                                  self.Settings['METADATA'], 'XNAT Metadata')



  

    @staticmethod
    def __createSettings(_SettingsFile):
        """
        @param _SettingsFile: The SettingsFile
        @type _SettingsFile: SettingsFile

        @return: An ordered dictionary of the Settings.
        @rtype: collections.OrderedDict(string, Settings)
        """
        settingsDict = OrderedDict([
          ('HOSTS', Settings_Hosts(_SettingsFile)),
          ('CACHE' , Settings_Cache(_SettingsFile)),
          ('METADATA', Settings_Metadata(_SettingsFile)),
          ('VIEW', Settings_View(_SettingsFile, 'View')),
          ('DETAILS' , Settings_Details(_SettingsFile)),
         ])
        return settingsDict



    def __setNodeDetailsCallbacks(self):
      """
      """
      #
      # Link a node click to populate NodeDetails.
      #
      self.View.Events.onEvent('nodeChanged', 
                               self.NodeDetails.setXnatNodeText)



  
    def __initLoginMenu(self):
      """
      As stated.
      """

      self.LoginMenu = LoginMenu(parent = self.parent, MODULE = self, 
                                Setting = self.Settings['HOSTS'])
      self.__setLoginMenuCalbacks()
      
      # This exists basically for running the collapse anim
      self.__loggedIn = {}
      self.LoginMenu.loadDefaultHost() 
      self.__setSettingsWindowLoggedOut()




    def currLoginHost(self):
      """
      @return: The key of the loggin host or None
      @rtype: str
      """
      for key, val in self.__loggedIn.iteritems():
        if val: return key
      return None
      



    def __setSettingsWindowLoggedOut(self):
      """
      """
      self.SettingsWindow.setAllTabsEnabled(False)
      self.SettingsWindow.setTabEnabled('Hosts')




    def __setSettingsWindowLoggedIn(self):
      """
      """
      self.SettingsWindow.setAllTabsEnabled(True)




    def __setLoginMenuCalbacks(self):
      """
      As stated.
      """
      self.LoginMenu.Events.onEvent('MANAGEHOSTSCLICKED', self.__showHostWindow)
      self.LoginMenu.Events.onEvent('HOSTSELECTED', self.__onHostSelected)



    def __showHostWindow(self, *args):
      """
      As stated.
      """
      try:
        self.SettingsWindow.showWindow(self.__Settings['HOSTS'].title)
      except Exception, e:
        print "Error opening Host Settings: %s"%(str(e))



    def __syncSettingsToCurrHost(self, host = None):
      """
      """
      if not host:
        host = self.LoginMenu.hostDropdown.currentText
      for key, Setting in self.__Settings.iteritems():
        Setting.currXnatHost = host
        #MokaUtils.debug.lf(Setting.__class__.__name__)
        Setting.syncToFile()
        slicer.app.processEvents()

      

    def __onHostSelected(self, host):
      """
      As stated.

      @param host: The selected host:
      @type host: str
      """

      if not host in self.__loggedIn or not self.__loggedIn[host]:
        self.__contractCollapsibles(self.__syncSettingsToCurrHost)
      else:
        self.__syncSettingsToCurrHost()
        
        self.__expandCollapsibles()




    def __filterToggled(self, toggled = None):
        """
        As stated.

        @param toggled: Whether the button clicked is toggled.
        @type toggled: bool
        """
        #MokaUtils.debug.lf("FILTER TOGGLED", self.__Settings['VIEW'].\
          #   buttons['sort']['accessed'].isChecked())

        if toggled == None:
          toggled = self.__Settings['VIEW'].CHECKBOXES\
                    ['lastAccessed']['widget'].isChecked()
        if toggled:
          self.View.filter_accessed()
        else:
          self.View.filter_all()
