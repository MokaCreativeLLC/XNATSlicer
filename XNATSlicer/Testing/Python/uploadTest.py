
def upload(num):

    login = "sunilk"
    password = "ambuSa5t"
    localSrc = "C:/Users/Sunil Kumar/Desktop/test1.mrb"
    f=open(localSrc, 'rb')
    filebody = f.read()
    f.close()
    
    
    #url = 'http://central.xnat.org/data' + XnatDst;
    url = 'http://central.xnat.org/data/projects/XnatSlicerTest/subjects/DE-IDENTIFIED/experiments/UCLA_1297/resources/Slicer/files/test%s.mrb'%(num)
    
    print "*******************URL: ", url
    
    
    req = urllib2.Request (url)
    connection = httplib.HTTPSConnection (req.get_host ())
    #userAndPass = b64encode(b"%s:%s"%(self.user,self.password)).decode("ascii")     
    userAndPass = b64encode(b"%s:%s"%(login, password)).decode("ascii")       
    header = { 'Authorization' : 'Basic %s' %  userAndPass, 'content-type': 'application/octet-stream'}
    
    #connection.request ('PUT', req.get_selector (), body=b64encode(filebody).decode("base64"), headers=header)
    connection.request ('PUT', req.get_selector (), body=(filebody), headers=header)
    response = connection.getresponse ()
    print "response: ", response.read()
    return response


def notWorking():
    import os
    from os.path import abspath, isabs, isdir, isfile, join
    import string
    import sys
    import httplib
    from base64 import b64encode
    
    
    filePath = "C:/Users/Sunil Kumar/Desktop/test1.mrb"
    url = 'http://central.xnat.org/data/projects/XnatSlicerTest/subjects/DE-IDENTIFIED/experiments/UCLA_1297/resources/Slicer/files'
    
    r = requests.get(url, auth=('sunilk', 'ambuSa5t'))
    print r.text
    
    
    
    fl=open(filePath, 'rb')
    filebody = fl.read()
    fl.close()
    
    
    #url = os.path.join(url, "AAAAA.mrb") 
    url = url.replace("\\", '/')
    
    #files = {'file': ('asdfasdf', open(filePath, 'rb'))}
    
    
    r = requests.put(url,  data={'file': open(filePath, 'rb')}, auth=('sunilk', 'ambuSa5t'))
    #r = requests.put(url, files=files, auth=('sunilk', 'ambuSa5t'))
    print r.text






def codecDetermine():
    import codecs
    localSrc = 'C:/Program Files/Slicer 4.2.0-2013-07-31/XnatSlicer/XnatSlicer/XnatSlicerLib/data/temp/upload/test3ad.mrb'
    codecz =  ['ascii', 'big5', 'big5hkscs', 'cp037', 'cp424', 'cp437', 'cp500', 'cp720', 'cp737', 'cp775', 'cp850', 'cp852', 'cp855', 'cp856', 'cp857', 'cp858', 'cp860', 'cp861', 'cp862', 'cp863', 'cp864', 'cp865', 'cp866', 'cp869', 'cp874', 'cp875', 'cp932', 'cp949', 'cp950', 'cp1006', 'cp1026', 'cp1140', 'cp1250', 'cp1251', 'cp1252', 'cp1253', 'cp1254', 'cp1255', 'cp1256', 'cp1257', 'cp1258', 'euc_jp', 'euc_jis_2004', 'euc_jisx0213', 'euc_kr', 'gb2312', 'gbk', 'gb18030', 'hz', 'iso2022_jp', 'iso2022_jp_1', 'iso2022_jp_2', 'iso2022_jp_2004', 'iso2022_jp_3', 'iso2022_jp_ext', 'iso2022_kr', 'latin_1', 'iso8859_2', 'iso8859_3', 'iso8859_4', 'iso8859_5', 'iso8859_6', 'iso8859_7', 'iso8859_8', 'iso8859_9', 'iso8859_10', 'iso8859_13', 'iso8859_14', 'iso8859_15', 'iso8859_16', 'johab', 'koi8_r', 'koi8_u', 'mac_cyrillic', 'mac_greek', 'mac_iceland', 'mac_latin2', 'mac_roman', 'mac_turkish', 'ptcp154', 'shift_jis', 'shift_jis_2004', 'shift_jisx0213', 'utf_32', 'utf_32_be', 'utf_32_le', 'utf_16', 'utf_16_be', 'utf_16_le', 'utf_7', 'utf_8', 'utf_8_sig', 'base64', 'bz2', 'base-64', 'hex', 'quopri', 'zip', 'uu', 'idna', 'mbcs', 'palmos', 'punycode', 'raw_unicode_escape', 'rot_13', 'undefined', 'unicode_escape', 'unicode_internal']
    
    for c in codecz:
        try:
            project_archive = codecs.open(localSrc, "rb", c)
            filebody = project_archive.read()
            print "\n\n SUCCESS WITH CODEC '%s' !!"%(c)
            break
        except Exception, e:
            print "********** Codec: '%s' doesn't work. Error: '%s'"%(c, str(e))


codecDetermine()



## THIS WORKS
def codecTry2(num):
    import codecs
    localSrc = 'C:/Program Files/Slicer 4.2.0-2013-07-31/XnatSlicer/XnatSlicer/XnatSlicerLib/data/temp/upload/test3z.mrb'
    url = 'http://central.xnat.org/data/projects/XnatSlicerTest/subjects/DE-IDENTIFIED/experiments/UCLA_1297/resources/Slicer/files/test%s.mrb'%(num)
    project_archive = codecs.open(localSrc, "rb", "cp037")
    filebody = (project_archive.read())
    
    login = "sunilk"
    password = "ambuSa5t"
    f=open(localSrc, 'rb')
    filebody = f.read()
    f.close()
    
    req = urllib2.Request (url)
    connection = httplib.HTTPSConnection (req.get_host ())
    userAndPass = b64encode(b"%s:%s"%(login, password)).decode("ascii")       
    header = { 'Authorization' : 'Basic %s' %  userAndPass, 'content-type': 'application/octet-stream'}
    connection.request ('PUT', req.get_selector (), body=(filebody), headers=header)
    response = connection.getresponse ()
    print "response: ", response.read()


codecTry2(204)


def codecTry3(num):
    import codecs
    localSrc = 'C:/Program Files/Slicer 4.2.0-2013-07-31/XnatSlicer/XnatSlicer/XnatSlicerLib/data/temp/upload/test3z.mrb'
    xnatDst = 'http://central.xnat.org/data/projects/XnatSlicerTest/subjects/DE-IDENTIFIED/experiments/UCLA_1297/resources/Slicer/files/test%s.mrb'%(num)    
    project_archive = codecs.open(str(localSrc), "rb", "cp037")
    filebody = project_archive.read()        
    login = "sunilk"
    password = "ambuSa5t"
    f=open(localSrc, 'rb')
    filebody = f.read()
    f.close()
    req = urllib2.Request(xnatDst)
    connection = httplib.HTTPSConnection (req.get_host())  
    userAndPass = b64encode(b"%s:%s"%(login, password)).decode("ascii")       
    header = { 'Authorization' : 'Basic %s' %  userAndPass, 'content-type': 'application/octet-stream'}    
    connection.request ('PUT', req.get_selector(), body = filebody, headers = header)
    response = connection.getresponse ()
    print "response: ", response.read()


codecTry3(242)



# MAC
def codecTry3(num):
    import codecs
    import urllib2
    import httplib
    localSrc = '/Users/sunilkumar/Desktop/test1.mrb'
    xnatDst = 'http://central.xnat.org/data/projects/XnatSlicerTest/subjects/DE-IDENTIFIED/experiments/UCLA_1297/resources/Slicer/files/test%s.mrb'%(num)    
    project_archive = codecs.open(str(localSrc), "rb", "cp037")
    filebody = project_archive.read()        
    login = "sunilk"
    password = "ambuSa5t"
    f=open(localSrc, 'rb')
    filebody = f.read()
    f.close()
    req = urllib2.Request(xnatDst)
    connection = httplib.HTTPSConnection (req.get_host())  
    userAndPass = b64encode(b"%s:%s"%(login, password)).decode("ascii")       
    header = { 'Authorization' : 'Basic %s' %  userAndPass, 'content-type': 'application/octet-stream'}    
    connection.request ('PUT', req.get_selector(), body = filebody, headers = header)
    response = connection.getresponse ()
    print "response: ", response.read()


codecTry3(242)
