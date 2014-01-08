import os
import sys
import shutil
import time
import math
import urllib2
from urlparse import urljoin
import string    
import httplib
import codecs
from os.path import abspath, isabs, isdir, isfile, join
from base64 import b64encode
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
    @author: Sunil Kumar (sunilk@mokacreativellc.com)

    XnatIo is a lightweight communicator class to XNAT. XnatIo uses httplib REST calls to 
    send/receive commands and files to XNAT. Since input is usually string-based, there are 
    several utility methods in this class to clean up strings for input to httplib / urllib2.


    Example Usage:
    
    >>> from XnatIo import *
    >>> xnatIo = XnatIo()
    >>> xnatIo.setup('http://central.xnat.org', 'sunilk', 'sunilk')
    >>> contents = xnatIo.getFolder('projects')
    >>> print contents[111]['ID']
    XNATSlicerTest    


    """



    def __init__(self):
        """ 
        Parent init.
        """
        self.downloadQueue = []        
        self.callbacks = {
            'downloadCancelled': [],
            'downloading': [],
            'downloadStarted': [],
            'downloadFinished': [],
            'downloadFailed': [],
            'jsonError': []
        }


        

    def setCallback(self, callbackKey, callback):
        """
        """
        self.callbacks[callbackKey].append(callback)


        
        
    def runCallbacks(self, callbackKey, *args):
        """
        """
        for callback in self.callbacks[callbackKey]:
            callback(*args)
            
        
        
        
    def setup(self, host, user, password):
        """ 
        Setup function.  Initializes the internal variables. 
        A 'setup' paradigm is employed, as opposed
        to an 'init' paradim, because the XnatIo object is created, but
        not logged into until the user enters the relevant information.
        """

        #-------------------
        # Set relevant variables (all required)
        #-------------------
        self.projectCache = None
        self.host = host
        self.user = user
        self.password = password


        
        #-------------------
        # Make tracking dictionary for download modal.
        #-------------------
        self.downloadTracker = {
            'totalDownloadSize': {'bytes': None, 'MB': None},
            'downloadedSize': {'bytes': None, 'MB': None},
        }


        #-------------------
        # Make relevant variables for httpsRequests
        #-------------------        
        self.userAndPass = b64encode(b"%s:%s"%(self.user, self.password)).decode("ascii")
        self.authenticationHeader = { 'Authorization' : 'Basic %s' %(self.userAndPass) }
        self.fileDict = {};


        

    @property
    def queryArguments(self):
        """ For appending to a URL when querying for metadata.
        """
        return {'accessible' : 'accessible=true',
                'imagesonly' : 'xsiType=xnat:imageSessionData',
                }




    
    def getFile(self, src, dst): 
        """ 
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
        if os.path.exists(dst):
            os.remove(dst)
  
                    
        
        #-------------------------
        # If we're downloading a single file, go ahead and get it
        # by calling the internal 'get' function.
        #-------------------------
        self.get(src, dst)



    
    
    def upload(self, localSrcUri, remoteDstUri, delExisting = True):
        """ Upload a file to an XNAT host using Python's 'urllib2' library.
            The argument 'localSrcUri' provides the relvant path to
            the file that will be uploaded.  The argument 'remoteDstUri'
            provides the relevant path to the destination on a given
            XNAT host.  
        """

        
        #-------------------- 
        # Read 'localSrcUri' data.
        #-------------------- 
        f = open(localSrcUri, 'rb')
        filebody = f.read()
        f.close()



        #-------------------- 
        # Delete existing remoteDstUri from XNAT host.
        #-------------------- 
        if delExisting:
            self.httpsRequest('DELETE', remoteDstUri, '')
        ##print "%s Uploading\nsrc: '%s'\nremoteDstUri: '%s'"%(localSrcUri, remoteDstUri)


        
        #-------------------- 
        # Clean 'remoteDstUri' string and endcode
        #-------------------- 
        if not remoteDstUri.startswith(self.host + '/data'):
            remoteDstUri = self.host + '/data' + remoteDstUri
        ##print remoteDstUri
        remoteDstUri = str(remoteDstUri).encode('ascii', 'ignore')


        
        #-------------------- 
        # Put the file in XNAT using the internal 'httpsRequest'
        # method.
        #-------------------- 
        response = self.httpsRequest('PUT', remoteDstUri, filebody, {'content-type': 'application/octet-stream'})
        return response
        

        
        
    def httpsRequest(self, restMethod, xnatUri, body='', headerAdditions={}):
        """ Allows the user to make httpsRequests to an XNAT host
            using RESTful methods provided in the argument 'restMethod'.  The argument
            'xnatUri' is the URI that points to a given location to conduct the
            rest call.  This could be a file or folder using the compatible
            REST methods.
        """

        #-------------------- 
        # Uppercase the REST method string.
        #-------------------- 
        restMethod = restMethod.upper()


        
        #-------------------- 
        # Clean target URL
        #-------------------- 
        prepender = self.host.encode("utf-8") + '/data'
        url =  prepender +  xnatUri.encode("utf-8") if not prepender in xnatUri else xnatUri


        
        #-------------------- 
        # Get request using 'urllib2'
        #-------------------- 
        req = urllib2.Request (url)


        
        #-------------------- 
        # Get connection
        #-------------------- 
        connection = httplib.HTTPSConnection (req.get_host ()) 


        
        #-------------------- 
        # Merge the authentication header with any other headers
        #-------------------- 
        header = dict(self.authenticationHeader.items() + headerAdditions.items())

        

        #-------------------- 
        # Conduct REST call
        #-------------------- 
        connection.request(restMethod, req.get_selector (), body = body, headers = header)
        ##print ('%s httpsRequest: %s %s')%(, restMethod, url)


        
        #-------------------- 
        # Return response
        #-------------------- 
        return connection.getresponse ()



    
    
    def delete(self, xnatUri):
        """ Deletes a given file or folder from an XNAT host
            based on the 'xnatUri' argument.  Calls on the internal
            'httpsRequest' RESTfully.
        """
        #print "Deleting %s"%(xnatUri)
        response =  self.httpsRequest('DELETE', xnatUri, '')
        #print response.read()




    def bytesToMB(self, bytes):
        """ Converts bytes to MB.  Returns a float.
        """
        bytes = int(bytes)
        mb = str(bytes/(1024*1024.0)).split(".")[0] + "." + str(bytes/(1024*1024.0)).split(".")[1][:2]
        return float(mb)
        


        
    def downloadFailed(self, message):
        """ Opens a QMessageBox informing the user
            of the faile download.
        """
        self.runCallbacks('downloadFailed', message)

    

    
    def get_httplib(self, _src, _dst, dstFile):
        """
        This method exists as a backup for the actual "get" function of XnatIo.
        The reason it exists is because certain servers, like the CNDA, do not like
        the way urllib2 communicates with it with the 'GET' calls (it kicks back
        an authentication error).
        
        The downside of using httplib to 'GET' is that we can't read buffers, 
        and therefore have an accurate progress indicator.

        @param _src: The _src url to run the GET request on.
        @type _src: string
        """
                
        #
        # Get the file using httpsRequest and GET
        #
        httpString = "\nXnatIo: urllib2 'get' failed.  Attempting httplib version.  "
        httpString += "Usually this is the result of certain servers (like CNDA) not liking python urllib2's communication methods."
        print httpString
        self.runCallbacks('downloadStarted', _src, -1)
        self.runCallbacks('downloading', _src, 0)
        response = self.httpsRequest('GET', _src)
        data = response.read()           
        dstFile.close()
        self.removeFromDownloadQueue(_src)
        self.runCallbacks('downloadFinished', _src)
            
                
        #
        # Write the response data to file.
        #
        with open(_dst, 'wb') as f:
            f.write(data)
                    
        print "\nhttplib download succeeded."



    
    def get(self, _src, _dst):
        """ This method is in place for the main purpose of downlading
            a given Uri in packets (buffers) as opposed to one large file.
            If, for whatever reason, a packet-based download cannot occur,
            (say the server doesn't like urllib2)
            the function then resorts to a standard 'GET' call, via 'httpsRequest'
            which will download everything without a progress indicator.  This is bad UX,
            but still necessary.
                       
        """

        print "XnatIo: GET:", _src, '\n', _dst

        
        #-------------------- 
        # Set the src URI based on the 
        # internal variables of XnatIo.
        #-------------------- 
        xnatUrl = self.makeXnatUrl(_src)


        

        #-------------------- 
        # Construct the authentication handler
        #-------------------- 
        passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passman.add_password(None, xnatUrl, self.user, self.password)
        authhandler = urllib2.HTTPBasicAuthHandler(passman)
        opener = urllib2.build_opener(authhandler)
        urllib2.install_opener(opener)


        
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
            self.downloadFailed(str(e))
            return
      


        #-------------------- 
        # Get the response URL from the XNAT host.
        #-------------------- 
        errorString = ""
        try:
            response = urllib2.urlopen(xnatUrl)


            
        #-------------------- 
        # If the urllib2 version fails then use httplib.
        # See get_httplib for more details.
        #-------------------- 
        except Exception, e:
            errorString += str(e) + "\n"
            print errorString
            self.get_httplib(xnatUrl, _dst, dstFile)
            return
            try:                
                self.get_httplib(xnatUrl, _dst, dstFile)
                return
                
            except Exception, e2:
                errorString += str(e2)
                self.downloadFailed(errorString)
                return


        
        #-------------------- 
        # Get the content size, first by checking log, then by reading header
        #-------------------- 
        self.downloadTracker['downloadedSize']['bytes'] = 0   
        self.downloadTracker['totalDownloadSize'] = self.getSize(xnatUrl)
        if not self.downloadTracker['totalDownloadSize']['bytes']:
            # If not in log, read the header
            if response.headers and "Content-Length" in response.headers:
                self.downloadTracker['totalDownloadSize']['bytes'] = int(response.headers["Content-Length"])  
                self.downloadTracker['totalDownloadSize']['MB'] = self.bytesToMB(self.downloadTracker['totalDownloadSize']['bytes'])

        
        #-------------------- 
        # Start the buffer reading cycle by
        # calling on the buffer_read function above.
        #-------------------- 
        bytesRead = self.bufferRead_(xnatUrl, dstFile, response)
        dstFile.close()

    


    def bufferRead_(self, _src, dstFile, response, bufferSize=8192):
        """
        Downloads files by a constant buffer size.
        
        Define the starter function for reading a file from
        XNAT to a local destination as packets.  Contained within  
        is the loop that continuously reads buffers from XNAT until all
        are read. 
        
        For showing the progress bar as we download, we also 
        need to set it up and update it accordingly.
        """
        
        
        #--------------------
        # Pre-download callbacks
        #--------------------
        size = self.downloadTracker['totalDownloadSize']['bytes'] if self.downloadTracker['totalDownloadSize']['bytes'] else -1
        self.runCallbacks('downloadStarted', _src, size)
                                  
 
            
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
                self.runCallbacks('downloadCancelled', _src)
                break


            #
            # If DOWNLOAD FINISHED
            #
            buffer = response.read(bufferSize)
            if not buffer: 
                # Pop from the queue
                self.removeFromDownloadQueue(_src)
                self.runCallbacks('downloadFinished', _src)
                break

            
            #
            # Otherwise, Write buffer chunk to file
            #
            dstFile.write(buffer)

            #
            # And update progress indicators
            #
            self.downloadTracker['downloadedSize']['bytes'] += len(buffer)
            self.runCallbacks('downloading', _src, self.downloadTracker['downloadedSize']['bytes'])
 
                
        return self.downloadTracker['downloadedSize']['bytes']



            
        
    def getJson(self, xnatUri):
        """ Returns a json object from a given XNATURI using
            the internal method 'httpsRequest'.
        """

        #-------------------- 
        # Get the response from httpRequest
        #--------------------     
        xnatUri = self.makeXnatUrl(xnatUri)
        response = self.httpsRequest('GET', xnatUri).read()
        ##print "%s %s"%(, xnatUri)
        ###print "Get JSON Response: %s"%(response)


        
        #-------------------- 
        # Try to load the response as a JSON...
        #-------------------- 
        try:
            return json.loads(response)['ResultSet']['Result']


        
        #-------------------- 
        # If that fails, kick back error...
        #-------------------- 
        except Exception, e:
            ##print "%s login error to host '%s'!"%(, self.host)
            self.runCallbacks('jsonError', self.host, self.user, response)
            



    
    
    def getXnatUriAt(self, xnatUri, level):
        """ Returns the XNAT path from 'xnatUri' at the 
            provided 'level' by splicing 'xnatUri' accordingly.
        """
        ##print "%s %s"%(, xnatUri, level)
        if not level.startswith('/'):
            level = '/' + level
        if level in xnatUri:
            return  xnatUri.split(level)[0] + level
        else:
            raise Exception("Invalid get level '%s' parameter: %s"%(xnatUri, level))

        

        
    def fileExists(self, fileUri):
        """ Determines whether a file exists
            on an XNAT host based on the 'fileUri' argument.
        """
        ##print "%s %s"%(fileUri)

        #-------------------- 
        # Query logged files before checking
        #-------------------- 
        if (os.path.basename(fileUri) in self.fileDict):
            return True
                

        
        #-------------------- 
        # Clean string
        #-------------------- 
        parentDir = self.getXnatUriAt(fileUri, 'files');

        

        #-------------------- 
        # Parse result dictionary and 
        # return the boolean.
        #-------------------- 
        for i in self.getJson(parentDir):
            if os.path.basename(fileUri) in i['Name']:
                return True   
        return False
    


    
    def getSize(self, fileUri):
        """ Retrieves a tracked file's size and 
            converts it to MB based on the 'self' variable
            'fileDict' which contains the raw byte size 
            of the given file.
        """
        ##print "%s %s"%(, fileUri)
        #--------------------
        # Query the tracked files by the name
        # of the fileUri.
        #--------------------
        bytes = 0
        fileName = os.path.basename(fileUri)
        if fileName in self.fileDict:
            bytes = int(self.fileDict[fileName]['Size'])
            return {"bytes": (bytes), "MB" : self.bytesToMB(bytes)}

        return {"bytes": None, "MB" : None}


    
    
    def applyQueryArgumentsToUri(self, queryUri, queryArguments):
        """ Using the static variable self.queryArguments dictionary,
            appends the relevant arguments to a given queryURI.  Usually
            for 'xsiType' calls and modifications to query URIs specific
            to a given XNAT level.
        """
        queryArgumentstring = ''
        for i in range(0, len(queryArguments)):
            if i == 0:
                queryArgumentstring += '?'
            else:
                queryArgumentstring += '&'
            queryArgumentstring += self.queryArguments[queryArguments[i].lower()]
        return queryUri + queryArgumentstring
        



    
    def makeXnatUrl(self, queryUri):
        """
        Adds the necessary prefixes to the queryUri argument
        so as to produce a full XNAT url to run a query on.

        @param queryUri: The partial or full XNAT query uri
        @type queryUri: string

        @return: The full XNAT url for to run the query on.
        @rtype: string
        """
        if queryUri.startswith('/'):
            queryUri = queryUri[1:]

        if not queryUri.startswith(self.host):
            if queryUri.startswith('data/'):
                queryUri = urljoin(self.host, queryUri)
            else:
                prefixUri = urljoin(self.host, 'data/archive')
                queryUri = urljoin(prefixUri, queryUri) 
        
        return queryUri




    def getFolder(self, queryUris, metadataTags = None, queryArguments = None):   
        """ Returns the contents of a given folder provided in the arguments
            'queryUris'.  Returns an object based on the 'metadataTags' argument
            that the 'queryUri' gets return.  The 'queryArguments' parameter
            deals generally with fitering certain contents within a given folder. 
            For instance, to get projects only the user has access to, the URI needs
            to be appended with '?accessible=True'.
        """

        returnContents = {}


        
        #-------------------- 
        # Differentiate between a list of paths
        # and once single path (string) -- make all a list
        #-------------------- 
        if isinstance(queryUris, basestring):
           queryUris = [queryUris]


           
        #-------------------- 
        # Differentiate between a list of queryArguments
        # and one single queryArgument (string) -- make all a list
        #-------------------- 
        if isinstance(queryArguments, basestring):
           queryArguments = [queryArguments]

           
           
        #-------------------- 
        # Acquire contents via 'self.getJson'
        #-------------------- 
        contents = []
        for queryUri in queryUris:
            newQueryUri = queryUri
            
                
            #
            # Apply query arguments.
            #
            if queryArguments:
                newQueryUri = self.applyQueryArgumentsToUri(queryUri, queryArguments)
                
                ##print "%s query path: %s"%(, newQueryUri)
            #
            # Get the JSON
            #
            json = self.getJson(newQueryUri)
    
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
            if queryUri.endswith('/projects'):
                self.projectCache = contents


                ##print "CONTENTS", contents
        #-------------------- 
        # Exit out if there are non-Json or XML values.
        #-------------------- 
        if str(contents).startswith("<?xml"): return [] # We don't want text values

        

        #-------------------- 
        # Get other attributes with the contents 
        # for metadata tracking.
        #-------------------- 
        for content in contents:
            if metadataTags:
                for metadataTag in metadataTags:
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
        for queryUri in queryUris:
            queryUri = queryUri.replace('//', '/')
            if queryUri.endswith('/files'):
                for content in contents:
                    # create a tracker in the fileDict
                    ##print "\n\nCONTENT", content, queryUri    
                    self.fileDict[content['Name']] = content
                ##print "%s %s"%(, self.fileDict)
            elif queryUri.endswith('/projects'):
                self.projectCache = returnContents


                
        #-------------------- 
        # Return the contents of the folder as a
        # dictionary of lists
        #-------------------- 
        return returnContents



    
    def getResources(self, folder):
        """ Gets the contents of a 'resources' folder
            in a given XNAT host.  'resources' folders 
            demand a bit more specifity in the metadata manipulation.
            Furthermore, 'resources' folders are frequently accessed
            as part of the Slicer file location within an 'experiment'.
        """

        #-------------------- 
        # Get the resource JSON
        #-------------------- 
        folder += "/resources"
        resources = self.getJson(folder)
        ##print "%s %s"%(, folder)
        ##print  + " Got resources: '%s'"%(str(resources))


        
        #-------------------- 
        # Filter the JSONs
        #-------------------- 
        resourceNames = []
        for r in resources:
            if 'label' in r:
                resourceNames.append(r['label'])
                ##print ( +  "FOUND RESOURCE ('%s') : %s"%(folder, r['label']))
            elif 'Name' in r:
                resourceNames.append(r['Name'])
                ##print ( +  "FOUND RESOURCE ('%s') : %s"%(folder, r['Name']))                
            
            return resourceNames




    def getItemValue(self, XnatItem, attr):
        """ Retrieve an item by one of its attributes
        """

        #-------------------- 
        # Clean string
        #-------------------- 
        XnatItem = self.cleanUri(XnatItem)
        ##print "%s %s %s"%(, XnatItem, attr)


        
        #-------------------- 
        # Parse json
        #-------------------- 
        for i in self.getJson(os.path.dirname(XnatItem)):
            for key, val in i.iteritems():
                if val == os.path.basename(XnatItem):
                    if len(attr)>0 and (attr in i):
                        return i[attr]
                    elif 'label' in i:
                        return i['label']
                    elif 'Name' in i:
                        return i['Name']
 



                    
    def cleanUri(self, fileUri):
        """ Removes any double-slashes
            with single slashes.  Removes the 
            last character if the string ends
            with a '/'
        """
        if not fileUri.startswith("/"):
            fileUri = "/" + fileUri
        fileUri = fileUri.replace("//", "/")
        if fileUri.endswith("/"):
            fileUri = fileUri[:-1]
        return fileUri

    


    def makeFolder(self, remoteDstUri):
        """ Function for adding a folder to a given XNAT host.
        """
        
        #-------------------- 
        # Clean 'remoteDstUri' string and endcode
        #-------------------- 
        if not remoteDstUri.startswith(self.host + '/data'):
            remoteDstUri = self.host + '/data' + remoteDstUri
        remoteDstUri = str(remoteDstUri).encode('ascii', 'ignore')


        
        #-------------------- 
        # Make folder accodringly.
        #--------------------        
        response = self.httpsRequest('PUT', remoteDstUri)



        #-------------------- 
        # Get and return the response from the connetion.
        #-------------------- 
        ##print , "MAKE FOLDER", response.read()
        return response
    

            

    def search(self, searchString):
        """ 
        Utilizes the XNAT search query function
        to on all levels of XNAT based on the provided
        searchString.  Searches through the available
        columns as described below.

        @param searchString: The search query string.
        @type searchString: string
        """

        searchUris = []
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
                    resultsDict[level] = resultsDict[level] + self.getJson(searchStr2)
                resultsDict[level] = resultsDict[level] + self.getJson(searchStr)


        
        return resultsDict




    def clearCallbacks(self):
        """
        """
        for key in self.callbacks:
            self.callbacks[key] = []




    def clearDownloadQueue(self):
        """
        """
        #print "CLEAR DOWNLOAD QUEUE"
        self.downloadQueue = []
        self.clearCallbacks()
        

        
        
    def addToDownloadQueue(self, srcDstDict):
        """
        """
        #print "ADD TO DOWNLOAD QUEUE", srcDstDict, '\n\n'
        self.downloadQueue.append(srcDstDict)



        
    def startDownloadQueue(self, onQueueStarted = None, onQueueFinished = None):
        """
        """
        

        if onQueueStarted:
            onQueueStarted()
            
        print "DOWNLOAD QUEUE", self.downloadQueue

        while len(self.downloadQueue):
            #try:
            if self.downloadQueue[0]['dst'] != None:
                self.getFile(self.downloadQueue[0]['src'], self.downloadQueue[0]['dst'])
            #except Exception, e:
            #    print("\n\nDownload queue warning: '%s'"%(str(e)))

        if onQueueFinished:
            onQueueFinished()

        self.clearDownloadQueue()
        #if slicer and slicer.app: slicer.app.processEvents()

            
        

    def inDownloadQueue(self, _src):
        """
        """
        for dl in self.downloadQueue:
            if _src in dl['src']:
                return True
        return False



    
    def removeFromDownloadQueue(self, _src):
        """
        """
        for dl in self.downloadQueue:
            if _src in dl['src']:
                self.downloadQueue.pop(self.downloadQueue.index(dl))
                return
        

            
    def cancelDownload(self, _src):
        """ Set's the download state to 0.  The open buffer in the 'GET' method
            will then read this download state, and cancel out.
        """
        print "\n\nXNAT IO CANCEL DOWNLOAD", _src

        #-------------------- 
        # Pop from queue
        #--------------------
        self.removeFromDownloadQueue(_src) 


        print "DOWNLOAD QUEUE", self.downloadQueue
                
        #-------------------- 
        # Clear queue if there is nothing
        # left in it.
        #-------------------- 
        if len(self.downloadQueue) == 0:
            self.clearDownloadQueue()


        #-------------------- 
        # Callbacks
        #-------------------- 
        self.runCallbacks('downloadCancelled', _src)    

