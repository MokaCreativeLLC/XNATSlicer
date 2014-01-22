# application
from __main__ import qt

# external
from Xnat import *

# module
from Timer import *
from SlicerUtils import *
from XnatSlicerUtils import *
from SessionManager import *




class View(object):
    """
    View is the class that handles all of the UI interactions 
    to the XnatIo.  It is meant to serve as a parent
    class to various View schemes such as TreeView.
    
    @todo:  Consider sending more functions from TreeView
    here. 
    """

    EVENT_TYPES = [
        'nodeChanged',
    ] 


    def __init__(self, MODULE = None):
        """ 
        @param MODULE: The XNATSlicer module
        @type MODULE: XnatSlicerWidget
        """
        
        self.MODULE = MODULE
        self.sessionManager = SessionManager(self.MODULE)
        self.setup()


        
        #--------------------
        # Events
        #--------------------
        self.Events = MokaUtils.Events(self.EVENT_TYPES)

        
        
        
    def loadProjects(self):
        """ 
        To be inherited by child class.
        """
        pass


    
    
    def begin(self, skipAnim = False):
        """ 
        Begins the the View communication process, 
        first by retrieving the projects from the XNAT server 
        based on the user's credentials.
        
        Displays error message boxes accordingly (server communication issues,
        or credential issues.)

        @param skipAnim: Whether to skip the animation.
        @type skipAnim: bool
        """


        #----------------------
        # Check projects
        #----------------------
        projectContents = None
        if self.MODULE.XnatIo.projectCache == None:
            self.clear()
            projectContents = None

            try:
                projectContents = self.MODULE.XnatIo.getFolder('projects', Xnat.metadata.DEFAULT_TAGS['projects'], 'accessible')

            #
            # Error: SERVER ISSUES
            #
            except Exception, e:
                self.showError("Server error", "Server error for 'HOST_NAME' (HOST_URL):\n%s" %(str(e)))
                return
                
            #
            # Error: LOGIN
            #
            if projectContents == None:
                self.showError("Login error", "Invalid username and/or password for the XNAT host 'HOST_NAME' (HOST_URL).")
                return


            
        #----------------------
        # Load projects ino View.
        #----------------------
        self.loadProjects(filters = None, projectContents = projectContents)
        slicer.app.processEvents()
        if not skipAnim:
            self.MODULE.onLoginSuccessful()
        self.MODULE.Buttons.setEnabled(buttonKey='addFolder', enabled=True) 




    def showError(self, title, msg):
        """
        Displays an error message box.

        @param title: The message box title.
        @type title: str

        @param msg: The error message.
        @type msg: str
        """
        hostName = self.MODULE.LoginMenu.hostDropdown.currentText
        hostUrl = self.MODULE.SettingsFile.getAddress(hostName)
        qt.QMessageBox.warning( None, title, msg.replace('HOST_NAME', hostName).replace('HOST_URL', hostUrl))
        self.MODULE.onLoginFailed()





