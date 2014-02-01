from __main__ import qt

import os
import sys
from XnatSlicerUtils import *




class FileInfo(object):
    """
    FileInfo is a class that primarily deals with uri  
    manipulation of various files pertinent to the XnatWorkflow.  Relevant 
    characteristics include: remoteURI (ie, its Xnat origin), localURI (where 
    it is cached locally), basename, extension, etc.  XnatFiles can be further 
    specialized for manipulation relative to that files used in the given 
    workflow -- uploading, downloading, etc.  Its primary use is within
    the 'XnatSceneWorkflow_Load' though, as other workflows grow more complex,
    it can be applied there as well.
    
    @todo: Create child classes of FileInfo -- right now it tries to 
    handle everything.

    """
    def __init__(self, remoteURI, localURI):
        """ 
        """
        
        #----------------------
        # Replace all double slashes for local files.
        #----------------------        
        localURI = localURI.replace("//", "/").replace("\\\\", "/").replace("\\", "/")


        
        #----------------------
        # Define the remote filesnames. (path included) Ex. for "http://foo/file.exe" returns "http://foo/file.exe"
        #----------------------
        self.fileInfo = {}
        self.fileInfo["remoteURI"] = remoteURI
        self.fileInfo["remoteURINoHost"] = qt.QUrl(remoteURI).path()
        self.fileInfo["remoteHost"] = qt.QUrl(remoteURI).host()

        

        #----------------------
        # Derived remove URIs.
        #----------------------
        self.fileInfo["remoteDirName"] = os.path.dirname(remoteURI)
        self.fileInfo["remoteBasename"] = os.path.basename(remoteURI)


        
        #----------------------
        # Local and related derived URIs.
        #----------------------        
        self.fileInfo["localURI"] = localURI
        self.fileInfo["localDirName"] = os.path.dirname(localURI)
        self.fileInfo["localBasename"]  = os.path.basename(localURI)


        
        #----------------------
        # Other.
        #---------------------- 
        if self.fileInfo["remoteBasename"] == self.fileInfo["localBasename"]:
            self.fileInfo["basename"] = os.path.basename(localURI)
            self.fileInfo["basenameNoExtension"] = self.fileInfo["basename"].split(".")[0]
            self.fileInfo["extension"]           = "." + self.fileInfo["basename"].split(".")[1]


            
    @property    
    def remoteURI(self):
        return self.fileInfo["remoteURI"] 


    
    @property    
    def remoteURINoHost(self):
        return self.fileInfo["remoteURINoHost"] 


    
    @property 
    def localURI(self):
        return self.fileInfo["localURI"]


    
    @property 
    def remoteDirName(self):
        return self.fileInfo["remoteDirName"]


    
    @property 
    def localDirName(self):
        return self.fileInfo["localDirName"]


    
    @property 
    def basename(self):
        return self.fileInfo["basename"]


    
    @property 
    def basenameNoExtension(self):
        return self.fileInfo["basenameNoExtension"]


    
    @property 
    def extension(self):
        return self.fileInfo["extension"]


    
    @property 
    def remoteHost(self):
        return self.fileInfo["remoteHost"]


    
    @remoteHost.setter
    def remoteHost(self, remoteHost):
        self.fileInfo["remoteHost"] = remoteHost


