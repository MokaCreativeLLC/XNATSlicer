# python
import imp
import os
import inspect
import sys
import math
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






comment = """
XNAT Software License Agreement

Copyright 2005 Harvard University / Howard Hughes Medical Institute (HHMI) / 
Washington University
All rights reserved.

Redistribution and use in source and binary forms, with or without 
modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this 
list of conditions and the following disclaimer.  Redistributions in binary 
form must reproduce the above copyright notice, this list of conditions and 
the following disclaimer in the documentation and/or other materials provided 
with the distribution.  Neither the names of Washington University, Harvard 
University and HHMI nor the names of its contributors may be used to endorse 
or promote products derived from this software without specific prior written 
permission.

THIS SOFTWARE IS PROVIDED BY The COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND 
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, The IMPLIED 
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
DISCLAIMED. IN NO EVENT SHALL The COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE 
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL 
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER 
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, 
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF The USE 
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""




class XnatSlicer:
  """ 
  This is the class that interfaces with Slicer.
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


    COLLAPSIBLE_KEYS = ['login', 'viewer', 'details', 'tools']
    
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

        #--------------------------------
        # Construct all needed directories
        # if not there...
        #--------------------------------
        XnatSlicerUtils.constructNecessaryModuleDirectories()



        #--------------------------------
        # Collapse the data probe button
        #--------------------------------
        self.__collapseDataProbe()


        #--------------------------------
        # Xnat IO
        #--------------------------------
        self.XnatIo = None 

        
        #--------------------------------
        # Set the layout
        #--------------------------------
        self.layout = self.parent.layout()


        #-------------------
        # SettingsFile
        #-------------------
        self.SettingsFile = SettingsFile(slicer.qMRMLWidget(), 
            XnatSlicerGlobals.LOCAL_URIS['settings'], self)
    

        #-------------------
        # Settings
        #-------------------
        self.__initSettings()


        #-------------------
        # Login Menu
        #-------------------
        self.__initLoginMenu()
        

        #--------------------------------
        # SearchBar
        #--------------------------------
        self.SearchBar = SearchBar(MODULE = self)

      
        #--------------------------------
        # Viewer
        #--------------------------------
        self.View = View_Tree(self, self.Settings['VIEW'])  

        
        
        #--------------------------------
        # Node Details
        #--------------------------------
        self.NodeDetails = NodeDetails(self.Settings['DETAILS'])
        self.__setNodeDetailsCallbacks()
        

        
        #--------------------------------
        # Xnat Buttons
        #--------------------------------
        self.Buttons = Buttons(self.parent, MODULE=self)  
        
        


        #--------------------------------
        # Xnat Folder Maker
        #--------------------------------
        self.FolderMaker = FolderMaker(None, self)



        
        #--------------------------------
        # Init gui
        #--------------------------------
        self.initGUI()
        
        
        
        #--------------------------------
        # Listeners/observers from gui
        #--------------------------------
        slicer.mrmlScene.AddObserver(slicer.mrmlScene.EndCloseEvent, 
                                     self.sceneClosedListener)
        slicer.mrmlScene.AddObserver(slicer.mrmlScene.EndImportEvent, 
                                     self.sceneImportedListener)



        #--------------------------------
        # Tester
        #--------------------------------
        #self.tester = XnatSlicerTest(self)



        #--------------------------------
        # Clean the temp dir
        #--------------------------------
        self.cleanCacheDir(200)

        
      

      
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
    


        
    def sceneClosedListener(self, caller, event):
        """
        Actions for when the user closes a scene from the GUI.

        @param caller: The object calling the event.
        @type caller: vtk.vtkObject
        @param event: The unsigned long int value of the vent.
        @type event: number
        """ 
        #print("'Close Scene' called. Resetting Xnat session data.")    
        self.View.sessionManager.clearCurrentSession()  



        
    def sceneImportedListener(self, caller, event): 
        """
        Actions for when the user imports a scene from the GUI.
        NOTE: This technically is not used, as the user must refer to files 
        from an XNAT location. Nonetheless, it is implemented in the event 
        that it is needed.

        @param caller: The object calling the event.
        @type caller: vtk.vtkObject
        @param event: The unsigned long int value of the vent.
        @type event: number
        """
        if self.View.lastButtonClicked == None:
            #print("'Import Data' called. Resetting Xnat session data.")
            self.View.sessionManager.clearCurrentSession() 
    

            
            
    def initGUI(self):  
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
        #
        # set in '__resetMainLayout'
        #--------------------------------  
        self.__mainLayout = None
                
        #self.mainCollapsibleButton.setLayout(self.__mainLayout)
        


        
        #--------------------------------
        # Set LOGIN Group Box.
        #--------------------------------    
        self.collapsibles['login'].setContents(self.LoginMenu)


        
        #--------------------------------
        # Set VIEWER Group Box.
        #--------------------------------
        self.Viewer = Viewer(self)
        self.collapsibles['viewer'].setContents(self.Viewer)



        #--------------------------------
        # Set DETAILS Group Box.
        #-------------------------------- 
        #
        # Add detauls layout to group box.
        #
        self.collapsibles['details'].setContents(self.NodeDetails)


        

        
        #--------------------------------
        # Set TOOLS Group Box.
        #-------------------------------- 
        #
        # Add tools layout to group box.
        #
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



        
    def cleanCacheDir(self, maxSize):
        """ 
        Empties contents of the temp directory based on the maxSize argument.

        @param maxSize: The maximum size in MB allowed for the cache directory.
        @type maxSize: An number >= 0.
        """

        if maxSize < 0:
          raise Exception("'maxSize' argument must be greater than or" + 
                          " equal to 0!")


        folder = XnatSlicerGlobals.CACHE_URI
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
          shutil.rmtree(folder)
          os.mkdir(folder)




                
    def beginXnat(self):
        """ 
        Opens the View class to allow for user interaction.
        Runs a test for the relevant libraries (i.e. SSL)
        before allowing the login process to begin.
        """

        #--------------------
        # Can SSL be imported?
        #--------------------
        #print("XnatSlicer Module: Checking if SSL is installed...")
        try:      
            import ssl
            httplib.HTTPSConnection
            #print("XnatSlicer Module: SSL is installed!")

            

        #--------------------
        # If not, kick back OS error
        #--------------------
        except Exception, e:
            strs = "XnatSlicer cannot operate on this version of " + \
                   "Slicer because SSL is not installed."
            strs += "Please download the latest version of Slicer from " + \
                    "http://www.slicer.org ."
            #print("XnatSlicer Module: %s"%(strs))
            qt.QMessageBox.warning(slicer.util.mainWindow(), 
                                   "No SSL", "%s"%(strs))
            return
                


        #----------------------
        # Check dicom database.  Error if none.
        #----------------------
        if not slicer.dicomDatabase:
          self.dicomDBMessage = qt.QMessageBox (2, "Setup error", 
                                                "XNATSlicer cannot " + \
          "proceed without a DICOM database.  XNATSlicer will now open" + \
                                    " the DICOM module so you can set one up.")
          self.dicomDBMessage.connect('buttonClicked(QAbstractButton*)', 
                                      SlicerUtils.showDicomDetailsPopup)
          self.dicomDBMessage.show()
          self.__contractCollapsibles()
          return  


        
        #--------------------
        # Init XnatIo.
        #--------------------
        self.XnatIo = Xnat.io(self.SettingsFile.\
                        getAddress(self.LoginMenu.hostDropdown.currentText), 
                              self.LoginMenu.usernameLine.text,
                              self.LoginMenu.passwordLine.text)
        def jsonError(host, user, response):
            return Error(host, user, response)
        self.XnatIo.onEvent('jsonError', jsonError)        



        #--------------------
        # Begin communicator
        #--------------------
        self.View.begin()






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
        def onAnimatedCollapsibleAnimate():
            self.__mainLayout.update()
        for key, collapsible in self.collapsibles.iteritems():
            collapsible.onEvent('animate', onAnimatedCollapsibleAnimate)
            



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
      

        


          
    def onLoginSuccessful(self, callback = None):
      """
      """
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
        #self.collapsibles['viewer'].onEvent('expanded', clearChain)
        #self.collapsibles['details'].onEvent('expanded', expandViewer)         
        #self.collapsibles['tools'].onEvent('expanded', expandDetails)
        #self.collapsibles['login'].onEvent('collapsed', expandTools)
            
        
        #--------------------
        # Fire off the animation chain,
        # first by compressing the 'Login'
        # collapsible.
        #--------------------              
        self.collapsibles['login'].setChecked(False)




        
    def onLoginFailed(self, callback = None):
      """
      """
      self.__contractCollapsibles(callback)
        



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




    def onFilterButtonClicked(self):
        """ 
        As stated.  Handles the toggling of filter
        buttons relative to one another in the View
        class.
        """


        try:
            self.Buttons.buttons['filter']
        except Exception, e:
            return
        #-----------------
        # Count down buttons
        #------------------
        checkedButtons = 0
        buttonLength = len(self.Buttons.buttons['filter'])
        for key in self.Buttons.buttons['filter']:
           currButton = self.Buttons.buttons['filter'][key]
           if currButton.isChecked():
               checkedButtons += 1

               
               
        #-----------------
        # If there are no down buttons, apply the ['all']
        # filter and return.
        #------------------
        if checkedButtons == 0:
            for key in self.Buttons.buttons['filter']:
                self.Buttons.buttons['filter'][key].setDown(False)
                self.Buttons.buttons['filter'][key].setChecked(False)
            self.currentlyToggledFilterButton = ''
            self.View.loadProjects(['all'])
            return
 

        
        #-----------------
        # If a new button has been clicked
        # then set it as the self.currentlyToggledFilterButton. 
        #------------------
        for key in self.Buttons.buttons['filter']:
            currButton = self.Buttons.buttons['filter'][key]
            if currButton.isChecked() and \
               self.currentlyToggledFilterButton != currButton:
                self.currentlyToggledFilterButton = currButton
                break

            
                
        #-----------------
        # Un-toggle previously toggled buttons.
        #-----------------
        for key in self.Buttons.buttons['filter']:
            currButton = self.Buttons.buttons['filter'][key]
            if currButton.isChecked() and \
               self.currentlyToggledFilterButton != currButton:
                currButton.setDown(False)

                

        #-----------------
        # Apply method
        #------------------
        for key in self.Buttons.buttons['filter']:
            if self.currentlyToggledFilterButton == \
               self.Buttons.buttons['filter'][key]:
                self.View.loadProjects([\
                              self.currentlyToggledFilterButton.text.lower()])





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

      #MokaUtils.debug.lf(args[0])
      for key, Setting in self.Settings.iteritems():
        Setting.syncToFile()
        slicer.app.processEvents()
      #try:
      if hasattr(self, 'NodeDetails'):
        self.NodeDetails.updateFromSettings()
      if hasattr(self, 'View'):
        self.View.updateFromSettings()
      if hasattr(self, 'LoginMenu') and not isFontChange:
        #MokaUtils.debug.lf()
        self.LoginMenu.updateFromSettings()
      #except Exception, e:
      #  print (MokaUtils.debug.lf(str(e)))
      #  pass




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
                                  
            def filterToggled():
              #MokaUtils.debug.lf("FILTER TOGGLED", self.__Settings['VIEW'].\
              #   buttons['sort']['accessed'].isChecked())
              if self.__Settings['VIEW'].\
                 buttons['sort']['accessed'].isChecked():
                self.View.filter_accessed()
              else:
                self.View.filter_all()

            #
            # Sort Button event.
            #
            for key, button \
                in self.__Settings['VIEW'].buttons['sort'].iteritems():
              button.connect('clicked()', self.onFilterButtonClicked)

            self.__Settings['VIEW'].Events.onEvent('FILTERTOGGLED',
                                                       filterToggled)

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




    def __onHostSelected(self, host):
      """
      As stated.
      """
      for key, Setting in self.__Settings.iteritems():
        Setting.currXnatHost = host
        #MokaUtils.debug.lf(Setting.__class__.__name__)
        Setting.syncToFile()

      if not host in self.__loggedIn or not self.__loggedIn[host]:
        self.__contractCollapsibles()
      else:
        self.__expandCollapsibles()
