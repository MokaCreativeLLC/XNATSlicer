import sys
import os
import shutil
from datetime import datetime


def createBackup(rootDir, backupPath):
    for root, dirs, files in os.walk(rootDir):
       for f in files:
           filename = (f).replace('\\', "/")
           rVal = root.replace(rootDir, "")
           dst = (os.path.join("./", backupPath + "/" + rVal + "/" + filename)).replace("\\", "/").replace("//", "/")           
           src = os.path.join(root, filename)                                                                                                            
           
           # make paths that don't exist
           if (not os.path.exists(os.path.dirname(dst))):
                os.makedirs(os.path.dirname(dst))
           
           # copy files to backup
           shutil.copyfile(src, dst)
    
   
           
def replaceInFile(src, findStr, replaceStr):
   
   # read the file line by line, store it.
   if os.path.exists(src):
       lines = [line for line in open(src)]
       newLines = []
       for l in lines:
           a = l.replace(findStr, replaceStr)
           if (a != l):
               print "In %s, replaced '%s' with '%s', in line: %i\n    %s\n    %s"%(src, findStr, replaceStr, lines.index(l), l, a)
           newLines.append(a)
    
       try:
           fl = open(src, 'w')
           for item in newLines:
               fl.write("%s" % item)
           fl.close()
           #print "Replaced '%s' with '%s' in %s."%(findStr, replaceStr, src)
       except ValueError:
            print ValueError    
        
        
        
def main():



    #------------------------------------
    # MAIN PARAMS
    #------------------------------------
    makeBackup = True
    rootDir = "../XnatSlicerLib"
    backupDir = "scriptsBackup"
    
    findStr = "*from"
    replaceStr = "*\nfrom"
    fileExt = ".py"

    
    #------------------------------------
    # OTHER PARAMS
    #------------------------------------    
    htmlFile = "../index-uncompressed.html"
    fileReplaceStr = replaceStr #replaceStr.split(".")[2]
    skipDirs = ["jquery", "python"];
    backupPath = os.path.join("./", backupDir) + "_" + datetime.now().strftime("%Y-%m-%d %H:%M:%S").replace(':','_').replace(" ", "__").strip()
    renameFile = False



    #------------------------------------
    # MAKE BACKUP
    #------------------------------------
    if makeBackup:
        #  Clear Existing
        if (not os.path.exists(backupPath)):
            os.mkdir(backupPath)
            
            # Command
            createBackup(rootDir, backupPath)



    #------------------------------------
    #  WALK THROUGH + REPLACE
    #------------------------------------   
    for root, dirs, files in os.walk(rootDir):
       print dirs
       for f in files:
           print f
           filename = (f).replace('\\', "/") 
           src = os.path.join(root, filename)
           
           # Determine keeper
           keeper = True
           for skipper in skipDirs:
               if (len( skipper ) > 0) and ( skipper  in root):
                   keeper = False;
                   break;
           
           # Continue if keeper    
           if keeper and src.endswith(fileExt):
               print src
               dst = src
               
               # Rename file with string               
               if (findStr in src) and renameFile:
                   dst = src.replace(findStr, fileReplaceStr)
                   os.rename(src, dst)

                   
               replaceInFile(dst, findStr, replaceStr)
           else:
               continue
               #print ("\n [SKIPPING %s]" %(os.path.join(root, f)))



    # Replace in main html if necessary
    if len(htmlFile)>0 and os.path.exists(htmlFile):
        replaceInFile(htmlFile, findStr, fileReplaceStr)

if __name__ == "__main__":
    main()
