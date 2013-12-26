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
    
   
           
def checkAndInject(src, findStr, replaceStr):
   
   # read the file line by line, store it.
   if os.path.exists(src):
       lines = [line for line in open(src)]
       newLines = lines
       for l in lines:
           if findStr in l:
               newLines = [replaceStr + '\n'] + newLines
               print "Injecting '%s' into '%s'"%(replaceStr, src)
               break
        

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
    
    findStr = "GLOB_"
    injectStr = "from GLOB import *"


 
    backupPath = os.path.join("../", backupDir) + "_" + datetime.now().strftime("%Y-%m-%d %H:%M:%S").replace(':','_').replace(" ", "__").strip()




    #------------------------------------
    # MAKE BACKUP
    #------------------------------------
    if (not os.path.exists(backupPath)):
        os.mkdir(backupPath)
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
           checkAndInject(src, findStr, injectStr)



if __name__ == "__main__":
    main()
