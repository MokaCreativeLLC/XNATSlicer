# python
import os
import glob
import sys

# spplication
from __main__ import qt, slicer

# module
from SettingsWindow import *



class SettingsFile:
  """ 
  SettingsFile is the class that manages storable settings for the
  XnatSlicer module.  The class is activated by clicking the wrench
  icon in the XnatSlicer MODULE.  SettingsFile utilizes the qt.QSettings
  object to write to a settings database called 'SettingsFile.ini'.  As
  the formate of the database indicates, the storage method is .ini, which
  utilizes key-value pairs under a single header.


  Ex:

  [Central]
  FullName=Central
  Address=https://central.xnat.org
  IsModifiable=False
  CurrUser=user
  IsDefault=True

  @author: Sunil Kumar (sunilk@mokacreativellc.com)
  @organization: Moka Creative LLC, NRG, Washington University in St. Louis
  """

  HOST_NAME_TAG = 'FullName'
  HOST_ADDRESS_TAG =   'Address'
  HOST_IS_MODIFIABLE_TAG = 'IsModifiable'
  HOST_IS_DEFAULT_TAG = 'IsDefault'
  HOST_CURR_USER_TAG = 'CurrUser'
  REST_PATH_TAG = 'RESTPath'
  PATH_TAG = 'Paths'

  
  def __init__(self, parent = None, rootDir = None, MODULE = None):    
    """ 
    Init function.

    @param parent:
    @type parent:

    @param rootDir:
    @type rootDir:

    @param MODULE:
    @type MODULE:
    """
    if not parent:
      self.parent = slicer.qMRMLWidget()
    else:
      self.parent = parent   
      
    self.MODULE = MODULE
    self.filepath = os.path.join(rootDir, 'SettingsFile.ini')

    #--------------------
    # OS specific database settings
    #--------------------
    self.dbFormat = qt.QSettings.IniFormat 

        
    self.resetDatabase()

    
    self.defaultHosts = {'Central': 'https://central.xnat.org', 
                         'CNDA': 'https://cnda.wustl.edu'}  
    self.setup()
    self.currErrorMessage = ""
    slicer.app.processEvents()

    


  def resetDatabase(self):
      """
      """
      self.database = qt.QSettings(self.filepath, self.dbFormat)

      

      

  def backupCurrentSettings(self):
      """
      """
 
      shutil.copy(self.filepath, self.filepath.replace("File.ini", "BACKUP.txt"))

        


  def restorePreviousSettings(self):
      """
      """
      shutil.move(self.filepath, self.filepath.replace("File.ini", "OLD.txt"))
      shutil.move(self.filepath.replace("File.ini", "BACKUP.txt"), self.filepath)
      self.resetDatabase()



    
  def setup(self):
    """ 
    Determine if there is an SettingsFile.ini file.
    """
    if not os.path.exists(self.filepath): 
        #print 'No Xnat settings found...creating new settings file: ' + self.filepath
        self.createDefaultSettings()
        #
        # We want the application to wait
        # until the file has been created. 
        #
        slicer.app.processEvents()



        
  def createDefaultSettings(self):  
    """ 
    Constructs a default database based on
    the 'self.defaultHosts' parameter.
    """
    restPaths = ['']
    for name in self.defaultHosts:
         default = True if name == 'Central' else False
         modifiable = True if name != 'Central' else False
         #print modifiable, name
         self.saveHost(name, self.defaultHosts[name], isModifiable = modifiable, isDefault = default)    
    self.savePaths(restPaths, "REST")


    

  def getHostsDict(self):
    """ 
    Queries the database for hosts and creates
    a dictionary of key 'name' and value 'address'
    """
    hostDict = {}        
    for key in self.database.allKeys():
        if SettingsFile.HOST_ADDRESS_TAG in key:
            hostDict[key.split("/")[0].strip()] = self.database.value(key)
    return hostDict



  
  def setSetting(self, hostName, *args):
      """ 
      Saves the custom metadata tags to the given host.
      """


      
      self.database.beginGroup(hostName)


      #--------------------
      # For dictionary arguments
      #--------------------
      if isinstance(args[0], dict):
        for tag, items in args[0].iteritems(): 
          #
          # Convert items to list, if necessary
          #
          items = items if isinstance(items, list) else [items]
          if len(items) > 0:
            self.database.setValue(tag, ','.join(str(item) for item in items))
          else:
            self.database.setValue(tag, '')



      #--------------------
      # For multiple arguments
      #--------------------
      else:
          if len(args) > 1:
            values = ''
            for i in range(1, len(args)):
              if isinstance(args[i], list):
                values += ','.join(str(item) for item in args[i])
              else:
                values += ','.join(args[i])
              

            self.database.setValue(args[0], values)
            
          else:
            self.database.setValue(args[0], '')
          


      self.database.endGroup()




  def printAll(self):
    """
    """
    if os.path.exists(self.filepath):
      with open(self.filepath) as f:
        content = f.readlines()
        for l in content:
          print l
        del content
    else:
      print "No settings file at: %s"%(self.filepath)


      
  
  def saveHost(self, hostName, hostAddress, isModifiable=True, isDefault=False):
    """ Writes host to the QSettings.ini database.
    """
    
    hostDict = self.getHostsDict()
    hostNameFound = False


    
    #--------------------
    # Check to see if 'hostAddress' is a valid http URL, 
    # modify if not.
    #--------------------
    if not hostAddress.startswith("http://") and not hostAddress.startswith("https://"):
        hostAddress ="http://" + hostAddress



    #--------------------
    # Check if the host name exists.
    #--------------------
    for name in hostDict:
        hostNameFound = True if str(name).lower() == str(hostName).lower() else False 



    #--------------------
    # If there are blank fields, return warning window...
    #--------------------
    if hostName == "" or hostAddress == "":
       blanks = [] 
       if hostName == "": 
           blanks.append("Name")
       if hostAddress == "": 
           blanks.append("URI")
       
       blankTxt = ""
       for i in range(0, len(blanks)):
            blankTxt += blanks[i]
            if i<len(blanks)-1: blankTxt+=", "
            
       qt.QMessageBox.warning( None, "Save Host", "Please leave no text field blank (%s)"%(blankTxt))
       return False    

    

    #--------------------
    # Else if the host name is already used, return warning window, then exit...
    #--------------------
    elif hostNameFound == True and isModifiable == True:
       qt.QMessageBox.warning( None, "Save Host", hostName + " is a name that's already in use.")
       hostFound = False
       return False


    #--------------------
    # Otherwise, save host.
    #--------------------
    else:
        #
        # Remove existing.
        #
        self.database.remove(hostName)
        #
        # Start group.
        #
        self.database.beginGroup(hostName)
        self.database.setValue(SettingsFile.HOST_NAME_TAG, hostName)
        self.database.setValue(SettingsFile.HOST_ADDRESS_TAG, hostAddress)
        #
        # Set isModifiable.
        #
        self.database.setValue(SettingsFile.HOST_IS_MODIFIABLE_TAG, str(isModifiable))
        #
        # Set currUser.
        #
        self.database.setValue(SettingsFile.HOST_CURR_USER_TAG, "")
        #
        # Set isDefault to 'False' (first pass)
        #
        self.database.setValue(SettingsFile.HOST_IS_DEFAULT_TAG, str(False))
        self.database.endGroup()
        #
        # (second pass) conuct the setDefault function.
        #
        if isDefault: 
            self.setDefault(hostName)
        return True



    
  def savePaths(self, paths, pathType = "REST"): 
    """ As stated.
    """
    if pathType == "REST":
        currTag = SettingsFile.REST_PATH_TAG       
    for path in paths:
        self.database.setValue(SettingsFile.PATH_TAG + currTag, path)



          
  def getPath(self, pathType = "REST"):
    """ As stated.
    """
    if pathType == "REST":
        currTag = SettingsFile.REST_PATH_TAG      
    return self.database.value(SettingsFile.PATH_TAG + currTag, "")   



  
  def deleteHost(self, hostName): 
    """ As stated.
    """
    if self.database.value(hostName + "/" + SettingsFile.HOST_IS_MODIFIABLE_TAG, ""):
        self.database.remove(hostName)
        return True
    return False



    
  def setDefault(self, hostName):
    """ As stated.
    """

    #--------------------
    # Cycle through database...
    #--------------------
    for key in self.database.allKeys():
        #
        # Find keys that have the 'isDefault' tag (all of them)...
        #
        if SettingsFile.HOST_IS_DEFAULT_TAG in key:
            #
            # If there's a match in with hostName, then 
            # save the 'setDefault' to database.
            #
            tHost = key.split("/")[0].strip()
            retVal = True if hostName == tHost else False
            self.database.beginGroup(tHost)
            self.database.setValue(SettingsFile.HOST_IS_DEFAULT_TAG, str(retVal))
            self.database.endGroup()



    
  def getDefault(self):
    """ As stated.  Cycle through all
        database keys to find the default hosts.
    """   
    for key in self.database.allKeys():
        if SettingsFile.HOST_IS_DEFAULT_TAG in key and self.database.value(key) == 'True':
            return key.split("/")[0].strip()



    
  def isDefault(self, hostName):
    """ As stated.  Determines if a given host name
        is also a defaulted host name.
    """   

    val = self.database.value(hostName + "/" + SettingsFile.HOST_IS_DEFAULT_TAG)
    if not val or 'False' in val:
        return False
    return True



  
  def isModifiable(self, hostName):
    """ As stated.  Determines if a given host
        can be modified by the user.
    """
    val = self.database.value(hostName + "/" + SettingsFile.HOST_IS_MODIFIABLE_TAG)

    if not val:
        return True
    if 'False' in val:
        return False
    return True



  def tagExists(self, hostName, tag):
    """
    """
    return self.database.contains(hostName + "/" + tag)
    


  def getSetting(self, hostName, tag):
    """ 
    As stated.  Determines if a given host
    can be modified by the user.
    """
    val = self.database.value(hostName + "/" + tag)

    if val:
        if ',' in val:
            return val.split(',')
        return [val]
    return []

  

  
  def getAddress(self, hostName):
    """ As stated.
    """
    return self.database.value(hostName + "/" + SettingsFile.HOST_ADDRESS_TAG, "")



  
  def setCurrUsername(self, hostName, username):
    """ As stated.
    """
    self.database.beginGroup(hostName)  
    self.database.setValue(SettingsFile.HOST_CURR_USER_TAG, username)
    self.database.endGroup()



    
  def getCurrUsername(self, hostName):
    """ As stated.
    """
    for key in self.database.allKeys():
        if SettingsFile.HOST_CURR_USER_TAG in key and hostName in key:
            return self.database.value(key)
 


 
