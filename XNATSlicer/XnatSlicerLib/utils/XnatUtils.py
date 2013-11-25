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
    
    def __init__(self, MODULE):
        self.MODULE = MODULE   
        pass


        
    def constructNecessaryModuleDirectories(self):
        """ As stated.
        """

        
        #---------------------
        # Make the module paths if they don't exist.
        #---------------------
        for key, val in self.MODULE.GLOBALS.LOCAL_URIS.iteritems():
            if not os.path.exists(val):    
                os.makedirs(val)

    

    
    @property
    def xnatDepthDict(self):
        return {0:"projects",
                1:"subjects",
                2:"experiments",
                3:"scans"}


    
    @property
    def osType(self):
        if slicer.app.os.lower() == "win":
            return "win"
        elif slicer.app.os.lower() == "darwin" or slicer.app.os.lower() == "macosx": 
            return "mac"
        elif slicer.app.os.lower() == "linux": 
            return "linux"
    

    
    
    @property
    def localizedMRMLExtension(self):
        return "-LOCALIZED"


    
    
    @property
    def referencedMRMLExtension(self):
        return ""



    
    @property
    def condensedMRMLExtension(self):
        return ""


    

    @property
    def defaultSceneName(self):
        return "SlicerScene_"


    
    
    @property
    def referenceDirName(self):
        return "reference/"


    
    
    @property
    def slicerFolderName(self):
        return "Slicer"



    
    @property
    def defaultXnatSaveLevel(self):
        return "experiments"


    
    
    @property
    def requiredSlicerFolders(self):
        return [self.slicerFolderName]

    
    
    @property
    def defaultPackageExtension(self):
        return ".mrb"



    
    @property
    def packageExtensions(self):
        return  [".zip", ".mrb"]



    
    @property
    def dicomDBBackupFN(self):
        return self.adjustPathSlashes(os.path.join(self.LOCAL_URIS['settings'], "slicerDICOMDBBackup.txt")) 




    @property
    def XnatMetadataTags_projects(self):
        return ['secondary_ID',
                'pi_lastname',
                'pi_firstname',
                'description',
                'name',
                'ID',
                'URI',
                # The reason for two ID keys is because the "?accessible=True" filter
                # returns lowercase 'id'
                'id',	
                'pi',	
                'project_invs',	
                'project_access_img',	
                'insert_date',
                'insert_user',	
                'user_role_497',	
                'last_accessed_497',	
                'quarantine_status'
                ]



    
    @property
    def XnatMetadataTags_subjects(self):
        return ['project',
                'insert_user',
                'ID',
                'insert_date',
                'label',
                'URI',
                'totalRecords'
                ]


    

    @property
    def XnatMetadataTags_experiments(self):
        return ['project',
                'xsiType',
                'ID',
                'insert_date',
                'label',
                'date',
                'URI',
                'totalRecords'
                ]



    
    @property
    def XnatMetadataTags_resources(self):
        return ['cat_id',
                'element_name',
                'category',
                'xnat_abstractresource_id',
                'label',
                'cat_desc',
                ]


    

    @property
    def XnatMetadataTags_scans(self):
        return ['xsiType',
                'quality',
                'series_description',
                'xnat_imagescandata_id',
                'URI',
                'note',
                'type',
                'ID'
                ]

    

    
    @property
    def XnatMetadataTags_files(self):
        return ['Name', 
                'file_content',
                'collection',
                'file_format',
                'file_tags',
                'cat_ID',
                'URI',
                'Size'
                ]


    
    
    @property
    def XnatMetadataTags_all(self):
        return self.uniqify(self.XnatMetadataTags_projects + 
                                self.XnatMetadataTags_subjects + 
                                self.XnatMetadataTags_experiments + 
                                self.XnatMetadataTags_resources + 
                                self.XnatMetadataTags_scans + 
                                self.XnatMetadataTags_files)




    def getMetadataTagsByXnatLevel(self, xnatLevel):
        """ Returns the appropriate tag list by the given
            'xnatLevel' argument.
        """

        if 'projects' in xnatLevel:
            return self.XnatMetadataTags_projects
        elif 'subjects' in xnatLevel:
            return self.XnatMetadataTags_subjects
        elif 'experiments' in xnatLevel:
            return self.XnatMetadataTags_experiments
        elif 'resources' in xnatLevel:
            return self.XnatMetadataTags_resources   
        elif 'scans' in xnatLevel:
            return self.XnatMetadataTags_scans
        elif 'files' in xnatLevel:
            return self.XnatMetadataTags_files
        elif 'Slicer' in xnatLevel:
            return self.XnatMetadataTags_files     

        

    def uniqify(self, seq):
        """ Returns only unique elements in a list, while 
            preserving order: O(1).
            From: http://www.peterbe.com/plog/uniqifiers-benchmark
        """
        seen = set()
        seen_add = seen.add
        return [ x for x in seq if x not in seen and not seen_add(x)]


    

    def XnatMetadataTagsByLevel(self, level):
        """ Returns the relevant XNAT metadata dags that the 
            XNAT server returns when looking at the contents of a 
            given XNAT level at provided by the 'level' argument.
        """
        if level == 'projects': return self.XnatMetadataTags_projects
        elif level == 'subjects' : return self.XnatMetadataTags_subjects
        elif level == 'experiments' : return self.XnatMetadataTags_experiments
        elif level == 'scans' : return self.XnatMetadataTags_scans
        elif level == 'resources' : return self.XnatMetadataTags_resources
        elif level == 'files' : return self.XnatMetadataTags_files


        
            
    def removeDirsAndFiles(self, path):
        """ Attempts multiple approaches (they vary from OS)
            to remove the files and directories of the path.
        """
        if os.path.exists(path):
            self.removeDir(path)
        if os.path.exists(path):
            try:
                os.rmdir(path)
            except Exception, e:
                print self.lf() + "%s Can't remove dir '%s'"%(str(e), path)


                
            
    def appendFile(self, fileName, appendStr):
        """ Appends a string to a given filename by
            splitting at the '.' to preserve the extension.
        """
        name = os.path.splitext(fileName)[0]
        ext = os.path.splitext(fileName)[1]
        return name + appendStr + ext



    
    def removeDir(self, path, pattern=''):
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
                        self.removeDir(name, '')
                        try:
                            os.rmdir(name)
                        except Exception, e:
                            print self.lf() + "%s Can't remove dir '%s'"%(str(e), name)
        else:
            print self.lf() + " ATTEMPTED TO REMOVE: %s but it does not exist!"%(path)



            
    def removeFilesInDir(self, theDir):
        """  Removes the files within a directory but not the 
             directory itself.
        """
        for the_file in os.listdir(theDir):
            file_path = os.path.join(theDir, the_file)
            try:
                os.unlink(file_path)
                os.remove(file_path)
            except Exception, e:
                if the_file.endswith("\\") or the_file.endswith("/"): 
                    self.removeFilesInDir(file_path)



                    
    def shortenFileName(self, fn, maxLen = 20):
        """ Shortens a given filename to a length provided
            in the argument.  Appends the file with "..." string.
        """
        basename = os.path.basename(fn)
        pre = basename.split(".")[0]
        if len(pre) > maxLen:
             baseneme = pre[0:8] + "..." + pre[-8:] + "." + basename.split(".")[1]
        return basename


    
    
    def removeFile(self, theFile):
        """ Attempts to a remove a file from disk.
        """
        try:           
            os.unlink(theFile)
            os.remove(theFile)
        except Exception, e:
            pass



            
    def moveDirContents(self, srcDir, destDir, deleteSrc = True):
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
                    print (self.lf() + "RootSplit Error: " + str(e))
                #
                # Move the file, and track it             
                #
                shutil.move(currURI, newURI)
                newURIs.append(self.adjustPathSlashes(newURI))

                 
                
        #------------------
        # If the src path is to be deleted...
        #------------------
        if deleteSrc:
            if not srcDir.find(destDir) == -1:
                self.removeDirsAndFiles(srcDir)
        

        return newURIs



    
    def writeZip(self, packageDir, deleteFolders = False):
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




            
    def checkStorageNodeDirs(self, currScene):
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



    
    def writeDebugToFile(self, debugStr):
        """ Writes a string to a file for debugging purposes.
        """
        f = open(os.path.join(self.MODULE.GLOBALS.LOCAL_URIS['home'], "DebugLog.txt"), 'a')
        f.write(str(datetime.datetime.now()) + ": " + debugStr + "\n")            
        f.close()



        
    def isRecognizedFileExt(self, ext):
        """ Determine if an extension is a readable file
            by Slicer and/or XNATSlicer.
        """
        if len(ext) > 0 and ext[0] != '.':   ext = "." + ext
        arr = (self.MODULE.GLOBALS.DICOM_EXTENSIONS + 
               self.MODULE.GLOBALS.MRML_EXTENSIONS + 
               self.MODULE.GLOBALS.ALL_LOADABLE_EXTENSIONS + 
               self.packageExtensions)
        for item in arr:
            if ext == item:
                return True
            elif ext.find(item)>-1:
                return True            
        return False



    def isExtension(self, ext, extList):  
        """  Compares two strings to see if they match
             for extension matching.
        """    
        ext = "." + ext
        for val in extList:
            if ext.lower().endswith(val.lower()): 
                return True
        return False



    
    def isDICOM(self, ext = None):
        """ As stated.
        """
        return self.isExtension(ext, self.MODULE.GLOBALS.DICOM_EXTENSIONS)



    def isAnalyze(self, ext = None):
        """ As stated.
        """
        return self.isExtension(ext, self.MODULE.GLOBALS.ANALYZE_EXTENSIONS)



    
    def isMRML(self, ext = None): 
        """ As stated.
        """    
        return self.isExtension(ext, self.MODULE.GLOBALS.MRML_EXTENSIONS)


       
       
    def isScenePackage(self, ext = None):
        """ Determins if a given extension is a Slicer scene
            package.
        """
        return self.isExtension(ext, self.packageExtensions)
   
    

    
    def getAncestorUri(self, remotePath, ancestorName = None):
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



    
    def isCurrSceneEmpty(self):
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



    
    def doNotCache(self, filename):
        """ Determine if a file is not cachable.
        """
        for ext in self.doNotCache:
            if filename.endswith(ext):
                return True
        return False



    
    def isDecompressible(self, filename):
        """ Determine if a file can be decompressed.
        """
        for ext in self.MODULE.GLOBALS.DECOMPRESSIBLE_EXTENSIONS:
            if filename.endswith(ext):
                return True
        return False



    
    def decompressFile(self, filename, dest = None):
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



    
    def getCurrImageNodes(self, packageDir = None):
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



    
    def getDateTimeStr(self):
        """ As stated.
        """
        strList = str(datetime.datetime.today()).rsplit(" ")
        timeStr = strList[1]
        timeStr = timeStr.replace(":", " ")
        timeStr = timeStr.replace(".", " ")
        timeList = timeStr.rsplit(" ")
        shortTime = timeList[0]+ "-" + timeList[1]
        return strList[0] + "_" + shortTime



    
    def createSceneName(self):   
        """ For creating scene names if none is provided by the 
            user.
        """
        strList = str(datetime.datetime.today()).rsplit(" ")
        timeStr = strList[1]
        timeStr = timeStr.replace(":", " ")
        timeStr = timeStr.replace(".", " ")
        timeList = timeStr.rsplit(" ")
        shortTime = timeList[0]+ "-" + timeList[1]
        tempFilename = self.defaultSceneName + self.getDateTimeStr()
        return tempFilename


    
    
    def adjustPathSlashes(self, str):
        """  Replaces '\\' path
        """
        return str.replace("\\", "/").replace("//", "/")


    
    
    def replaceForbiddenChars(self, fn, replaceStr=None):
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


    
    
    def constructSlicerSaveUri(self, currUri, xnatLevel = None):
        """ Constructs a Slicer save URI (on the XNAT host) based on the provided 
            arguments of currUri and the optional arguments of xnatLevel and findNearest.  
            If xnatLevel is left as 'None', the Slicers save URI will be constructed based upon
            the 'self.defaultXnatSaveLevel' value.
        """

        #-----------------------
        # Set the default XNAT save level if 'xnatLevel' is 
        # none (i.e. not entered by user.)
        #------------------------
        if (not xnatLevel):
            xnatLevel = self.defaultXnatSaveLevel


            
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
        slicerSaveUri += "resources/%s/files/"%(self.slicerFolderName) 

        return slicerSaveUri



    
    def lf(self, msg=""):
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



    
    def removeZeroLenStrVals(self, _list):
        """ As stated.  Removes any string values with 
            zero length within a list.
        """
        for listItem in _list: 
            if (len(listItem)==0):
                _list.remove(listItem)
        
        return _list



    
    def getSaveTuple(self, filepath = None):
        """ Constructs a save URI based upon a provided
            filePath by splitting it and then applying the default
            locations specified in this cass.
        """
        saveLevelDir = None
        slicerDir = None
        if filepath:
            lSplit, rSplit = filepath.split(self.defaultXnatSaveLevel + "/")
            saveLevelDir = (lSplit + self.defaultXnatSaveLevel + "/" + rSplit.split("/")[0])
            slicerDir = saveLevelDir + "/resources/" + self.slicerFolderName + "/files"
        return saveLevelDir, slicerDir



    

    def bytesToMB(self, bytes):
        """ Converts bytes to MB.  Returns a float.
        """
        bytes = int(bytes)
        mb = str(bytes/(1024*1024.0)).split(".")[0] + "." + str(bytes/(1024*1024.0)).split(".")[1][:2]
        return float(mb)




    def repositionToMainSlicerWindow(self, positionable, location = "center"):
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




    def makeXnatUriDictionary(self, xnatUri):
        """ Splits apart the 'path' into the various
            XNAT folder levels, then returns it as a dictionary.
        """
        uriDict = {"projects":None, "subjects":None, "experiments":None, "scans":None, "resources":None, "files":None}
        uriList = xnatUri.split("/")
        for i in range(0, len(uriList)):
            for k in uriDict:
                if uriList[i].strip() == k:
                    if (i+1) < len(uriList):
                        uriDict[uriList[i]] = uriList[i+1]
        return uriDict




    def generateButton(self, iconOrLabel="", toolTip="", font = qt.QFont('Arial', 10, 10, False),  size = None, enabled=False):
        """ Creates a qt.QPushButton(), with the arguments.  Sets text, font,
        toolTip, icon, size, and enabled state.
        """
        
        button = qt.QPushButton()
        
        
        
        #--------------------
        # Set either Icon or label, depending on
        # whehter the icon file exists.
        #--------------------
        iconPath = os.path.join(self.MODULE.GLOBALS.LOCAL_URIS['icons'], iconOrLabel)
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




    def makeSettingsButton(self, XnatSetting):
        """ Constructs a setting button with a wrench icon that
            opens the appropriate settings tab.
        """
        button = HoverButton()
        button.setIcon(qt.QIcon(os.path.join(self.MODULE.GLOBALS.LOCAL_URIS['icons'], 'wrench.png')) )
        button.setFixedWidth(23)
        button.setFixedHeight(17)
        button.setDefaultStyleSheet('border: 1px solid transparent; border-radius: 2px; background-color: transparent; margin-left: 5px; text-align: left; padding-left: 0px; ')
        button.setHoverStyleSheet('border: 1px solid rgb(150,150,150); border-radius: 2px; background-color: transparent; margin-left: 5px; text-align: left; padding-left: 0px;')
        def openSettings():
            self.MODULE.XnatSettingsWindow.showWindow(XnatSetting.tabTitle)
        button.connect('clicked()', openSettings)
        return button




    def makeDisplayableFileName(self, fileUri):
        """ Makes a filename displayable but culling
            a lot of the unnecessary file path characters.
        """
        fileUri = '/experiments' + fileUri.split('experiments')[1]

        if '?' in fileUri:
            return fileUri.split('?')[0]
        return fileUri

    
        
    
    def makeDateReadable(self, dateString):
        """ Xnat Date metadata is generally long and not
            very human readable.  This converts it.
        """
      
        newDateString = dateString
        tempStr = str(dateString).strip().replace('\n', '')
        
        if len(tempStr) == 0:
            return ''
            
        d = datetime.datetime.strptime(tempStr, '%Y-%m-%d %H:%M:%S.%f')
        #day_string = d.strftime('%Y-%m-%d')
        day_string = d.strftime('%A %d, %B %Y')
        day_string = d.strftime('%c')
        return day_string


    

    def toPlainText(self, text):
        """ Converts a string to plain text.
        """
        doc = qt.QTextDocument()
        doc.setHtml(text)
        return doc.toPlainText()
        
