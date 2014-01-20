# python
from __future__ import with_statement
import os
import xml.etree.ElementTree as ET
import codecs
import shutil

# application
from __main__ import slicer




class SlicerUtils(object):
    """
    """

    @staticmethod
    def loadNodeFromFile(fileUri):
        """ 
        Load a given file as a node into Slicer, first by 
        calling on slicer.app.coreIOManager.fileType to 
        determine the file's type, then by calling on 
        slicer.util.loadNodeFromFile.

        @param fileUri: The file to load.
        @type fileUri: string
        """
        coreIOManager = slicer.app.coreIOManager()
        fileType = coreIOManager.fileType(fileUri)
        fileSuccessfullyLoaded = slicer.util.loadNodeFromFile(fileUri, fileType)            
        if not fileSuccessfullyLoaded:
            errStr = "Could not load '%s'!"%(fileUri)
            print (errStr)




    @staticmethod    
    def isCurrSceneEmpty():
        """
        Determines if the scene is empty based on 
        the visible node count.

        @return: Whether the currently loaded scene is empty.
        @rtype: boolean
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
                        ##print "The %sth node of the scene is visible: %s"%(str(i), mrmlNode.GetClassName())
                        visibleNodes.append(mrmlNode)
                except Exception, e:
                    pass

                
             
        #------------------------
        # Return true if there are no visible nodes.
        #------------------------
        ##print "NUMBER OF VISIBLE NODES: %s"%(str(len(visibleNodes)))   
        if (len(visibleNodes) == 1) and (visibleNodes[0].GetClassName() == "vtkMRMLViewNode"):
            return True
        elif (len(visibleNodes) < 1):
            return True
        
        return False


    
    @staticmethod    
    def getCurrImageNodes():
        """
        Returns the image nodes int the currently loaded Slicer scene.

        @returns: Unmodified image nodes, modified image nodes, all image nodes.
        @todo: Determine what class the nodes belong to.
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
        # Cycle through nodes...
        #------------------------
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
    def showDicomDetailsPopup():
        """
        As stated.
        """
        from DICOM import DICOMWidget
        p = DICOMWidget()
        p.parent.hide()
        p.detailsPopup.open()        




    class MrmlParser(object):
        """ 
        MrmlParser handles the parsing of a MRML file (XML-based) and 
        either changes the paths of the remotely linked files to local 
        directories, or to relative directories.
        """


        @staticmethod
        def changeValues(filename, newFilename, replaceValues, 
                         otherReplaceValues, removeOriginalFile = False, 
                         debug = True):
            """ 
            Changes the string values within a given file
            based on a provided lists 'replaceValues' and 'otherReplaceValues'.
            """


            ##print (MokaUtils.debug.lf(), "Changing values in the mrml.") 
            dicoms = []
            compLines = []


            #------------------------
            # Concatenate all replace values to a list
            #------------------------
            if otherReplaceValues:
                replaceValues.update(otherReplaceValues)



            #------------------------
            # Create new mrml, backup old
            #------------------------
            if filename == newFilename:
                bkpFN = filename.split(".")[0] + ".BKP"
                shutil.copy(filename,bkpFN)
                os.remove(filename)
                slicer.app.processEvents()
                filename = bkpFN



            #------------------------
            # Init xml parser
            #------------------------
            
            mrmlFile = codecs.open(filename, encoding="UTF-8", errors='ignore')
            mrmlText = mrmlFile.read()
            elementTree = ET.ElementTree(ET.fromstring(mrmlText))
            root = elementTree.getroot()
            iterator = root.getiterator()



            #------------------------
            # Loop through element tree, replace strings accordingly
            #------------------------
            for subelement in iterator:
                if subelement.keys():
                    for name, value in subelement.items():
                        #
                        # If no strings to be changed, at least make 
                        # sure filepaths are relative
                        #
                        if replaceValues == {}:
                            if os.path.basename(os.path.dirname(value)).lower() == "data":
                                ##print MokaUtils.debug.lf() + " CHANGING NAME WITH DATA FORMAT: 
                                # %s\tOLD: %s\tNEW:%s"%(subelement.attrib[name], value, "./Data/" + os.path.basename(value))
                                subelement.attrib[name] = "./Data/%s"%(os.path.basename(value))



            #------------------------
            # write new mrml
            #------------------------
            elementTree.write(newFilename)     
            #root.write(newFilename)     


            ### For testing purposes #############################################################
            #if self.TESTWRITE:
            #    z = open(filename,"r")
            #    oldlines = z.readlines()
            #    z.close()
            #    self.makeMrmlReadable(str(newFilename).split(".")[0]+"BEFORE", oldlines)
            #    self.makeMrmlReadable(str(newFilename).split(".")[0]+"AFTER", lines)      
            ######################################################################################



            #------------------------
            # return the dicom files, if necessary
            #------------------------
            ##print (MokaUtils.debug.lf(), "Done writing new mrml!")
            return {"dicoms": dicoms}        




        def makeMrmlReadable(self, filename, lines = None):
            """Makes MRML files more readable to humans (i.e. linebreaks).
            """
            if not lines:
                z = open(filename,"r")
                lines = z.readlines()
                z.close()

            f = open(filename,'w' )
            for line in lines:
                words = line.split()
                for word in words:
                    word = word.rstrip()
                    if len(word)>0:     
                        #word = word.strip() 
                        f.write(word + '\n')
            f.close()


