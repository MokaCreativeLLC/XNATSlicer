# python
from __future__ import with_statement
import os
import unittest
import glob
import shutil
import sys
import zipfile
import tempfile
import platform
import inspect
import datetime
import time 
import inspect
from contextlib import closing
from zipfile import ZipFile, ZIP_DEFLATED

# application
from __main__ import vtk, ctk, qt, slicer

# external
from Xnat import *
from MokaUtils import *

# module
from XnatSlicerGlobals import *
from HoverButton import *




class XnatSlicerUtils(object):
    """
    XnatSlicerUtils contains a variety of utility methods
    for XNAT interactions used throughout the
    XNATSlicer suite. 

    All of its methods are static; the user doesn't 
    need to instantiate the XnatSlicerUtils class to
    use it.
    """

    @staticmethod
    def constructNecessaryModuleDirectories():
        """ 
        Makes any of the needed modules paths on the
        local system.
        """
        for key, val in XnatSlicerGlobals.LOCAL_URIS.iteritems():
            if not os.path.exists(val):    
                os.makedirs(val)




    @staticmethod        
    def isRecognizedFileExt(ext):
        """ 
        Determine if an extension is a readable file
        by Slicer and/or XNATSlicer.

        @param ext: The extension the check.
        @type ext: string

        @return: Whether the filename belongs to the category.
        @rtype: string
        """
        if len(ext) > 0 and ext[0] != '.':   ext = "." + ext
        arr = (XnatSlicerGlobals.DICOM_EXTENSIONS + 
               XnatSlicerGlobals.MRML_EXTENSIONS + 
               XnatSlicerGlobals.ALL_LOADABLE_EXTENSIONS + 
               XnatSlicerGlobals.SLICER_PACKAGE_EXTENSIONS)
        for item in arr:
            if ext == item:
                return True
            elif ext.find(item)>-1:
                return True            
        return False




    @staticmethod
    def isExtension(ext, extList):  
        """  
        Compares one stirng against
        a set of strings to see if there's a match.
        NOT case sensitive.
        
        @param ext: The extension to check.
        @type ext: string

        @param extList: The list to check the 'ext' argument against.
        @type extList: list of strings

        @return: Whether the filename belongs to the category.
        @rtype: boolean
        """    
        ext = "." + ext
        for val in extList:
            if ext.lower().endswith(val.lower()): 
                return True
        return False




    @staticmethod
    def isMiscLoadable( fileName = None):
        """ 
        Checks if the fileName's extension is part of
        XnatSlicerGlobals.MISC_LOADABLE_EXTENSIONS

        @param fileName: The file to check.
        @param fileName: string

        @return: Whether the filename belongs to the category.
        @rtype: boolean
        """
        return XnatSlicerUtils.isExtension(fileName, XnatSlicerGlobals.MISC_LOADABLE_EXTENSIONS)

    


    @staticmethod    
    def isDICOM(fileName = None):
        """ 
        Checks if the provided fileName is a DICOM.

        @param fileName: The file to check.
        @param fileName: string

        @return: Whether the filename belongs to the category.
        @rtype: boolean
        """
        fileNameExt = '.' + fileName.rsplit('.', 1)[1].lower()
        for extension in XnatSlicerGlobals.DICOM_EXTENSIONS:
            if extension.lower() in fileNameExt:
                return True
        return False




    @staticmethod
    def isAnalyze(fileName = None):
        """ 
        Checks if the provided fileName is a an Analyze file.

        @param fileName: The file to check.
        @param fileName: string    

        @return: Whether the filename belongs to the category.
        @rtype: boolean
        """
        return XnatSlicerUtils.isExtension(fileName, XnatSlicerGlobals.ANALYZE_EXTENSIONS)




    @staticmethod    
    def isMRML(fileName = None): 
        """ 
        Checks if the provided fileName is a MRML file.

        @param fileName: The file to check.
        @param fileName: string    

        @return: Whether the filename belongs to the category.
        @rtype: boolean
        """    
        return XnatSlicerUtils.isExtension(fileName, XnatSlicerGlobals.MRML_EXTENSIONS)



       
    @staticmethod       
    def isScenePackage( ext = None):
        """ 
        Checks if the provided fileName is a scene package.

        @param fileName: The file to check.
        @param fileName: string    

        @return: Whether the filename belongs to the category.
        @rtype: boolean
        """
        return XnatSlicerUtils.isExtension(ext, XnatSlicerGlobals.SLICER_PACKAGE_EXTENSIONS)
   



    @staticmethod    
    def doNotCache(fileName):
        """ 
        Determine if a file is not cachable.

        @param fileName: The file name to check against the XnatSlicerUtils.doNotCache list.
        @type fileName: string
        """

        fileName = "." + fileName
        for ext in XnatSlicerUtils.doNotCache:
            if fileName.endswith(ext):
                return True
        return False




    @staticmethod    
    def isDecompressible(fileName):
        """ 
        Determine if a file can be decompressed.

        @param fileName: The file name to check against the XnatSlicerGlobals.DECOMPRESSIBLE_EXTENSIONS list.
        @type fileName: string

        @return: Whether the file name meets the criteria.
        @type: string
        """
        for ext in XnatSlicerGlobals.DECOMPRESSIBLE_EXTENSIONS:
            if fileName.endswith(ext):
                return True
        return False




    @staticmethod    
    def getSaveTuple( fileUri = None):
        """ 
        Constructs a save URI based upon a provided
        fileUri by splitting it and then applying the default
        XNAT Slicer scene save locations specified in GLOB.py .
        
        @param fileUri: The file uri to derive the save tuple from.
        @type fileUri: string

        @returns: The save level uri (likely ends at 'experiments'), The specific uri where slicer files are located. 
        @rtypes: string, string 
        """
        saveLevelUri = None
        slicerSaveUri = None
        if fileUri:
            lSplit, rSplit = fileUri.split(XnatSlicerGlobals.DEFAULT_XNAT_SAVE_LEVEL + "/")
            saveLevelUri = (lSplit + XnatSlicerGlobals.DEFAULT_XNAT_SAVE_LEVEL + "/" + rSplit.split("/")[0])
            slicerSaveUri = saveLevelUri + "/resources/" + XnatSlicerGlobals.SLICER_FOLDER_NAME + "/files"
        return saveLevelUri, slicerSaveUri




    @staticmethod
    def repositionToMainSlicerWindow(positionable, location = "center"):
        """ 
        Repositions a widget window to the main slicer window relative
        to the "location" argument.

        @param positionable: The widget to reposition.
        @type positionable: qt.QWidget


        @param location: The location of the widget.
        @type location: string
        """

    
        #---------------------------
        # Get main window and its position.
        #---------------------------
        mainWindow = slicer.util.mainWindow()
        screenMainPos = mainWindow.pos


        
        #---------------------------
        # Derive coordinates
        #---------------------------
        location = location.lower().strip()
        if location == 'upperleftcorner':
            x = screenMainPos.x()
            y = screenMainPos.y()  
        #
        # If location = 'center'
        #
        else :
            x = screenMainPos.x() + mainWindow.width/2 - positionable.width/2
            y = screenMainPos.y() + mainWindow.height/2 - positionable.height/2
            
        positionable.move(qt.QPoint(x,y))




    @staticmethod
    def getXnatPathDict(xnatUri):
        """ 
        Splits apart the xnatUri into the various
        XNAT folder levels, this split as a dictionary.

        @param xnatUri: The file uri to derive path dictionary from.
        @type xnatUri: string

        @return: The XNAT path as a path dictionary.
        @rtype: dict
        """
        uriDict = Xnat.path.DEFAULT_PATH_DICT.copy()
        uriList = xnatUri.split("/")
        for i in range(0, len(uriList)):
            for k in uriDict:
                if uriList[i].strip() == k:
                    if (i+1) < len(uriList):
                        uriDict[uriList[i]] = uriList[i+1]
        return uriDict
    



    @staticmethod
    def generateButton(iconOrLabel="", toolTip="", 
                       font = qt.QFont('Arial', 10, 10, False),  
                       size = None, enabled=False):
        """ 
        Creates a qt.QPushButton(), with the arguments.  Sets text, font,
        toolTip, icon, size, and enabled state.

        @param iconOrLabel: Either the icon uri or the label of the button.   
            Defaults to ''.
        @type iconOrLabel: string

        @param toolTip: The tool tip of the button.  Defaults to ''.
        @type toolTip: string

        @param font: The font of the button.  Defaults to 'Arial, 10, plain.'
        @type font: qt.QFont

        @param size: The size of the button.  Defaults QT presets.
        @type size: qt.QSize

        @param enabled: The enabled state of the button.  Defaults to 'False'.
        @type enabled: boolean

        @return: The constructed button to return.
        @rtype: qt.QPushButton
        """
        
        button = qt.QPushButton()
        
        
        
        #--------------------
        # Set either Icon or label, depending on
        # whehter the icon file exists.
        #--------------------
        iconPath = os.path.join(XnatSlicerGlobals.LOCAL_URIS['icons'], 
                                iconOrLabel)
        if os.path.exists(iconPath):
            button.setIcon(qt.QIcon(iconPath))
        else:
            button.setText(iconOrLabel)

        
            button.setToolTip(toolTip)
            button.setFont(font)

        if size:
            button.setFixedHeight(size.height())
            button.setFixedWidth(size.width())

                
                
        button.setEnabled(enabled) 
        return button

    
        
    @staticmethod
    def makeDateReadable(dateString):
        """ 
        Convets XNAT date metadata to a more human readable string.

        @param dateString: The XNAT date metadata to convert.
        @type dateString: string

        @return: The converted XNAT date.
        @rtype: string
        """
      
        newDateString = dateString
        tempStr = str(dateString).strip().replace('\n', '')
        
        if len(tempStr) == 0:
            return ''

        try:
            d = datetime.datetime.strptime(tempStr, '%Y-%m-%d %H:%M:%S.%f')
            #day_string = d.strftime('%Y-%m-%d')
            day_string = d.strftime('%A %d, %B %Y')
            day_string = d.strftime('%c')
        except Exception, e:
            #print "Using default date string from server"#. (Error: %s)" %(e)
            day_string = dateString
        
        return day_string



    
    @staticmethod
    def toPlainText(text):
        """ 
        Converts a rich text string to plain text.

        @param text: The rich text string to convert.
        @type text: string

        @return: The plain text string.
        @rtype: string
        """
        doc = qt.QTextDocument()
        doc.setHtml(text)
        return doc.toPlainText()
        


    @staticmethod
    def makeCustomMetadataTag(xnatLevel): 
        """
        @param xnatLevel: The XNAT level to derive the custom metadata tag from.
        @type xnatLevel: string

        @return: The constructed custom metadata tag.
        @rtype: string
        """
        return XnatSlicerGlobals.CUSTOM_METADATA_SETTINGS_PREFIX + xnatLevel.lower()



