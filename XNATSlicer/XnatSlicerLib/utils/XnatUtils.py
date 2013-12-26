
from __future__ import with_statement
from __main__ import vtk, ctk, qt, slicer

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

from GLOB import *

from HoverButton import *





comment = """
XnatUtils is the class that owns many of the default 
directory strings and string manipulation efforts of the 
module.  It's a generic utility class with a variety of 
methods to serve a number of general purposes.  It contains
see

TODO : 
"""




class XnatUtils(object):


    @staticmethod
    def constructNecessaryModuleDirectories():
        """ As stated.
        """
        #---------------------
        # Make the module paths if they don't exist.
        #---------------------
        for key, val in GLOB_LOCAL_URIS.iteritems():
            if not os.path.exists(val):    
                os.makedirs(val)

    

    



    
    @property
    def osType():
        if slicer.app.os.lower() == "win":
            return "win"
        elif slicer.app.os.lower() == "darwin" or slicer.app.os.lower() == "macosx": 
            return "mac"
        elif slicer.app.os.lower() == "linux": 
            return "linux"
    

    
    
    @property
    def localizedMRMLExtension():
        return "-LOCALIZED"


    
    
    @property
    def referencedMRMLExtension():
        return ""



    
    @property
    def condensedMRMLExtension():
        return ""


    

    @property
    def defaultSceneName():
        return "SlicerScene_"


    
    
    @property
    def referenceDirName():
        return "reference/"


    
    
    @property
    def defaultPackageExtension():
        return ".mrb"



    
    @property
    def packageExtensions():
        return  [".zip", ".mrb"]



    
    @property
    def dicomDBBackupFN():
        return XnatUtils.adjustPathSlashes(os.path.join(XnatUtils.LOCAL_URIS['settings'], "slicerDICOMDBBackup.txt")) 


    @staticmethod
    def getMetadataTagsByLevel( xnatLevel):
        """ Returns the appropriate tag list by the given
            'xnatLevel' argument.
        """

        if 'projects' in xnatLevel:
            return GLOB_DEFAULT_XNAT_METADATA['projects']
        elif 'subjects' in xnatLevel:
            return GLOB_DEFAULT_XNAT_METADATA['subjects']
        elif 'experiments' in xnatLevel:
            return GLOB_DEFAULT_XNAT_METADATA['experiments']
        elif 'resources' in xnatLevel:
            return GLOB_DEFAULT_XNAT_METADATA['resources']  
        elif 'scans' in xnatLevel:
            return GLOB_DEFAULT_XNAT_METADATA['scans']
        elif 'files' in xnatLevel:
            return GLOB_DEFAULT_XNAT_METADATA['files']
        elif 'Slicer' in xnatLevel:
            return GLOB_DEFAULT_XNAT_METADATA['slicer']     
        

        
    @staticmethod
    def uniqify( seq):
        """ Returns only unique elements in a list, while 
            preserving order: O(1).
            From: http://www.peterbe.com/plog/uniqifiers-benchmark
        """
        seen = set()
        seen_add = seen.add
        return [ x for x in seq if x not in seen and not seen_add(x)]



        
    @staticmethod            
    def removeDirsAndFiles( path):
        """ Attempts multiple approaches (they vary from OS)
            to remove the files and directories of the path.
        """
        if os.path.exists(path):
            XnatUtils.removeDir(path)
        if os.path.exists(path):
            try:
                os.rmdir(path)
            except Exception, e:
                print XnatUtils.lf() + "%s Can't remove dir '%s'"%(str(e), path)


                
    @staticmethod            
    def appendFile( fileName, appendStr):
        """ Appends a string to a given filename by
            splitting at the '.' to preserve the extension.
        """
        name = os.path.splitext(fileName)[0]
        ext = os.path.splitext(fileName)[1]
        return name + appendStr + ext



    @staticmethod    
    def removeDir( path, pattern=''):
        """ Tries various approaches to remove a directory.
            (Approaches can vary by OS).
        """
        import re
        pattern = re.compile(pattern)
        if os.path.exists(path):
            for each in os.listdir(path):
                if pattern.search(each):
                    name = os.path.join(path, each)
                    try: 
                        os.remove(name)
                    except:
                        XnatUtils.removeDir(name, '')
                        try:
                            os.rmdir(name)
                        except Exception, e:
                            print XnatUtils.lf() + "%s Can't remove dir '%s'"%(str(e), name)
        else:
            print XnatUtils.lf() + " ATTEMPTED TO REMOVE: %s but it does not exist!"%(path)



    @staticmethod            
    def removeFilesInDir( theDir):
        """  Removes the files within a directory but not the 
             directory itXnatUtils.
        """
        for the_file in os.listdir(theDir):
            file_path = os.path.join(theDir, the_file)
            try:
                os.unlink(file_path)
                os.remove(file_path)
            except Exception, e:
                if the_file.endswith("\\") or the_file.endswith("/"): 
                    XnatUtils.removeFilesInDir(file_path)



    @staticmethod                    
    def shortenFileName( fn, maxLen = 20):
        """ Shortens a given filename to a length provided
            in the argument.  Appends the file with "..." string.
        """
        basename = os.path.basename(fn)
        pre = basename.split(".")[0]
        if len(pre) > maxLen:
             baseneme = pre[0:8] + "..." + pre[-8:] + "." + basename.split(".")[1]
        return basename


    
    @staticmethod    
    def removeFile( theFile):
        """ Attempts to a remove a file from disk.
        """
        try:           
            os.unlink(theFile)
            os.remove(theFile)
        except Exception, e:
            pass



    @staticmethod            
    def moveDirContents( srcDir, destDir, deleteSrc = True):
        """ Moves the contents of one directory to another.
        """
        
        newURIs = []


        
        #------------------
        # Make destination dir
        #------------------
        if not os.path.exists(destDir): 
            os.mkdir(destDir)

            
            
        #------------------
        # Walk through src path.     
        #------------------
        for root, subFolders, files in os.walk(srcDir):
            for file in files:
                #
                # Construct src folder, current uri, and dst uri
                #
                srcFolder = os.path.basename(srcDir)
                currURI = os.path.join(root,file)
                newURI = os.path.join(destDir, file)
                #
                # Clean up the newURI payh string.
                #
                try:
                    folderBegin = root.split(srcFolder)[-1] 
                    if folderBegin.startswith("\\"): 
                        folderBegin = folderBegin[1:] 
                    if folderBegin.startswith("/"): 
                        folderBegin = folderBegin[1:] 
                    #
                    # Make the new URIs of the sub directory.
                    #
                    if folderBegin and len(folderBegin) > 0:
                        newPath = os.path.join(destDir, folderBegin)
                        if not os.path.exists(newPath):
                            os.mkdir(newPath)
                        newURI = os.path.join(newPath, file)
                except Exception, e: 
                    print (XnatUtils.lf() + "RootSplit Error: " + str(e))
                #
                # Move the file, and track it             
                #
                shutil.move(currURI, newURI)
                newURIs.append(XnatUtils.adjustPathSlashes(newURI))

                 
                
        #------------------
        # If the src path is to be deleted...
        #------------------
        if deleteSrc:
            if not srcDir.find(destDir) == -1:
                XnatUtils.removeDirsAndFiles(srcDir)
        

        return newURIs



    @staticmethod    
    def writeZip( packageDir, deleteFolders = False):
        """ Writes a given path to a zip file based on the basename
            of the 'packageDir' argument.
            
           from: http://stackoverflow.com/questions/296499/how-do-i-zip-the-contents-of-a-folder-using-python-version-2-5
        """
        zipURI = packageDir + ".zip"
        assert os.path.isdir(packageDir)
        with closing(ZipFile(zipURI, "w", ZIP_DEFLATED)) as z:
            for root, dirs, files in os.walk(packageDir):
                for fn in files: #NOTE: ignore empty directories
                    absfn = os.path.join(root, fn)
                    zfn = absfn[len(packageDir)+len(os.sep):] #XXX: relative path
                    z.write(absfn, zfn)
        return zipURI




    @staticmethod            
    def checkStorageNodeDirs( currScene):
        """Determines if there's at least one storable node 
           with at least one filename associated with it. 
           Part of a series of functions to determine if a 
           Slicer scene is empty.
        """
        
        #------------------------
        # Get the storage nodes of volumes.
        #------------------------
        tempNode =  currScene.GetNodesByClass('vtkMRMLVolumeArchetypeStorageNode') # none GetItemAsObject(1)
        storageNode = None


        
        #------------------------
        # Cycle through nodes, identify 'vtkMRMLVolumeArchetypeStorageNode',
        # and select one of them.
        #------------------------
        for i in range(0,tempNode.GetNumberOfItems()):            
            if tempNode.GetItemAsObject(i).GetClassName() == 'vtkMRMLVolumeArchetypeStorageNode': 
                storageNode = tempNode.GetItemAsObject(i)
                break


            
        #------------------------
        # Get the filenames associated with the node.
        #------------------------
        fileNames = []
        try: 
            for i in range(0, storageNode.GetNumberOfFileNames()):
                fileNames.append(storageNode.GetNthFileName(i))
        except Exception, e:
            pass
        return fileNames



    @staticmethod    
    def writeDebugToFile( debugStr):
        """ Writes a string to a file for debugging purposes.
        """
        f = open(os.path.join(GLOB_LOCAL_URIS['home'], "DebugLog.txt"), 'a')
        f.write(str(datetime.datetime.now()) + ": " + debugStr + "\n")            
        f.close()



    @staticmethod        
    def isRecognizedFileExt( ext):
        """ Determine if an extension is a readable file
            by Slicer and/or XNATSlicer.
        """
        if len(ext) > 0 and ext[0] != '.':   ext = "." + ext
        arr = (GLOB_DICOM_EXTENSIONS + 
               GLOB_MRML_EXTENSIONS + 
               GLOB_ALL_LOADABLE_EXTENSIONS + 
               XnatUtils.packageExtensions)
        for item in arr:
            if ext == item:
                return True
            elif ext.find(item)>-1:
                return True            
        return False


    @staticmethod
    def isExtension( ext, extList):  
        """  Compares two strings to see if they match
             for extension matching.
        """    
        ext = "." + ext
        for val in extList:
            if ext.lower().endswith(val.lower()): 
                return True
        return False


    @staticmethod
    def isMiscLoadable( filename = None):
        """ As stated.
        """
        return XnatUtils.isExtension(filename, GLOB_MISC_LOADABLE_EXTENSIONS)

    
    @staticmethod    
    def isDICOM( filename = None):
        """ As stated.
        """
        filenameExt = '.' + filename.rsplit('.', 1)[1].lower()
        for extension in GLOB_DICOM_EXTENSIONS:
            if extension.lower() in filenameExt:
                return True
        return False


    @staticmethod
    def isAnalyze( ext = None):
        """ As stated.
        """
        return XnatUtils.isExtension(ext, GLOB_ANALYZE_EXTENSIONS)



    @staticmethod    
    def isMRML( ext = None): 
        """ As stated.
        """    
        return XnatUtils.isExtension(ext, GLOB_MRML_EXTENSIONS)


       
    @staticmethod       
    def isScenePackage( ext = None):
        """ Determins if a given extension is a Slicer scene
            package.
        """
        return XnatUtils.isExtension(ext, XnatUtils.packageExtensions)
   
    

    @staticmethod    
    def getAncestorUri( remotePath, ancestorName = None):
        """ Returns an ancestor path based on the provided level.
        """ 
        
        #---------------------
        # Convert the path to a URL to avoid slash errors.
        #---------------------
        remotePath = os.path.dirname(qt.QUrl(remotePath).path())



        #---------------------
        # Split the path by the forward slashes.
        #---------------------
        pathLayers = remotePath.rsplit("/")        
        parentPath = ""
        for pathLayer in pathLayers:
            if pathLayer == ancestorName:
                break
            parentPath += pathLayer + "/"
        return parentPath



    @staticmethod    
    def isCurrSceneEmpty():
        """Determines if the scene is empty based on 
           the visible node count.
        """
        
        #------------------------
        # Construct path parameters.
        #------------------------
        visibleNodes = []    
        origScene = slicer.app.applicationLogic().GetMRMLScene()
        origURL = origScene.GetURL()
        origRootDirectory = origScene.GetRootDirectory()


        
        #------------------------
        # Cycle through nodes to get the visible ones.
        #------------------------
        for i in range(0, origScene.GetNumberOfNodes()):
            mrmlNode = origScene.GetNthNode(i);
            if mrmlNode:
                try:
                    #
                    # Get visible nodes
                    #
                    if (str(mrmlNode.GetVisibility()) == "1" ):
                        #print "The %sth node of the scene is visible: %s"%(str(i), mrmlNode.GetClassName())
                        visibleNodes.append(mrmlNode)
                except Exception, e:
                    pass

                
             
        #------------------------
        # Return true if there are no visible nodes.
        #------------------------
        #print "NUMBER OF VISIBLE NODES: %s"%(str(len(visibleNodes)))   
        if (len(visibleNodes) == 1) and (visibleNodes[0].GetClassName() == "vtkMRMLViewNode"):
            return True
        elif (len(visibleNodes) < 1):
            return True
        
        return False



    @staticmethod    
    def doNotCache( filename):
        """ Determine if a file is not cachable.
        """
        for ext in XnatUtils.doNotCache:
            if filename.endswith(ext):
                return True
        return False



    @staticmethod    
    def isDecompressible( filename):
        """ Determine if a file can be decompressed.
        """
        for ext in GLOB_DECOMPRESSIBLE_EXTENSIONS:
            if filename.endswith(ext):
                return True
        return False



    @staticmethod    
    def decompressFile( filename, dest = None):
        """  Various methods to decompress a given file
             based on the file extension.  
        """
        if filename.endswith(".zip"):
            import zipfile
            z = zipfile.ZipFile(filename)      
            if not dest: dest = os.path.dirname(filename)
            z.extractall(dest)
        elif filename.endswith(".gz"):
            import gzip 
            a = gzip.GzipFile(filename, 'rb')
            content = a.read()
            a.close()                                          
            f = open(filename.split(".gz")[0], 'wb')
            f.write(content) 
            f.close()



    @staticmethod    
    def getCurrImageNodes( packageDir = None):
        """
        """
        
        #------------------------
        # Get curr scene and its nodes.
        #------------------------
        currScene = slicer.app.mrmlScene()
        ini_nodeList = currScene.GetNodes()


        
        #------------------------
        # Parameters
        #------------------------
        unmodifiedImageNodes = []
        modifiedImageNodes = []
        allImageNodes = []


        
        #------------------------
        # If no directory is provided...
        #------------------------
        if not packageDir:
            #
            # Cycle through nodes...
            #
            for x in range(0,ini_nodeList.GetNumberOfItems()):
                nodeFN = None
                node = ini_nodeList.GetItemAsObject(x)
                try:              
                      #
                      # See if node has a filename.
                      #
                      nodeFN = node.GetFileName()
                except Exception, e:
                      pass 
                #
                # If there is a filename, get its extension.              
                #
                if nodeFN:
                    nodeExt = '.' + nodeFN.split(".", 1)[1]                      


                    
        #------------------------
        # Determine if there are any modified image nodes.
        #------------------------
        for _node in allImageNodes:
            if  unmodifiedImageNodes.count(_node) == 0:
                modifiedImageNodes.append(_node)   

                
        return unmodifiedImageNodes, modifiedImageNodes, allImageNodes



    @staticmethod    
    def getDateTimeStr():
        """ As stated.
        """
        strList = str(datetime.datetime.today()).rsplit(" ")
        timeStr = strList[1]
        timeStr = timeStr.replace(":", " ")
        timeStr = timeStr.replace(".", " ")
        timeList = timeStr.rsplit(" ")
        shortTime = timeList[0]+ "-" + timeList[1]
        return strList[0] + "_" + shortTime



    @staticmethod   
    def createSceneName():   
        """ For creating scene names if none is provided by the 
            user.
        """
        strList = str(datetime.datetime.today()).rsplit(" ")
        timeStr = strList[1]
        timeStr = timeStr.replace(":", " ")
        timeStr = timeStr.replace(".", " ")
        timeList = timeStr.rsplit(" ")
        shortTime = timeList[0]+ "-" + timeList[1]
        tempFilename = XnatUtils.defaultSceneName + XnatUtils.getDateTimeStr()
        return tempFilename


    
    @staticmethod    
    def adjustPathSlashes( str):
        """  Replaces '\\' path
        """
        return str.replace("\\", "/").replace("//", "/")


    
    @staticmethod    
    def replaceForbiddenChars( fn, replaceStr=None):
        """ As stated.
        """
        if not replaceStr: replaceStr = "_"
        fn = fn.replace(".", replaceStr)
        fn = fn.replace("/", replaceStr)
        fn = fn.replace("\\", replaceStr)
        fn = fn.replace(":", replaceStr)
        fn = fn.replace("*", replaceStr)
        fn = fn.replace("?", replaceStr)
        fn = fn.replace("\"", replaceStr)
        fn = fn.replace("<", replaceStr)
        fn = fn.replace(">", replaceStr)
        fn = fn.replace("|", replaceStr)
        return fn


    
    @staticmethod    
    def constructSlicerSaveUri( currUri, xnatLevel = None):
        """ Constructs a Slicer save URI (on the XNAT host) based on the provided 
            arguments of currUri and the optional arguments of xnatLevel and findNearest.  
            If xnatLevel is left as 'None', the Slicers save URI will be constructed based upon
            the 'GLOB_DEFAULT_XNAT_SAVE_LEVEL' value.
        """

        #-----------------------
        # Set the default XNAT save level if 'xnatLevel' is 
        # none (i.e. not entered by user.)
        #------------------------
        if (not xnatLevel):
            xnatLevel = GLOB_DEFAULT_XNAT_SAVE_LEVEL


            
        #------------------------
        # Initial parameters.
        #------------------------
        slicerSaveUri = ""
        counter = 0


                
        #------------------------
        # Build the URI and stop at xnatLevel.  
        # This will be the start point
        # for the Slicer path.
        #------------------------
        uriElements = currUri.split("/")
        for uriElement in uriElements:
            if len(uriElement) > 0:
                slicerSaveUri += uriElement + "/"
                if uriElement == xnatLevel:
                    slicerSaveUri += uriElements[counter+1]
                    break
            counter+=1   


                
        #------------------------
        # Append the 'slicerSaveUri' parameter with
        # the necessary strings.
        #------------------------
        if not slicerSaveUri.endswith("/"):
            slicerSaveUri+="/"    
        slicerSaveUri += "resources/%s/files/"%(GLOB_SLICER_FOLDER_NAME) 

        return slicerSaveUri



    @staticmethod    
    def lf( msg=""):
        """For debugging purposes.  Returns the current line number and function
           when used throughout the module.
        """

        #---------------------------
        # Acquire the necessary parameters from
        # where the function is called.
        #---------------------------
        frame, filename, line_number, function_name, lines, index = inspect.getouterframes(inspect.currentframe())[1]
        returnStr = "\n"
        try:
            #
            # Construct a string based on the 
            # above parameters.
            #
            returnStr = "%s (%s) %s: %s"%(os.path.basename(filename), function_name, line_number, msg)
        except Exception, e:
            print "Line Print Error: " + str(e)
        return "\n" + returnStr



    @staticmethod    
    def removeZeroLenStrVals( _list):
        """ As stated.  Removes any string values with 
            zero length within a list.
        """
        for listItem in _list: 
            if (len(listItem)==0):
                _list.remove(listItem)
        
        return _list



    @staticmethod    
    def getSaveTuple( filepath = None):
        """ Constructs a save URI based upon a provided
            filePath by splitting it and then applying the default
            locations specified in this cass.
        """
        saveLevelDir = None
        slicerDir = None
        if filepath:
            lSplit, rSplit = filepath.split(GLOB_DEFAULT_XNAT_SAVE_LEVEL + "/")
            saveLevelDir = (lSplit + GLOB_DEFAULT_XNAT_SAVE_LEVEL + "/" + rSplit.split("/")[0])
            slicerDir = saveLevelDir + "/resources/" + GLOB_SLICER_FOLDER_NAME + "/files"
        return saveLevelDir, slicerDir



    
    @staticmethod
    def bytesToMB( bytes):
        """ Converts bytes to MB.  Returns a float.
        """
        bytes = int(bytes)
        mb = str(bytes/(1024*1024.0)).split(".")[0] + "." + str(bytes/(1024*1024.0)).split(".")[1][:2]
        return float(mb)



    @staticmethod
    def repositionToMainSlicerWindow( positionable, location = "center"):
        """ As stated.  User can provide location of window
            within the arguments.
        """

        #---------------------------
        # Make sure positionable is open.
        #---------------------------
        positionable.show()



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
    def getXnatPathDict( xnatUri):
        """ Splits apart the 'path' into the various
            XNAT folder levels, then returns it as a dictionary.
        """
        uriDict = GLOB_DEFAULT_PATH_DICT.copy()
        uriList = xnatUri.split("/")
        for i in range(0, len(uriList)):
            for k in uriDict:
                if uriList[i].strip() == k:
                    if (i+1) < len(uriList):
                        uriDict[uriList[i]] = uriList[i+1]
        return uriDict
    



    @staticmethod
    def generateButton(iconOrLabel="", toolTip="", font = qt.QFont('Arial', 10, 10, False),  size = None, enabled=False):
        """ Creates a qt.QPushButton(), with the arguments.  Sets text, font,
        toolTip, icon, size, and enabled state.
        """
        
        button = qt.QPushButton()
        
        
        
        #--------------------
        # Set either Icon or label, depending on
        # whehter the icon file exists.
        #--------------------
        iconPath = os.path.join(GLOB_LOCAL_URIS['icons'], iconOrLabel)
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
    def makeSettingsButton( XnatSetting):
        """ Constructs a setting button with a wrench icon that
            opens the appropriate settings tab.
        """
        button = HoverButton()
        button.setIcon(qt.QIcon(os.path.join(GLOB_LOCAL_URIS['icons'], 'wrench.png')) )
        button.setFixedWidth(23)
        button.setFixedHeight(17)
        button.setDefaultStyleSheet('border: 1px solid transparent; border-radius: 2px; background-color: transparent; margin-left: 5px; text-align: left; padding-left: 0px; ')
        button.setHoverStyleSheet('border: 1px solid rgb(150,150,150); border-radius: 2px; background-color: transparent; margin-left: 5px; text-align: left; padding-left: 0px;')
        def openSettings():
            XnatUtils.MODULE.XnatSettingsWindow.showWindow(XnatSetting.tabTitle)
        button.connect('clicked()', openSettings)
        return button



    @staticmethod
    def makeDisplayableFileName( fileUri):
        """ Makes a filename displayable but culling
            a lot of the unnecessary file path characters.
        """
        fileUri = '/experiments' + fileUri.split('experiments')[1]

        if '?' in fileUri:
            return fileUri.split('?')[0]
        return fileUri

    
        
    @staticmethod
    def makeDateReadable( dateString):
        """ Xnat Date metadata is generally long and not
            very human readable.  This converts it.
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
            print "Using default date string from server"#. (Error: %s)" %(e)
            day_string = dateString
        
        return day_string


    
    @staticmethod
    def toPlainText( text):
        """ Converts a string to plain text.
        """
        doc = qt.QTextDocument()
        doc.setHtml(text)
        return doc.toPlainText()
        

    @staticmethod
    def loadNodeFromFile( fileName):
        """
        """
        coreIOManager = slicer.app.coreIOManager()
        fileType = coreIOManager.fileType(fileName)
        fileSuccessfullyLoaded = slicer.util.loadNodeFromFile(fileName, fileType)            
        if not fileSuccessfullyLoaded:
            errStr = "Could not load '%s'!"%(fileName)
            print (errStr)

            

    @staticmethod      
    def filterFiles( fileArr, filterFunction):
        """
        """
        newExtractedFiles = []
        for fileName in fileArr:
            if filterFunction(fileName):
                newExtractedFiles.append(fileName)
        return newExtractedFiles



    @staticmethod
    def sortLoadablesByType( fileNames):
        """
        """
        
        filesByType = {
            'analyze': [],
            'dicom': [],
            'misc': [],
            'unknown': []
        }

        for fileName in fileNames:
            if XnatUtils.isAnalyze(fileName):
                filesByType['analyze'].append(fileName)
            elif XnatUtils.isDICOM(fileName):
                filesByType['dicom'].append(fileName)
            elif XnatUtils.isMiscLoadable(fileName):
                filesByType['misc'].append(fileName)
            else:
                filesByType['unknown'].append(fileName)

        return filesByType


    @staticmethod
    def makeCustomMetadataTag(xnatLevel): 
        """
        """
        return GLOB_CUSTOM_METADATA_SETTINGS_PREFIX + xnatLevel.lower()



