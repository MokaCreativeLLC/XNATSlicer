import sys
import os
import shutil
from datetime import datetime


SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))


def createBackup(rootDir, backupPath):
    """
    """
    

    for root, dirs, files in os.walk(rootDir):
       for f in files:
           filename = (f).replace('\\', "/")
           rVal = root.replace(rootDir, "")
           dst = (backupPath + "/" + rVal + "/" + filename).replace("\\", "/").replace("//", "/")           
           src = os.path.join(root, filename)                                                                                                            
           
           # make paths that don't exist
           if (not os.path.exists(os.path.dirname(dst))):
                os.makedirs(os.path.dirname(dst))
           
           # copy files to backup
           if not SCRIPT_DIR in src:
               shutil.copyfile(src, dst)
        
    
   
           
def condensePath(path):
    if len(path) > 50:
        path = '...' + path[-47:]
    return path


def printReplace(src, findStr, replaceStr, lineNum, oldLine, newLine):
    """
    """
    print "NEW In %s, replaced\n'%s' with '%s', in line: %i\n\n%s%s\n"%(condensePath(src), 
                                                                    findStr, 
                                                                    replaceStr, 
                                                                    lineNum, oldLine, newLine)



def replaceInFile(src, findStr, replaceStr):
    """
    @param src: The source file.
    @type src: string

    @param findStr: The string to find.
    @type findStr: string

    @param replaceStr: The string to replace.
    @type replaceStr: string
    """

    if os.path.exists(src) and os.path.isfile(src) and not SCRIPT_DIR in src:

        changedLinesCount = 0
        oldLines = [line for line in open(src)]
        newLines = []
        


        #------------------------------------
        # Generate a new line, store it
        #------------------------------------
        for i in range(0, len(oldLines)):
            oldLine = oldLines[i]
            newLine = oldLine.replace(findStr, replaceStr)
            if newLine != oldLine:
                changedLinesCount += 1
                printReplace(src, findStr, replaceStr, i, oldLine, newLine)
            newLines.append(newLine)
            
        
        #------------------------------------
        # Write the new lines to file ONLY if there are
        # changes
        #------------------------------------   
        try:
            if changedLinesCount:
                newFile = open(src, 'w')
                for line in newLines:
                    newFile.write("%s" % line)
                newFile.close()
           
        except ValueError, e:
            print "File write error: %s %s"%(str(ValueError), str(e))    
        
        

        
def beginReplace(findStr, replaceStr, fileExt, root, renameFile = False):
    """
    @param findStr: The string to find.
    @type findStr: string

    @param replaceStr: The string to replace.
    @type replaceStr: string

    @param fileExt: The file extension to apply the replace to.  All others
       will be excluded.
    @type fileExt: string

    @param root:
    @type root: string

    @param renameFile:
    @type renameFile: boolean

    """

    #------------------------------------
    # MAIN PARAMS
    #------------------------------------
    makeBackup = True
    backupDir = "scriptsBackup"
    
    
    #------------------------------------
    # OTHER PARAMS
    #------------------------------------    
    backupPath = os.path.join("./", backupDir) + "_" 
    backupPath += datetime.now().strftime("%Y-%m-%d %H:%M:%S").replace(':','_').replace(" ", "__").strip()
    renameFile = False


    #------------------------------------
    # MAKE BACKUP
    #------------------------------------
    if makeBackup:
        #  Clear Existing
        if (not os.path.exists(backupPath)):
            os.mkdir(backupPath)
            # Command
            createBackup(root, backupPath)

            
    #------------------------------------
    #  WALK THROUGH + REPLACE
    #------------------------------------   
    for root, dirs, files in os.walk(root):
       for f in files:
           filename = (f).replace('\\', "/") 
           src = os.path.join(root, filename)
           if src.endswith(fileExt):
               dst = src
               replaceInFile(dst, findStr, replaceStr)
           else:
               continue
               #print ("\n [SKIPPING %s]" %(os.path.join(root, f)))



if __name__ == "__main__":

    root = os.path.join(os.environ['XNATSLICER_HOME'], "XNATSlicer")
    fileExt = ".py"

    findReplaceDict = {
        'XnatSlicerUtils.loadNodeFromFile': 'SlicerUtils.loadNodeFromFile',
        'XnatSlicerUtils.isCurrSceneEmpty': 'SlicerUtils.isCurrSceneEmpty',
        'XnatSlicerUtils.getCurrImageNodes': 'SlicerUtils.getCurrImageNodes',
        }
    for findStr, replaceStr in findReplaceDict.iteritems():
        requirementsMet = len(findStr) > 0
        if requirementsMet:
            beginReplace(findStr, replaceStr, fileExt, root)


