from __main__ import vtk, ctk, qt, slicer
import datetime, time

import os
import sys



comment = """
XnatTimer manages time logging for performance testing and 
allows the user to write the log to a file.

Usage as follows:

from XnatTimer import *
timer = XnatTimer(writePath = "./", writeFileName = "timelog.txt")
timer.start(processName = "Download", debugStr = "Downloading...")

>>> Download
>>> 2013-08-21 09:27:11.673000 <--Start timer before Downloading....

# Download code here

timer.stop()

>>> 2013-08-21 09:27:18.396000 <---Stop timer after Downloading....
>>> TOTAL TIME ELAPSED FOR Download: 		0:00:06.723000

"""


                
class XnatTimer(object):
    """ Descriptor above.
    """
    
    def __init__(self, MODULE = None, writePath = './', writeFileName = 'timerlog.txt', fileOverWrite = False):
        """ Init function.  Defines necessary variables.
        """

        self.prev = None
        self.curr = None
        self.debugStr = None
        self.processName = None
        self.timerStrs = []

        #-------------------------
        # Override the defaulted 'writePath' if the 'MODULE' argument
        # is provided.
        #-------------------------
        if MODULE:
            self.writePath = MODULE.GLOBALS.LOCAL_URIS['settings']
        else:
            self.writePath = self.writePath


            
        #-------------------------
        # Make the 'writeFileName'
        #-------------------------
        if not writeFileName: 
            self.writeFileName = os.path.join(self.writePath, 'timerLog.txt')
        else: 
            self.writeFileName = os.path.join(self.writePath, writeFileName)
          
        self.fileOverWrite = fileOverWrite 
        self.startCalled = False



        
    def start(self, processName = None, debugStr = None):       
        """ Starts the timer process and tracks
            the variables accordingly.  Timer process is provided
            by the user in the 'processName' argument.
        """

        #-------------------------
        # Write the start time to console and to file.
        #-------------------------       
        self.startCalled = True
        self.debugStr = debugStr   
        self.prev = datetime.datetime.now() 
        
        currStr = ""

        if processName:
            self.processName = processName
            self.timerStrs.append('\n' + processName + '\n') 
            print('\n\n\n' + processName)

            
        if self.debugStr: 
            currStr = "before " + self.debugStr + "."

            
        str  = ("%s <--Start timer %s"%(self.prev, currStr))
        self.timerStrs.append(str + '\n')
        print str


        
            
    def stop(self, fileWrite = True, printTimeDiff = True):
        """ Writes the the stop time to file (and it's associated
            process name) and to console. Only works if the 'start'
            function was called before it.
        """
        if self.startCalled:
            currStr = ""
            elapseStr = ""

            #-------------------------
            # Write the stop time to console and the file.
            #-------------------------
            self.curr = datetime.datetime.now() 

            if self.debugStr: 
                currStr = "after " + self.debugStr + "."

            if self.processName: 
                elapseStr = "FOR " + self.processName
            
            str1  = ("%s <---Stop timer %s"%(self.curr, currStr))
            self.timerStrs.append(str1 + '\n')
            print str1

            if printTimeDiff:
                str2 =  ("\n\nTOTAL TIME ELAPSED %s: \t\t%s"%(elapseStr, (self.curr-self.prev)))
                self.timerStrs.append(str2 + '\n')
                print str2
            
            if fileWrite: self.write()
            self.clear()



            
    def write(self):
        """ As stated.
        """
        if self.writeFileName:
            f = open(self.writeFileName, 'a')
            f.writelines(self.timerStrs)            
            f.close()



            
    def clear(self):
        """ Clears the variables.
        """
        self.curr = None
        self.prev = None
        self.debugStr = None
        self.processName = None
        del self.timerStrs[:]
        self.startCalled = False
