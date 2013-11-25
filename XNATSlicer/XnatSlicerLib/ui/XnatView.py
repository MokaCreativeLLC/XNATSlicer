from __main__ import vtk, ctk, qt, slicer

import os
import sys
import shutil
import csv

from XnatTimer import *
from XnatSessionManager import *



comment = """
XnatView is the class that handles all of the UI interactions 
to the XnatIo.  It is meant to serve as a parent
class to various XnatView schemes such as XnatTreeView.

TODO:  Consider sending more functions from XnatTreeView
       here. 
"""



class XnatView(object):

    def __init__(self, MODULE = None):
        """ Sets parent and MODULE parameters.
        """
        
        self.MODULE = MODULE
        self.sessionManager = XnatSessionManager(self.MODULE)
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
            projectContents = self.MODULE.XnatIo.getFolderContents(queryUris = ['/projects'], 
                                                                              metadataTags = self.MODULE.utils.XnatMetadataTags_projects,
                                                                              queryArguments = ['accessible'])
            #
            # If the class name of the Json is 'XnatError'
            # return out, with the error.
            #
            if projectContents.__class__.__name__ == 'XnatError':
                qt.QMessageBox.warning( None, "Login error", projectContents.errorMsg)
                self.MODULE.onLoginFailed()
                return


            
        #----------------------
        # Create XnatView items via 'loadProjects' assuming
        # that there's projectCotnents
        #----------------------
        projectsLoaded = self.loadProjects(filters = None, projectContents = projectContents)
        if projectsLoaded:
            if not skipAnim:
                self.MODULE.onLoginSuccessful()
            self.MODULE.XnatButtons.setEnabled(buttonKey='addProj', enabled=True) 



        

    def addNodeChangedCallback(self, callback):
        """ 
        """
        self.nodeChangedCallbacks.append(callback)


        
    

    def runNodeChangedCallbacks(self, *args):
        """
        """
        for callback in self.nodeChangedCallbacks:
            callback(args)


            

