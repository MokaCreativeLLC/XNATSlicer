# python
import os

# external
from MokaUtils import *

# application
from __main__ import qt, slicer

# module
from SettingsWindow import *



class SettingsFile:
  """ 
  SettingsFile is the class that manages storable settings for the
  XnatSlicer module.  SettingsFile utilizes the qt.QSettings
  object to write to a settings database called 'SettingsFile.ini'.  As
  the format of the database indicates, the storage method is .ini, which
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
  HOST_URL_TAG =   'URL'
  HOST_IS_MODIFIABLE_TAG = 'IsModifiable'
  HOST_IS_DEFAULT_TAG = 'IsDefault'
  HOST_CURR_USER_TAG = 'CurrUser'
  REST_PATH_TAG = 'RESTPath'
  PATH_TAG = 'Paths'
  
  FILE_PREFIX = 'Settings'
  FILE_SUFFIX = 'File.ini'
  FILE_SUFFIX_OLD = 'OLD.txt'
  FILE_SUFFIX_BACKUP = 'BACKUP.txt'
  
  EVENT_TYPES = [
    'SETTINGS_FILE_RESTORED'
  ]
  
  def __init__(self, parent = None, rootDir = None, MODULE = None):    
    """ 
    Init function.

    @param parent: The parent qt.QWidget of the settings file.
    @type parent: qt.QWidget

    @param rootDir: The root directory where to store the settings file.
    @type rootDir:  str

    @param MODULE: The XNAT Slicer module.
    @type MODULE: XNATSlicerWidget
    """

    if not parent:
      self.parent = slicer.qMRMLWidget()
    else:
      self.parent = parent   
    self.Events = MokaUtils.Events(self.EVENT_TYPES)
    self.MODULE = MODULE
    self.filepath = os.path.join(rootDir, self.FILE_PREFIX + self.FILE_SUFFIX)

    #--------------------
    # OS specific database settings
    #--------------------
    self.dbFormat = qt.QSettings.IniFormat 
    self.__resetDatabase()
    self.defaultHosts = {'Central': 'https://central.xnat.org', 
                         'CNDA': 'https://cnda.wustl.edu'}  
    self.setup()
    self.currErrorMessage = ""
    slicer.app.processEvents()

    


  def __resetDatabase(self):
      """
      As stated.
      """
      self.database = qt.QSettings(self.filepath, self.dbFormat)

      
      

  def backupCurrentSettings(self):
      """
      Backs up the current settings file via a file copy to 
      SettingsFileBACKUP.txt
      """
      shutil.copy(self.filepath, self.filepath.replace( \
                                 self.FILE_SUFFIX,
                                 self.FILE_SUFFIX_BACKUP))

        


  def restorePreviousSettings(self):
      """
      Reverts the settings file by referring to the SettingsBACKUP.txt.
      Also stores the current settings into SettingsOLD.txt.
      """
      shutil.move(self.filepath, self.filepath.replace(\
                                        self.FILE_SUFFIX, 
                                        self.FILE_SUFFIX_OLD))

      shutil.move(self.filepath.replace(self.FILE_SUFFIX, 
                                        self.FILE_SUFFIX_BACKUP), 
                  self.filepath)
      self.__resetDatabase()
      self.Events.runEventCallbacks('SETTINGS_FILE_RESTORED')



    
  def setup(self):
    """ 
    Determine if there is an SettingsFile.ini file.  Creates one if there
    is none and applies default settings to it.
    """
    if not os.path.exists(self.filepath): 
        #MokaUtils.debug.lf('No Xnat settings found...' + 
        # 'creating new settings file: + self.filepath')
        self.__createDefaultSettings()
        slicer.app.processEvents()



        
  def __createDefaultSettings(self):  
    """ 
    Constructs a default database based on
    the 'self.defaultHosts' parameter.
    """
    restPaths = ['']
    for name in self.defaultHosts:
         default = True if name == 'Central' else False
         modifiable = True if name != 'Central' else False
         #print modifiable, name
         self.saveHost(name, self.defaultHosts[name], 
                       isModifiable = modifiable, isDefault = default)    

    

  def getHostsDict(self):
    """ 
    Queries the database for hosts and creates
    a dictionary of key 'name' and value 'address'.

    @return: A dictionary of host names to URLs.
    @rtype: dict
    """
    hostDict = {}        
    for key in self.database.allKeys():
        if SettingsFile.HOST_URL_TAG in key:
            hostDict[key.split("/")[0].strip()] = self.database.value(key)
    return hostDict



  
  def setSetting(self, hostName, *args):
      """ 
      Saves the custom metadata tags to the given host.

      @param hostName:  The name of the host to save the settings to.
      @type hostName: str

      @param args: The arguments to apply.
      @type args: dict(str, list(str)) | *str
      """
      
      self.database.beginGroup(hostName)

      #--------------------
      # For dictionary arguments
      #--------------------
      if isinstance(args[0], dict):
        for tag, items in args[0].iteritems(): 
          # Convert items to list, if necessary
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
    Prints the entire database into the python console.
    """
    if os.path.exists(self.filepath):
      with open(self.filepath) as f:
        content = f.readlines()
        for l in content:
          print l
        del content
    else:
      print "No settings file at: %s"%(self.filepath)


      
  
  def saveHost(self, hostName, hostURL, isModifiable=True, isDefault=False):
    """ 
    Writes host to the QSettings.ini database.

    @param hostName: The name of the host.
    @type hostName: str

    @param hostURL: The URL of the host.
    @type hostURL: str

    @param isModifiable: Whether the host is modifiable.
    @type isModifiable: bool

    @param isDefault: Whether to set the host as default.
    @type isDefault: bool
    """
    
    hostDict = self.getHostsDict()
    hostNameFound = False


    
    #--------------------
    # Check to see if 'hostURL' is a valid http URL, 
    # modify if not.
    #--------------------
    if not hostURL.startswith("http://") and \
       not hostURL.startswith("https://"):
        hostURL ="http://" + hostURL



    #--------------------
    # Check if the host name exists.
    #--------------------
    for name in hostDict:
        hostNameFound = True if str(name).lower() == str(hostName).lower() \
                        else False 



    #--------------------
    # If there are blank fields, return warning window...
    #--------------------
    if hostName == "" or hostURL == "":
       blanks = [] 
       if hostName == "": 
           blanks.append("Name")
       if hostURL == "": 
           blanks.append("URI")
       
       blankTxt = ""
       for i in range(0, len(blanks)):
            blankTxt += blanks[i]
            if i<len(blanks)-1: blankTxt+=", "
            
       qt.QMessageBox.warning( None, "Save Host", "Please leave no text " + 
                               " field blank (%s)"%(blankTxt))
       return False    

    

    #--------------------
    # Else if the host name is already used, return warning window, then exit...
    #--------------------
    elif hostNameFound == True and isModifiable == True:
       qt.QMessageBox.warning( None, "Save Host", hostName + " is a name" +
                               " that's already in use.")
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
        self.database.setValue(SettingsFile.HOST_URL_TAG, hostURL)
        #
        # Set isModifiable.
        #
        self.database.setValue(SettingsFile.HOST_IS_MODIFIABLE_TAG, 
                               str(isModifiable))
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


  
  def deleteHost(self, hostName): 
    """ 
    As stated.

    @param hostName: The name of the host to delete.
    @type hostName: str

    @return: Whether the delete operation was succesful.
    @rtype: bool
    """
    if self.database.value(hostName + "/" + \
                           SettingsFile.HOST_IS_MODIFIABLE_TAG, ""):
        self.database.remove(hostName)
        return True
    return False



    
  def setDefault(self, hostName):
    """ 
    Sets the provided hostName to the default.

    @param hostName: The name of the host to delete.
    @type hostName: str
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
            self.database.setValue(SettingsFile.HOST_IS_DEFAULT_TAG, 
                                   str(retVal))
            self.database.endGroup()



    
  def getDefault(self):
    """ As stated.  Cycle through all
        database keys to find the default hosts.
    """   
    for key in self.database.allKeys():
        if SettingsFile.HOST_IS_DEFAULT_TAG in key \
           and self.database.value(key) == 'True':
            return key.split("/")[0].strip()



    
  def isDefault(self, hostName):
    """ 
    Determines if a given host name
    is also a defaulted host name.

    @param hostName: The name of the host to run the operation on.
    @type hostName: str

    @return: Whether the hostName is the default.
    @rtype: bool
    """   

    val = self.database.value(hostName + "/" + \
                              SettingsFile.HOST_IS_DEFAULT_TAG)
    if not val or 'False' in val:
        return False
    return True



  
  def isModifiable(self, hostName):
    """ 
    Determines if a given host
    can be modified by the user.

    @param hostName: The name of the host to run the operation on.
    @type hostName: str

    @return: Whether the hostName is modifiable.
    @rtype: bool
    """
    val = self.database.value(hostName + "/" + \
                              SettingsFile.HOST_IS_MODIFIABLE_TAG)

    if not val:
        return True
    if 'False' in val:
        return False
    return True




  def tagExists(self, hostName, tag):
    """
    Determins if a tag exists within the current host name section.

    @param hostName: The name of the host to run the operation on.
    @type hostName: str

    @param tag: The tag within the host.
    @type tag: str

    @return: Whether the tag name exists.
    @rtype: bool
    """
    return self.database.contains(hostName + "/" + tag)
    


  def getSetting(self, hostName, tag):
    """ 
    Gets a given setting associated with a given host name.

    @param hostName: The name of the host to run the operation on.
    @type hostName: str

    @param tag: The tag within the host.
    @type tag: str

    @return: The contents of the array associated with the tag.  Returns an 
        empty array otherwise.
    @rtype: list
    """
    val = self.database.value(hostName + "/" + tag)

    if val:
        if ',' in val:
            return val.split(',')
        return [val]
    return []

  

  
  def getAddress(self, hostName):
    """ 
    Returns the URL associated with the provided host name.

    @param hostName: The name of the host to run the operation on.
    @type hostName: str

    @return: The URL associated with the provided host name.
    @rtype: str

    """
    return self.database.value(hostName + "/" + \
                               SettingsFile.HOST_URL_TAG, "")



  
  def setCurrUsername(self, hostName, username):
    """
    Sets the current username associated with a given host.

    @param hostName: The name of the host to run the operation on.
    @type hostName: str

    @param username: The username to store.
    @type username: str
    """
    self.database.beginGroup(hostName)  
    self.database.setValue(SettingsFile.HOST_CURR_USER_TAG, username)
    self.database.endGroup()



    
  def getCurrUsername(self, hostName):
    """
    Gets the current username associated with a given host.

    @param hostName: The name of the host to run the operation on.
    @type hostName: str

    @return: The username associated with the host.
    @rtype: str | None
    """
    for key in self.database.allKeys():
        if SettingsFile.HOST_CURR_USER_TAG in key and hostName in key:
            return self.database.value(key)
 


 
