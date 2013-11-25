from __main__ import qt

import os
import sys
from XnatUtils import *



comment = """
XnatFileInfo is a class that primarily deals with uri  
manipulation of various files pertinent to the XnatWorkflow.  Relevant 
characteristics include: remoteURI (ie, its Xnat origin), localURI (where 
it is cached locally), basename, extension, etc.  XnatFiles can be further 
specialized for manipulation relative to that files used in the given 
workflow -- uploading, downloading, etc.  Its primary use is within
the 'XnatSceneLoadWorkflow' though, as other workflows grow more complex,
it can be applied there as well.

TODO : Create child classes of XnatFileInfo -- right now it tries to 
handle everything.
"""



FILEINFO = {}
class XnatFileInfo(object):
    def __init__(self, remoteURI, localURI):
        """ Init function.
        """
        
        #----------------------
        # Replace all double slashes for local files.
        #----------------------        
        localURI = localURI.replace("//", "/").replace("\\\\", "/").replace("\\", "/")


        
        #----------------------
        # Define the remote filesnames. (path included) Ex. for "http://foo/file.exe" returns "http://foo/file.exe"
        #----------------------
        FILEINFO["remoteURI"] = remoteURI
        FILEINFO["remoteURINoHost"] = qt.QUrl(remoteURI).path()
        FILEINFO["remoteHost"] = qt.QUrl(remoteURI).host()

        

        #----------------------
        # Derived remove URIs.
        #----------------------
        FILEINFO["remoteDirName"] = os.path.dirname(remoteURI)
        FILEINFO["remoteBasename"] = os.path.basename(remoteURI)


        
        #----------------------
        # Local and related derived URIs.
        #----------------------        
        FILEINFO["localURI"] = localURI
        FILEINFO["localDirName"] = os.path.dirname(localURI)
        FILEINFO["localBasename"]  = os.path.basename(localURI)


        
        #----------------------
        # Other.
        #---------------------- 
        if FILEINFO["remoteBasename"] == FILEINFO["localBasename"]:
            FILEINFO["basename"] = os.path.basename(localURI)
            FILEINFO["basenameNoExtension"] = FILEINFO["basename"].split(".")[0]
            FILEINFO["extension"]           = "." + FILEINFO["basename"].split(".")[1]


            
    @property    
    def remoteURI(self):
        return FILEINFO["remoteURI"] 


    
    @property    
    def remoteURINoHost(self):
        return FILEINFO["remoteURINoHost"] 


    
    @property 
    def localURI(self):
        return FILEINFO["localURI"]


    
    @property 
    def remoteDirName(self):
        return FILEINFO["remoteDirName"]


    
    @property 
    def localDirName(self):
        return FILEINFO["localDirName"]


    
    @property 
    def basename(self):
        return FILEINFO["basename"]


    
    @property 
    def basenameNoExtension(self):
        return FILEINFO["basenameNoExtension"]


    
    @property 
    def extension(self):
        return FILEINFO["extension"]


    
    @property 
    def remoteHost(self):
        return FILEINFO["remoteHost"]


    
    @remoteHost.setter
    def remoteHost(self, remoteHost):
        FILEINFO["remoteHost"] = remoteHost


