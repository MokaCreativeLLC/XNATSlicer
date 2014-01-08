from __future__ import with_statement
from __main__ import vtk, ctk, qt, slicer

#Python imports
import os



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
