import os
import sys
import shutil
import time
import math
import urllib2
import base64
from urlparse import urljoin
import string    
import httplib
import codecs
from os.path import abspath, isabs, isdir, isfile, join
import json


"""
XNAT Software License Agreement

Copyright 2005 Harvard University / Howard Hughes Medical Institute (HHMI) / Washington University
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted 
provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this list of conditions 
and the following disclaimer.
Redistributions in binary form must reproduce the above copyright notice, this list of conditions 
and the following disclaimer in the documentation and/or other materials provided with the distribution.
Neither the names of Washington University, Harvard University and HHMI nor the names of its contributors 
may be used to endorse or promote products derived from this software without specific prior written permission.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED 
WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A 
PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR 
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED 
TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) 
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING 
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE 
POSSIBILITY OF SUCH DAMAGE.
"""


class XnatIo(object):
    """ 
    XnatIo is a lightweight communicator class to XNAT. XnatIo uses REST calls to 
    send/receive commands and files to XNAT. Since input is usually string-based, there are 
    several utility methods in this class to clean up strings.  Its primary
    communicator classes are httplib and urllib2.

    Example Usage:
    
        >>> from XnatIo import *
        >>> xnatIo = XnatIo('http://central.xnat.org', 'testUser', 'testUserPassword')
        >>> contents = xnatIo.getFolder('projects')
        >>> print contents[111]['ID']
        'XNATSlicerTest'    


    @author: Sunil Kumar (sunilk@mokacreativellc.com)
    @contact: Sunil Kumar (sunilk@mokacreativellc.com), Dan Marcus (dmarcus@wustl.edu)
    @organization: Moka Creative, LLC in collaboration wtih The Neuroinformatics Research Group (NRG) 
        and The National Alliance for Medial Computing (NA-MIC)
    @license: XNAT Software License Agreement (above)


    @see:
    U{http://www.voidspace.org.uk/python/articles/authentication.shtml}
    U{http://blog.oneiroi.co.uk/python/python-urllib2-basic-http-authentication/}
    U{http://stackoverflow.com/questions/5131403/http-basic-authentication-doesnt-seem-to-work-with-urllib2-in-python}
    U{http://stackoverflow.com/questions/635113/python-urllib2-basic-http-authentication-and-tr-im/4188709#4188709}
    """

    EVENT_TYPES = [
        'downloadCancelled',
        'downloading',
        'downloadStarted',
        'downloadFinished',
        'downloadQueueFinished',
        'downloadQueueStarted',
        'downloadFailed',
        'jsonError'
     ] 




    def __init__(self, host, username, password):
        """ 
        Initializes the internal variables. 
        
        @param host: The XNAT host to interact with.  NOTE: Full domain name needed.
        @type host: string

        @param username: The username for the XNAT host.
        @type username: string

        @param password: The password for the XNAT host.
        @type password: string        
        """
        self.downloadQueue = []        
        self.eventCallbacks = {}
        for eventType in self.EVENT_TYPES:
            self.eventCallbacks[str(eventType)] = []


        #-------------------
        # Set relevant variables (all required)
        #-------------------
        self.projectCache = None
        self.host = host
        self.username = username
        self.password = password


        
        #-------------------
        # Make tracking dictionary for download modal.
        #-------------------
        self.downloadTracker = {
            'totalDownloadSize': {'bytes': None, 'MB': None},
            'downloadedSize': {'bytes': None, 'MB': None},
        }


        #-------------------
        # Make relevant variables for __httpsRequests
        #-------------------       
        base64string = base64.encodestring('%s:%s' % (self.username, self.password))[:-1]
        self.authHeader = { 'Authorization' : 'Basic %s' %(base64string) }
        self.fileDict = {};




    def getFolder(self, folderUris, metadata = None, queryArgs = None):   
        """ 
        Returns the contents of a given folder provided in the arguments
        'folderUris'.  Returns an object based on the 'metadata' argument
        which filters the return contents.  The 'queryArgs' parameter
        deals generally with further fitering of certain contents within a given folder. 
        For instance, to get projects only the user has access to, the URI needs
        to be appended with '?accessible=True'.

        @param folderUris: A string or list of URIs to retrieve the contents from.
        @type folderUris: string | list.<string>

        @param metadata: A list of metadata attributes to include in the return dict.  
            Default is all metadata.
        @type metadata: list.<string>

        @param queryArgs: A string or list of query argument suffixes to apply.
            Default is no suffix.
        @type queryArgs: string | list.<string>

        @return: A list of dicts describing the contents of the folders, with metadata as keys.
        @rtype: list.<dict>
        """

        returnContents = {}


        
        #-------------------- 
        # Force the relevant argumets to lists
        #-------------------- 
        if isinstance(folderUris, basestring):
           folderUris = [folderUris]
        if isinstance(queryArgs, basestring):
           queryArgs = [queryArgs]

           
           
        #-------------------- 
        # Acquire contents via 'self.__getJson'
        #-------------------- 
        contents = []
        for folderUri in folderUris:
                
            #
            # Apply query arguments, if any.
            #
            if queryArgs:
                folderUri = XnatIo.uri.applyQueryArguments(folderUri, queryArgs)
                
    
            #
            # Get the JSON
            #
            folderUri = XnatIo.uri.makeXnatUrl(self.host, folderUri)
            json = self.__getJson(folderUri)
    
            #
            # If json is null we have a login error.
            # Return out.
            #
            if json == None:
                return None
            #
            # Otherwise, concatenate to rest of contents.
            #
            contents =  contents + json

            #
            # If we want the projects, store projects in a dictionary. 
            # 'self.projectCache' is reset if the user logs into a new host or 
            # logs in a again.
            #
            if folderUri.endswith('/projects'):
                self.projectCache = contents
            #print "CONTENTS", contents
        #-------------------- 
        # Exit out if there are non-Json or XML values.
        #-------------------- 
        if str(contents).startswith("<?xml"): return [] # We don't want text values

        

        #-------------------- 
        # Get other attributes with the contents 
        # for metadata tracking.
        #-------------------- 
        for content in contents:
            if metadata:
                for metadataTag in metadata:
                    if metadataTag in content:
                        #
                        # Create the object attribute if not there.
                        #
                        if not metadataTag in returnContents:
                            returnContents[metadataTag] = []
                        returnContents[metadataTag].append(content[metadataTag])
            else:
                returnContents = contents

            
        #-------------------- 
        # Track projects and files in global dict
        #-------------------- 
        for folderUri in folderUris:
            folderUri = folderUri.replace('//', '/')
            if folderUri.endswith('/files'):
                for content in contents:
                    # create a tracker in the fileDict
                    #print "\n\nCONTENT", content, folderUri    
                    self.fileDict[content['Name']] = content
                #print "%s %s"%(, self.fileDict)
            elif folderUri.endswith('/projects'):
                self.projectCache = returnContents


                
        #-------------------- 
        # Return the contents of the folder as a
        # dictionary of lists
        #-------------------- 
        return returnContents



    
    def getFile(self, _src, _dst): 
        """ 
        Downloads a file from a given XNAT host.

        @param _src: The source XNAT URL to download form.
        @type: string

        @param _dst: The local dst to download to.
        @type: string
        """
        
        #--------------------
        # Reset total size of downloads for all files
        #-------------------------
        self.downloadTracker['totalDownloadSize']['bytes'] = 0
        self.downloadTracker['downloadedSize']['bytes'] = 0
        downloadFolders = []


        
        #-------------------------
        # Remove existing dst files from their local URI
        #-------------------------
        if os.path.exists(_dst):
            os.remove(_dst)
        self.__getFile_urllib(_src, _dst)




    def getResources(self, folder):
        """ 
        Gets the contents of a 'resources' folder
        in a given XNAT host.  'resources' folders 
        demand a bit more specifity in the metadata manipulation.
        Furthermore, 'resources' folders are frequently accessed
        as part of the Slicer file location within an 'experiment'.

        @param folder: The folder to retrieve the 'resources' folder contents from.
        @type folder: string
        """

        #-------------------- 
        # Get the resource JSON
        #-------------------- 
        folder += "/resources"
        resources = self.__getJson(folder)
        #print "%s %s"%(, folder)
        #print  + " Got resources: '%s'"%(str(resources))


        
        #-------------------- 
        # Filter the JSONs
        #-------------------- 
        resourceNames = []
        for r in resources:
            if 'label' in r:
                resourceNames.append(r['label'])
                #print ( +  "FOUND RESOURCE ('%s') : %s"%(folder, r['label']))
            elif 'Name' in r:
                resourceNames.append(r['Name'])
                #print ( +  "FOUND RESOURCE ('%s') : %s"%(folder, r['Name']))                
            
            return resourceNames



    def getFileSize(self, _uri):
        """ 
        Retrieves a tracked file's size and 
        converts it to MB based on the 'self' variable
        'fileDict' which contains the raw byte size 
        of the given file.

        @param _uri: The file URI to retrieve the size from.
        @type _uri: string

        @return: The size in MB of the file.
        @rtype: integer
        """
        bytes = 0
        fileName = os.path.basename(_uri)
        if fileName in self.fileDict:
            bytes = int(self.fileDict[fileName]['Size'])
            return {"bytes": (bytes), "MB" : XnatIo.utils.bytesToMB(bytes)}

        return {"bytes": None, "MB" : None}



    def putFolder(self, _dst):
        """ 
        Function for adding a folder to a given XNAT host.

        @param _dst: The uri of the folder to put into the XNAT host.
        @type _dst: string
        """
        if not _dst.startswith(self.host + '/data'):
            _dst = self.host + '/data' + _dst
        _dst = str(_dst).encode('ascii', 'ignore')


        
        #-------------------- 
        # Make folder accodringly.
        #--------------------        
        response = self.__httpsRequest('PUT', _dst)



        #-------------------- 
        # Get and return the response from the connetion.
        #-------------------- 
        #print ("XnatIo (makeFolder)", response.read())
        return response


    
    
    def putFile(self, _src, _dst, delExisting = True):
        """ 
        Upload a file to an XNAT host.  Utilizes the internal
        method __httpsRequest.

        @param _src: The local source file to upload to.
        @type: string

        @param _dst: The XNAT dst to upload to.
        @type: string      

        @param delExisting: Delete the exsting _dst if it exists in the XNAT host.
            Defaults to 'True'.
        @type: boolean   
        """

        
        #-------------------- 
        # Read '_src' data.
        #-------------------- 
        f = open(_src, 'rb')
        filebody = f.read()
        f.close()



        #-------------------- 
        # Delete existing _dst from XNAT host.
        #-------------------- 
        if delExisting:
            self.__httpsRequest('DELETE', _dst, '')
        #print "%s Uploading\nsrc: '%s'\n_dst: '%s'"%(_src, _dst)


        
        #-------------------- 
        # Clean '_dst' string and endcode
        #-------------------- 
        _dst = XnatIo.uri.makeXnatUrl(self.host, _dst)
        _dst = str(_dst).encode('ascii', 'ignore')


        
        #-------------------- 
        # Put the file in XNAT using the internal '__httpsRequest'
        # method.
        #-------------------- 
        response = self.__httpsRequest('PUT', _dst, filebody, {'content-type': 'application/octet-stream'})
        return response
                
    
    
    def delete(self, _uri):
        """ 
        Deletes a given file or folder from an XNAT host.

        @param _uri: The XNAT URI to run the "DELETE" method on.
        @type: string
        """
        print "Deleting %s"%(_uri)
        response =  self.__httpsRequest('DELETE', _uri, '')
        


        
    def exists(self, _uri):
        """ 
        Determines whether a file exists
        on an XNAT host based on the '_uri' argument.

        @param _uri: The xnat uri to check if it exists on the XNAT host.
        @type _uri: string

        @return: Whether the file exists.
        @rtype: boolean
        """
        #print "%s %s"%(_uri)

        
        #-------------------- 
        # Query logged files before checking
        #-------------------- 
        if (os.path.basename(_uri) in self.fileDict):
            return True
                

        
        #-------------------- 
        # Clean string
        #-------------------- 
        xnatUrl = XnatIo.uri.makeXnatUrl(self.host, _uri)
        parentDir = XnatIo.uri.getUriAt(xnatUrl, 'files')
        for i in self.__getJson(parentDir):
            if os.path.basename(xnatUrl) in i['Name']:
                return True   
        return False
    

            

    def search(self, searchString):
        """ 
        Utilizes the XNAT search query function
        on all three XNAT levels (projects, subjects and experiments) based on the provided
        'searchString' argument.  Searches through the available
        columns as described below. CASE INSENSITIVE.

        @param searchString: The search query string.
        @type searchString: string

        @return: A dictionary of the results where the key is the XNAT level (projec, subject or experiment).
        @rtype: dict.<string, string>
        """
        resultsDict = {}

        
 
        #-------------------- 
        # Projects, subjects, experiments
        #-------------------- 
        levelTags = {}
        levelTags['projects'] = ['ID', 'secondary_ID',	'name', 'pi_firstname', 'pi_lastname', 'description']
        levelTags['subjects'] = ['ID', 'label']
        levelTags['experiments'] = ['ID', 'label']


        
        #-------------------- 
        # Looping through all of the levels,
        # constructing a searchQuery for each based
        # on the releant columns.
        #--------------------       
        levels = ['projects', 'subjects', 'experiments']
        for level in levels:
            resultsDict[level] = []
            for levelTag in levelTags[level]:
                searchStr = '/%s?%s=*%s*'%(level, levelTag, searchString)
                #
                # Experiments: only search folders with images
                #
                if level == 'experiments':
                    searchStr2 = searchStr + '&xsiType=xnat:mrSessionData'
                    searchStr = searchStr + '&xsiType=xnat:petSessionData'
                    resultsDict[level] = resultsDict[level] + self.__getJson(searchStr2)
                resultsDict[level] = resultsDict[level] + self.__getJson(searchStr)


        
        return resultsDict




    def addEventCallback(self, event, callback):
        """
        Adds a callback for a given event.  
        Callbacks are strored internally as a dictionary of arrays in XnatIo.callbacks.

        @param event: The event descriptor for the callbacks stored in XnatIo.callbacks.  Refer
          to XnatIo.EVENT_TYPES for the list.
        @type event: string

        @param callback: The callback function to enlist.
        @type callback: function

        @raise: Error if 'event' argument is not a valid event type.
        """
        if not event in XnatIo.EVENT_TYPES:
            raise Exception("XnatIo (onEvent): invalid event type '%s'"%(event))
        self.eventCallbacks[event].append(callback)



    def clearEventCallbacks(self):
        """
        As stated.
        """
        for key in self.eventCallbacks:
            self.eventCallbacks[key] = []



    def addToDownloadQueue(self, _src, _dst):
        """
        Adds a file to the download queue.

        @param _src: The source XNAT URL to download form.
        @type: string

        @param _dst: The local dst to download to.
        @type: string
        """
        self.downloadQueue.append({'src': _src, 'dst': _dst})



    def clearDownloadQueue(self):
        """
        As stated.
        """
        #print "CLEAR DOWNLOAD QUEUE"
        self.downloadQueue = []
        self.clearEventCallbacks()
        


        
    def startDownloadQueue(self):
        """
        Begins the the download queue.
        """
        
        self.__runEventCallbacks('downloadQueueStarted') 
        while len(self.downloadQueue):
            if self.downloadQueue[0]['dst'] != None:
                self.getFile(self.downloadQueue[0]['src'], self.downloadQueue[0]['dst'])
        self.__runEventCallbacks('downloadQueueFinished') 
        self.clearDownloadQueue()


            
        

    def inDownloadQueue(self, _src):
        """
        Determines whether a given source is in the download queue.

        @param _src: The source XNAT URL to check if it's in the download queue.
        @type: string

        @return: boolean
        @rtype: string
        """
        for dl in self.downloadQueue:
            if _src in dl['src']:
                return True
        return False



    
    def removeFromDownloadQueue(self, _src):
        """
        Removes a given source from the download queue.

        @param _src: The source XNAT URL to remove from the download queue.
        @type: string
        """
        for dl in self.downloadQueue:
            if _src in dl['src']:
                self.downloadQueue.pop(self.downloadQueue.index(dl))
                return
        

            
    def cancelDownload(self, _src):
        """ 
        Cancels a download.

        Set's the download state to 0.  The open buffer in the 'GET' method
        will then read this download state, and cancel out.

        @param _src: The source XNAT URL to cancel the download from.
        @type: string
        """
        print ("\n\nCancelling download of '%s'"%(_src))

        #-------------------- 
        # Pop from queue
        #--------------------
        self.removeFromDownloadQueue(_src) 

                
        #-------------------- 
        # Clear queue if there is nothing
        # left in it.
        #-------------------- 
        if len(self.downloadQueue) == 0:
            self.clearDownloadQueue()


        #-------------------- 
        # Callbacks
        #-------------------- 
        self.__runEventCallbacks('downloadCancelled', _src)    


        
        
    def __runEventCallbacks(self, event, *args):
        """
        'Private' function that runs the callbacks based on the provided 'event' argument.

        @param event: The event descriptor for the callbacks stored in XnatIo.callbacks.  Refer
          to XnatIo.EVENT_TYPES for the list.
        @type event: string

        @param *args: The arguments that are necessary to run the event callbacks.

        @raise: Error if 'event' argument is not a valid event type.
        """
        if not event in self.EVENT_TYPES:
            raise Exception("XnatIo (onEvent): invalid event type '%s'"%(event))
        for callback in self.eventCallbacks[event]:
            callback(*args)




    def __httpsRequest(self, method, _uri, body='', headerAdditions={}):
        """ 
        Makes httpsRequests to an XNAT host using RESTful methods.

        @param method: The request method to run ('GET', 'PUT', 'POST', 'DELETE').
        @type: string

        @param _uri: The XNAT uri to run the request on.
        @type: string      

        @param body: The body contents of the request.  Defaults to an empty string.
        @type: string

        @param headerAdditions: The additional header dictionary to add to the request.
        @type: dict
        """

        #-------------------- 
        # Make the request arguments
        #-------------------- 
        url = XnatIo.uri.makeXnatUrl(self.host, _uri)
        request = urllib2.Request(url)
        host = request.get_host()


        #-------------------- 
        # For local uris
        #
        # A ':' indicates the port...
        #-------------------- 
        if ':' in host:
            connection = httplib.HTTPConnection(host)
        else:
            connection = httplib.HTTPSConnection(host) 

        header = dict(self.authHeader.items() + headerAdditions.items())

        

        #-------------------- 
        # Conduct REST call
        #-------------------- 
        connection.request(method.upper(), request.get_selector(), body=body, headers=header)
        return connection.getresponse()

        


    def __downloadFailed(self, _src, _dst, dstFile, message):
        """ 
        Opens a QMessageBox informing the user
        of the failed download.
  
        @param _src: The source of the download file.
        @type _src: string

        @param _dst: The destination of the download file.
        @type _dst: string
      
        @param message: The message to indicated that the download failed.
        @type message: string
        """
        self.removeFromDownloadQueue(_src)
        dstFile.close()
        os.remove(dstFile.name)
        print "\nFailed to download '%s'.  Error: %s"%(_src, message)
        self.__runEventCallbacks('downloadFailed', _src, _dst, message)

    

    
    def __getFile_httplib(self, _src, _dst):
        """
        NOT the preferred method for getting files from XNAT.

        This method exists as a backup to the urllib2-based '__getFile' 
        function of XnatIo.  It's currently not utilized by XnatIo.
        
        urllib2.urlopen + reponse.read is the preferred method for getting files because 
        files can be downloaded in chunks (to allow for a progress
        indicator) as opposed to one grab, which httplib.HTTPSConnection does.

        @param _src: The _src url to run the GET request on.
        @type _src: string

        @param _dst: The destination path of the GET (for getting files).
        @type _dst: string

        @param dstFile: The python 'file' classType to run the write the file to.
        @type dstFile: file
        """
                
        #-------------------- 
        # Pre-download callbacks
        #-------------------- 
        self.__runEventCallbacks('downloadStarted', _src, -1)
        self.__runEventCallbacks('downloading', _src, 0)


        
        #-------------------- 
        # Download
        #-------------------- 
        response = self.__httpsRequest('GET', _src)
        data = response.read()  
        with open(_dst, 'wb') as f:
            f.write(data)     



        #-------------------- 
        # Post-download callbacks
        #--------------------     
        self.removeFromDownloadQueue(_src)
        self.__runEventCallbacks('downloadFinished', _src)
        
                    



    
    def __getFile_urllib(self, _src, _dst):
        """ 
        This is the preferred method for getting files from XNAT.

        This method is in place for the main purpose of downlading
        a given source in packets (buffers) as opposed to one large file.
        
        It should be noted that the urllib2 manager-based convention of authentication 
        returns a 401 error if the server does not follow the HTTP authentication standard
        (some CNDA machines are like this):
       
            #-------------------- 
            # RETURNS AN ERROR
            #-------------------- 
            >>> passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
            >>> passman.add_password(None, _xnatSrc, self.user, self.password)
            >>> authhandler = urllib2.HTTPBasicAuthHandler(passman)
            >>> opener = urllib2.build_opener(authhandler)
            >>> urllib2.install_opener(opener)
            >>> response = urllib2.urlopen(_xnatSrc)

       
        A workaround was found for this issue.  It simply includes the authentication header
        in the request, and we use urllib2 to open the request.

            #-------------------- 
            # WORKS
            #-------------------- 
            >>> request = urllib2.Request(xnatUrl)
            >>> request.add_header("Authorization", self.authHeader['Authorization'])
            >>> response = urllib2.urlopen(request)

        

        @see:
        U{http://www.voidspace.org.uk/python/articles/authentication.shtml}
        U{http://blog.oneiroi.co.uk/python/python-urllib2-basic-http-authentication/}
        U{http://stackoverflow.com/questions/5131403/http-basic-authentication-doesnt-seem-to-work-with-urllib2-in-python}
        U{http://stackoverflow.com/questions/635113/python-urllib2-basic-http-authentication-and-tr-im/4188709#4188709}
           

        @param _src: The _src url to run the GET request on.
        @type _src: string

        @param _dst: The destination path of the GET (for getting files).
        @type _dst: string         
        """
        
        #-------------------- 
        # Open the local destination file 
        # so that it can start reading in the buffers.
        #-------------------- 
        try:
            dstDir = os.path.dirname(_dst)        
            if not os.path.exists(dstDir):
                os.makedirs(dstDir)
            dstFile = open(_dst, "wb")
        except Exception, e:
            self.__downloadFailed(_src, _dst, dstFile, str(e))
            return



        #-------------------- 
        # Construct the request and authentication handler
        #-------------------- 
        xnatUrl = XnatIo.uri.makeXnatUrl(self.host, _src)
        request = urllib2.Request(xnatUrl)
        request.add_header("Authorization", self.authHeader['Authorization'])

        

        #-------------------- 
        # Get the response from the XNAT host.
        #-------------------- 
        try:
            response = urllib2.urlopen(request)



            
        #-------------------- 
        # If the urllib2 version fails then use httplib.
        # See get_httplib for more details.
        #-------------------- 
        except urllib2.HTTPError, e:
            #print str(e)
            #print _src, _dst
            #print d
            self.__downloadFailed(_src, _dst, dstFile, str(e))
            return


        #-------------------- 
        # Get the content size, first by checking log, then by reading header
        #-------------------- 
        self.downloadTracker['downloadedSize']['bytes'] = 0   
        self.downloadTracker['totalDownloadSize'] = self.getFileSize(xnatUrl)
        if not self.downloadTracker['totalDownloadSize']['bytes']:
            # If not in log, read the header
            if response.headers and "Content-Length" in response.headers:
                self.downloadTracker['totalDownloadSize']['bytes'] = int(response.headers["Content-Length"])  
                self.downloadTracker['totalDownloadSize']['MB'] =  XnatIo.utils.bytesToMB(self.downloadTracker['totalDownloadSize']['bytes'])

        
        #-------------------- 
        # Start the buffer reading cycle by
        # calling on the buffer_read function above.
        #-------------------- 
        bytesRead = self.__bufferRead(xnatUrl, dstFile, response)
        dstFile.close()

    


    def __bufferRead(self, _src, dstFile, response, bufferSize=8192):
        """
        Downloads files by a constant buffer size.

        @param _src: The _src url to run the GET request on.
        @type _src: string

        @param dstFile: The open python file to write the buffers to.
        @type dstFile: file  

        @param response: The urllib2 response to read buffers from.
        @type response: A file-like object. 
            @see: U{http://docs.python.org/2/library/urllib2.html}

        @param bufferSize: Buffer size to read.  Defaults to the standard 8192.
        @type bufferSize: integer

        @return: The total downloaded bytes.  
        @rtype: intengerhttp://docs.python.org/2/library/urllib2.html
        """
        
        
        #--------------------
        # Pre-download callbacks
        #--------------------
        size = self.downloadTracker['totalDownloadSize']['bytes'] if self.downloadTracker['totalDownloadSize']['bytes'] else -1
        self.__runEventCallbacks('downloadStarted', _src, size)
                                  
 
            
        #--------------------
        # Define the buffer read loop
        #--------------------
        while 1:     
                       
            #
            # If DOWNLOAD CANCELLED
            #              
            if not self.inDownloadQueue(_src):
                print "Cancelling download of '%s'"%(_src)
                dstFile.close()
                os.remove(dstFile.name)
                self.__runEventCallbacks('downloadCancelled', _src)
                break


            #
            # If DOWNLOAD FINISHED
            #
            buffer = response.read(bufferSize)
            if not buffer: 
                # Pop from the queue
                self.removeFromDownloadQueue(_src)
                self.__runEventCallbacks('downloadFinished', _src)
                break

            
            #
            # Otherwise, Write buffer chunk to file
            #
            dstFile.write(buffer)

            #
            # And update progress indicators
            #
            self.downloadTracker['downloadedSize']['bytes'] += len(buffer)
            self.__runEventCallbacks('downloading', _src, self.downloadTracker['downloadedSize']['bytes'])
 
                
        return self.downloadTracker['downloadedSize']['bytes']



            
        
    def __getJson(self, _uri):
        """ 
        Returns a json object from a given XNAT URI using
        the internal method '__httpsRequest'.

        @param _uri: The xnat uri to retrieve the JSON object from.
        @type _uri: string

        @return: A dictionary of the JSON result.
        @rtype: dict
        """

        #-------------------- 
        # Get the response from httpRequest
        #--------------------     
        xnatUrl = XnatIo.uri.makeXnatUrl(self.host, _uri)
        response = self.__httpsRequest('GET', xnatUrl).read()
        

        
        #-------------------- 
        # Try to load the response as a JSON...
        #-------------------- 
        try:
            return json.loads(response)['ResultSet']['Result']
        except Exception, e:
            self.__runEventCallbacks('jsonError', self.host, self.username, response)



    class utils(object):
        """
        Utility methods for XnatIo.
        """   
        @staticmethod
        def bytesToMB(bytes):
            """ 
            Converts bytes to MB, retaining the number type.
            
            @param bytes: The bytes to convert to MB.
            @type: number (integer)
            
            @return: The numerical value of bytes converted to MB.
            @rtype: float
            """
            bytes = int(bytes)
            mb = str(bytes/(1024*1024.0)).split(".")[0] + "." + str(bytes/(1024*1024.0)).split(".")[1][:2]
            return float(mb)



    class uri(object):
        """
        URI/URL methods for XnatIo specific to XNAT interaction.
        """                
    
        QUERY_FILTERS = {
            'accessible' : 'accessible=true',
            'imagesonly' : 'xsiType=xnat:imageSessionData',
        }


        @staticmethod
        def getUriAt(_uri, level):
            """ 
            Returns the XNAT path from '_uri' at the 
            provided 'level' by splicing '_uri' accordingly 
            and then adding 'level' as the suffix.
            
            @param _uri: The xnat uri to retrieve the JSON object from.
            @type _uri: string
            
            @param level: The the XNAT level to splice _uri at, then append to
                the spliced string.
            @type level: string

            @return: The spliced uri with 'level' as a suffix.
            @rtype: string
            
            @raise: Error if level is not found in the _uri.
            """
            #print "%s %s"%(, _uri, level)
            if not level.startswith('/'):
                level = '/' + level
            if level in _uri:
                return  _uri.split(level)[0] + level
            else:
                raise Exception("Invalid get level '%s' parameter: %s"%(_uri, level))



        @staticmethod
        def cleanUri(uri):
            """ 
            Removes any double-slashes
            with single slashes.  Removes the 
            last character if the string ends
            with a '/'
            
            @param uri: The xnat URL to clean.
            @type uri: string


            @return: The cleaned uri.
            @rtype: string            
            """
            if not uri.startswith("/"):
                uri = "/" + uri
            uri = uri.replace("//", "/")
            if uri.endswith("/"):
                uri = uri[:-1]
            return uri



        @staticmethod
        def applyQueryArguments(_uri, queryArgs):
            """ 
            Using the  XnatIo.QUERY_FILTERS,
            appends the relevant arguments to a given queryURI.  Usually
            for 'xsiType' calls and modifications to query URIs specific
            to a given XNAT level.
            
            @param _uri: The partial or full XNAT query uri
            @type _uri: string

            @param queryArgs: The list of query argument suffixes to apply.
            @type queryArgs: list.<string>
            
            @return: The XNAT query uri with the arguments added to it.
            @rtype: string
            """
            queryArgStr = ''
            for i in range(0, len(queryArgs)):
                queryArgStr += '?' if i == 0 else '&'
                queryArgStr += str(XnatIo.uri.QUERY_FILTERS[queryArgs[i].lower()])
            return _uri + queryArgStr



        @staticmethod
        def makeXnatUrl(host, _url):
            """
            Adds the necessary prefixes to the _url argument
            so as to produce a full XNAT url.
            
            @param _url: The partial or full XNAT query uri
            @type _url: string
            
            @return: The full XNAT url for to run the query on.
            @rtype: string
            """
            
        
            if _url.startswith('/'):
                _url = _url[1:]

            if not _url.startswith(host):
                if _url.startswith('data/'):
                    _url = urljoin(host, _url)
                else:
                    prefixUri = urljoin(host, 'data/archive/')
                    _url = urljoin(prefixUri, _url) 


            #--------------------
            # Remove double slashes
            #--------------------                    
            _url = _url.replace('//', '/')
            if 'http:/' in _url:
                _url = _url.replace('http:/', 'http://')
            elif 'https:/' in _url:
                _url = _url.replace('https:/', 'https://')

            return _url




class XnatGlobals(object):
    """
    XnatGlobals contains static properites relevant to 
    interacting with XNAT.
    """
    
    DEFAULT_XSI_TYPES =  {
        'MR Session': 'xnat:mrSessionData',
        'PET Session': 'xnat:petSessionData',
        'CT Session' : 'xnat:ctSessionData'
    }


    DEFAULT_METADATA =  {
        'LABELS' : [
            'ID',
            'id',
            'name',
            'Name',
            'label',
        ],
        'projects' : [
            'last_accessed_497',
            'ID',
            'id',
            'insert_user',
            'pi',
            'insert_date',
            'description',
            'secondary_ID',
            'pi_lastname',
            'pi_firstname',
            'project_invs',    
            'project_access_img',    
            'user_role_497',    
            'quarantine_status'
            'URI',
        ],
        'subjects' : [
            'ID',
            'label',
            'insert_date',
            'insert_user',
            'totalRecords'
            'project',
            'URI',
        ],
        'experiments' : [
            'ID',
            'label',
            'insert_date',
            'totalRecords',
            'date',
            'project',
            'xsiType',
            'xnat:subjectassessordata/id',
            'URI',
        ],
        'scans' : [
            'series_description',
            'note',
            'type',
            'xsiType',
            'quality',
            'xnat_imagescandata_id',
            'URI',
            'ID'
        ],
        'resources' : [
            'element_name',
            'category',
            'cat_id',
            'xnat_abstractresource_id',
            'cat_desc'
        ],
        'files' : [
            'Size',
            'file_format',
            'file_content',
            'collection',
            'file_tags',
            'cat_ID',
            'URI',
            'Name'
        ],
        'slicer' : [
            'Size',
            'file_format',
            'file_content',
            'collection',
            'file_tags',
            'cat_ID',
            'URI',
            'Name'
        ]
    }


    DEFAULT_XNAT_LEVELS =  ['projects', 'subjects', 'experiments', 'scans', 'slicer', 'files']

    DEFAULT_PATH_DICT = {
        "projects":None, 
        "subjects":None, 
        "experiments":None, 
        "scans":None, 
        "resources":None, 
        "files":None
    }
    
    HIGHEST_FOLDER_ADD_LEVEL  = 'experiments'
    DEFAULT_DATE_TAGS =  [ 'last_accessed_497', 'insert_date']    



    @staticmethod
    def getMetadataByLevel(xnatLevel):
        """ 
        Returns the appropriate tag list by the given
        'xnatLevel' argument.
        
        @param xnatLevel: The pertinent XNAT level to 
            get the default metadat from.
        @type xnatLevel: string

        @rtype: An array of strings referring to the XNAT metadata tags.
        @returns: The relevant XNAT metadata tags for the provided level. 

        @raise If the value of 'xnatLevel' doesn't exist within the default
            XNAT metadata hierarchy.
        """

        if 'projects' in xnatLevel:
            return XnatGlobals.DEFAULT_METADATA['projects']
        elif 'subjects' in xnatLevel:
            return XnatGlobals.DEFAULT_METADATA['subjects']
        elif 'experiments' in xnatLevel:
            return XnatGlobals.DEFAULT_METADATA['experiments']
        elif 'resources' in xnatLevel:
            return XnatGlobals.DEFAULT_METADATA['resources']  
        elif 'scans' in xnatLevel:
            return XnatGlobals.DEFAULT_METADATA['scans']
        elif 'files' in xnatLevel:
            return XnatGlobals.DEFAULT_METADATA['files']
        elif 'Slicer' in xnatLevel:
            return XnatGlobals.DEFAULT_METADATA['slicer'] 
        else:
            raise Exception("Invalid XNAT level: %s"%(xnatLevel))
