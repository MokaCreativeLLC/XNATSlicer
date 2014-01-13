#python
import os
import sys
import shutil
import csv

#application
from __main__ import vtk, ctk, qt, slicer

#external
from Xnat import XnatGlobals

#module
from Timer import *
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
    def __init__(self, MODULE = None):
        """ 

        """
        
        self.MODULE = MODULE
        self.sessionManager = SessionManager(self.MODULE)
        self.setup()


        
        #--------------------
        # For for populating details window.
        #--------------------
        self.nodeChangedCallbacks = []

        
        
        
    def loadProjects(self):
        """ To be inherited by child class.
        """
        pass


    
    
    def begin(self, skipAnim = None):
        """ Begins the communication process with.  Shows
            an error modal if it fails.
        """

        #----------------------
        # If there's no project cache, query for 
        # project contents...
        #----------------------
        projectContents = None
        if self.MODULE.XnatIo.projectCache == None:
            self.clear()
            projectContents = self.MODULE.XnatIo.getFolder('projects', XnatGlobals.DEFAULT_METADATA['projects'], 'accessible')
            #
            # If the class name of the Json is 'Error'
            # return out, with the error.
            #
            if projectContents == None:
                hostName = self.MODULE.LoginMenu.hostDropdown.currentText
                hostUrl = self.MODULE.SettingsFile.getAddress(hostName)
                qt.QMessageBox.warning( None, "Login error", "Invalid username and/or password for the XNAT host '%s' (%s)" %(hostName, hostUrl))
                self.MODULE.onLoginFailed()
                return


            
        #----------------------
        # Create View items via 'loadProjects' assuming
        # that there's projectCotnents
        #----------------------
        projectsLoaded = self.loadProjects(filters = None, projectContents = projectContents)
        if projectsLoaded:
            if not skipAnim:
                self.MODULE.onLoginSuccessful()
            self.MODULE.Buttons.setEnabled(buttonKey='addFolder', enabled=True) 



        

    def addNodeChangedCallback(self, callback):
        """ 
        @param callback: The callback for when a view node changes.
        @type callback: function
        """
        self.nodeChangedCallbacks.append(callback)


        
    

    def runNodeChangedCallbacks(self, *args):
        """
        """
        for callback in self.nodeChangedCallbacks:
            callback(args)


            

