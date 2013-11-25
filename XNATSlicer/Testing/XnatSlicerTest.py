from __main__ import vtk, qt, ctk, slicer


import unittest


from XnatIo import *



comment =  """

"""





class XnatSlicerTest(unittest.TestCase):
    """
    This is the test case for your XnatSlicer.
    """



    
    def __init__(self, MODULE):
        self.MODULE = MODULE
        self.testTracker = {}
        self.user = 'XnatSlicerTester'
        self.password = 'xnatslicer01'
        self.currHost = 'Central'



        
    def delayDisplay(self, message, msec=1000):
      """This utility method displays a small dialog and waits.
      This does two things: 1) it lets the event loop catch up
      to the state of the test so that rendering and widget updates
      have all taken place before the test continues and 2) it
      shows the user/developer/tester the state of the test
      so that we'll know when it breaks.
      """

      
      print(message)
      self.info = qt.QDialog()
      self.infoLayout = qt.QVBoxLayout()
      self.info.setLayout(self.infoLayout)
      self.label = qt.QLabel(message,self.info)
      self.infoLayout.addWidget(self.label)
      qt.QTimer.singleShot(msec, self.info.close)
      self.info.exec_()


        
    def setUp(self):
      """ Do whatever is needed to reset the state - typically a scene clear will be enough.
      """
      slicer.mrmlScene.Clear(0)

      

      
    def runTest(self):
      """Run as few or as many tests as needed here.
      """

      if not self.MODULE.utils.isCurrSceneEmpty(): 
          self.initClearDialog();
          self.clearSceneDialog.connect('buttonClicked(QAbstractButton*)', self.testLogin) 
          self.clearSceneDialog.show()
      else:
          self.testLogin()



      
    def initClearDialog(self):
        """ Initiates/resets dialog for window to clear the current scene.
        """
        try: 
            self.clearSceneDialog.delete()
        except: 
            pass
        
        self.clearSceneDialog = qt.QMessageBox()
        self.clearSceneDialog.setStandardButtons(qt.QMessageBox.Yes | qt.QMessageBox.No)
        self.clearSceneDialog.setDefaultButton(qt.QMessageBox.No)
        self.clearSceneDialog.setText("In order to run tests " + 
                                      "you have to clear the current scene." + 
                                      "\nAre you sure you want to clear?")


        
        
    def testLogin(self, button = None):
        """ Tests a login to central.xnat.org.
        """


        # For the "Clear Scene" dialog.
        if (button and 'no' in button.text.lower()):
            return
            
        
        # Clear the scene
        self.setUp()

        
        # Add 'login' componenet to testTracker
        self.testTracker['login'] = {}
        

        # Cannot proceed without a MODULE object
        if not self.MODULE:
            print "XnatSlicerTest: No MODULE set.  Returning..."
            return

        
        self.delayDisplay("Starting the login test...") 


        # Set the current index of the dropdown to Central
        # by finding central in dropdown
        print ("Finding %s in hostDropdown..."%(self.currHost))

        
        # Default results are False, until proven otherwise
        self.testTracker['login']['success'] = False
        self.testTracker['login']['error'] = 'Cannot find currHost: %s in the host dropdown!'%(self.currHost) 

        index = 0
        
        for i in range(0, self.MODULE.XnatLoginMenu.hostDropdown.maxVisibleItems):

            #
            # If central is found in dropdown....
            #
            if self.currHost.lower() in self.MODULE.XnatLoginMenu.hostDropdown.itemText(i).lower():

                
                print ("Found %s in hostDropdown in index %s.\nSetting its current index to %s."%(self.currHost, i, i))
                self.MODULE.XnatLoginMenu.hostDropdown.setCurrentIndex(i)

                currText = self.MODULE.XnatLoginMenu.hostDropdown.currentText
                print ("Getting address from hostDropdown.currentText: %s"%(currText))

                
                settingsAddr = self.MODULE.XnatSettingsFile.getAddress(currText)
                print ("And the address is: %s"%(settingsAddr))

                print ("Calling XnatIo. server: %s\nuser: %s\npassword: %s"%(settingsAddr, self.user, self.password))
                self.MODULE.XnatIo = XnatIo(MODULE = self.MODULE, 
                                                                 server = settingsAddr, 
                                                                 user = self.user, password = self.password)     
                
                try:
                    print ("Getting 'projects' folder of %s"%(settingsAddr))
                    projects, sizes = self.MODULE.XnatIo.getFolderContents(['/projects'], 'ID')
                    self.testTracker['login']['success'] = True
                    
                except Exception, e:
                    self.testTracker['login']['success'] = False
                    self.testTracker['login']['error'] = str(e) + " (likely an invalid user or password)"
                    

                break

            
        # Show results
        print ("")
        if self.testTracker['login']['success']:
            self.testTracker['login']['error'] = None
            printStr = "Login test succeeded!" 
            print projects
            self.delayDisplay(printStr)

            
        else:
            errStr = self.testTracker['login']['error']
            failStr = "Login test FAILED!" 
            fullStr =  failStr + " " + errStr
            self.delayDisplay(fullStr)                
            
