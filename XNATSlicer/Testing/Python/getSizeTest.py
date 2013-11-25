import json

def httpsRequest(restMethod, url = '', body = '', headerAdditions={}):

    url = 'https://cnda.wustl.edu/data/projects/Jon_temp/subjects/kqa778/experiments/kqa778_mMRtest/scans/1/resources/DICOM/files?format=zip'
    userAndPass = b64encode(b"%s:%s"%('Sunilk', 'ambuSa5t')).decode("ascii")
    authenticationHeader = { 'Authorization' : 'Basic %s' %(userAndPass) }
        
    # Clean REST method
    restMethod = restMethod.upper()
    
    # Clean url
    url = url.encode("utf-8")
    
    # Get request
    req = urllib2.Request (url)
    
    # Get connection
    connection = httplib.HTTPSConnection (req.get_host ()) 
    
    # Merge the authentication header with any other headers
    header = dict(authenticationHeader.items() + headerAdditions.items())
    
    # REST call
    connection.request (restMethod, req.get_selector (), body=body, headers=header)
    
    print "Xnat request - %s %s"%(restMethod, url)
    # Return response
    response = connection.getresponse()
    print response
    return response

a = httpsRequest('GET')


fileUrl = 'https://central.xnat.org/data/archive/projects/XnatSlicerTest/subjects/DE-IDENTIFIED/experiments/UCLA_1297/resources/Slicer/files/test3a.mrb'

def getSize(fileUrl):
    
    if ('/files' in fileUrl):
        parentDir = fileUrl.split('/files')[0] + '/files'
    else:
        raise Exception(" invalid getSize parameter: %s"%(fileUrl))

    response = httpsRequest('GET', parentDir).read()
    result = json.loads(response)['ResultSet']['Result']
    
    for i in result:
        if os.path.basename(fileUrl) in i['Name']:
            print "RES2: ", i['Size']


getSize(fileUrl);




def cndaDownload():
    XnatSrc =  'https://cnda.wustl.edu/data/projects/Jon_temp/subjects/kqa778/experiments/kqa778_mMRtest/scans/1/resources/DICOM/files?format=zip'
    username = 'Sunilk'
    password = 'ambuSa5t'
    password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    top_level_url = "https://cnda.wustl.edu"
    password_mgr.add_password(None, top_level_url, username, password)
    handler = urllib2.HTTPBasicAuthHandler(password_mgr)
    opener = urllib2.build_opener(handler)
    opener.open(XnatSrc)
    urllib2.install_opener(opener)

cndaDownload()




            url = XnatSrc
            userAndPass = b64encode(b"%s:%s"%(self.user, self.password)).decode("ascii")
            authenticationHeader = { 'Authorization' : 'Basic %s' %(userAndPass) }
            
            # Clean REST method
            restMethod = 'GET'
            
            # Clean url
            url = url.encode("utf-8")
            
            # Get request
            req = urllib2.Request (url)
            
            # Get connection
            connection = httplib.HTTPSConnection (req.get_host ()) 
            
            # Merge the authentication header with any other headers
            headerAdditions={}
            header = dict(authenticationHeader.items() + headerAdditions.items())
            
            # REST call
            connection.request (restMethod, req.get_selector (), body= '', headers=header)
            
            print "Xnat request - %s %s"%(restMethod, url)
            # Return response
            response = connection.getresponse()
