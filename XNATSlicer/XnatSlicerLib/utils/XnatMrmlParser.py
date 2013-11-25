from __main__ import vtk, ctk, qt, slicer

import os
import sys
import StringIO
import xml.etree.ElementTree as ET
import codecs
import shutil

from XnatTimer import *



comment = """
XnatMrmlParser handles the parsing of a MRML file (XML-based) and 
either changes the paths of the remotely linked files to local 
directories, or to relative directories.

TODO : 
"""



class XnatMrmlParser(object):
    """ Description above.
    """

    def __init__(self, MODULE = None):    
        """ Initialises class variables
        """   
        self.MODULE = MODULE
        self.useCache = True
        self.tempLocalFileMap = None
        self.tempNewFilename = None
        self.cacheList = None
        self.TESTWRITE = False



        
    def changeValues(self, filename, newFilename, replaceValues, 
                     otherReplaceValues, removeOriginalFile = False, 
                     debug = True):
        """ Changes the string values within a given file
            based on a provided lists 'replaceValues' and 'otherReplaceValues'.
        """

        
        #print (self.MODULE.utils.lf(), "Changing values in the mrml.") 
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
            self.MODULE.utils.removeFile(filename)
            slicer.app.processEvents()
            filename = bkpFN


            
        #------------------------
        # Init xml parser
        #------------------------
        elementTree = ET.parse(codecs.open(filename, encoding="UTF-8"))
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
                            #print self.MODULE.utils.lf() + " CHANGING NAME WITH DATA FORMAT: 
                            # %s\tOLD: %s\tNEW:%s"%(subelement.attrib[name], value, "./Data/" + os.path.basename(value))
                            subelement.attrib[name] = "./Data/%s"%(os.path.basename(value))

                            
        
        #------------------------
        # write new mrml
        #------------------------
        elementTree.write(newFilename)     

        
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
        #print (self.MODULE.utils.lf(), "Done writing new mrml!")
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

            
