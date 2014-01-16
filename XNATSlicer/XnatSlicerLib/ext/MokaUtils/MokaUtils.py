from __future__ import with_statement

# python
import os
import shutil
import zipfile
import inspect
import datetime



class MokaUtils(object):
    """

    """


    class list(object):
        """
        """

        @staticmethod
        def uniqify(_list):
            """ 
            Returns only unique elements in a list, while 
            preserving order: 
            From: http://www.peterbe.com/plog/uniqifiers-benchmark
        
            @param _list: The list to uniqify.
            @return: The uniqified list.
            @rtype: list
            """
            seen = set()
            seen_add = seen.add
            return [ x for x in _list if x not in seen and not seen_add(x)]



        @staticmethod    
        def removeZeroLenStrVals( _list):
            """ As stated.  Removes any string values with 
            zero length within a list.
            """
            for listItem in _list: 
                if (len(listItem)==0):
                    _list.remove(listItem)
                    
            return _list




    class path(object):
        """
        """                
        @staticmethod            
        def addSuffixToFileName( fileName, suffix):
            """ 
            Appends a string to a given filename by
            splitting at the '.' to preserve the extension.
            
            @param fileName: The filename to append the string to.
            @type fileName: string

            @param suffix: The string to append to the filename.
            @type suffix: string
            """
            name = os.path.splitext(fileName)[0]
            ext = os.path.splitext(fileName)[1]
            return name + suffix + ext





        @staticmethod                    
        def abbreviateFileName( fileName, maxLen = 20):
            """ 
            Shortens a given filename to a length provided
            in the argument.  Appends the file with "..." string.
            
            @param fileName: The filename to append the string to.
            @type fileName: string
            
            @return: The shortened filename.
            @rtype: string
            """
            basename = os.path.basename(fileName)
            pre = basename.split(".")[0]
            if len(pre) > maxLen:
                baseneme = pre[0:8] + "..." + pre[-8:] + "." + basename.split(".")[1]
            return basename




        @staticmethod            
        def moveDir(src, dst, deleteSrc = True):
            """ 
            Moves the contents of one directory to another.
            """
            
            newURIs = []


        
            #------------------
            # Make destination dir
            #------------------
            if not os.path.exists(dst): 
                os.mkdir(dst)

            
            
            #------------------
            # Walk through src path.     
            #------------------
            for root, subFolders, files in os.walk(src):
                for file in files:
                    #
                    # Construct src folder, current uri, and dst uri
                    #
                    srcFolder = os.path.basename(src)
                    currURI = os.path.join(root,file)
                    newURI = os.path.join(dst, file)
                    #
                    # Clean up the newURI path string.
                    #
                    try:
                        folderBegin = root.split(srcFolder)[-1] 
                        if folderBegin.startswith("\\"): 
                            folderBegin = folderBegin[1:] 
                        if folderBegin.startswith("/"): 
                            folderBegin = folderBegin[1:] 
                        #
                        # Make the new URIs of the sub directory.
                        #
                        newPath = None
                        if folderBegin and len(folderBegin) > 0:
                            newPath = os.path.join(dst, folderBegin)
                            if not os.path.exists(newPath):
                                os.mkdir(newPath)
                            newURI = os.path.join(newPath, file)
                    except Exception, e: 
                        errorStr = str(e)
                        print ("RootSplit Error: " + errorStr)
                    #
                    # Move the file, and track it             
                    #
                    shutil.move(currURI, newURI)
                    newURIs.append(MokaUtils.path.adjustPathSlashes(newURI))

                 
                
            #------------------
            # If the src path is to be deleted...
            #------------------
            if deleteSrc and not src.find(dst) == -1 and os.path.exists(src):
                shutil.rmtree(src)
                
            return newURIs


        @staticmethod    
        def getAncestorUri( uri, ancestorName):
            """ 
            Returns an ancestor uri based on the provided uri and the name of the ancestor.
            
            @param uri: The uri to derive the ancestor from.
            @type uri: string
            
            @param ancestorName: The ancestor folder of the uri.
            @type dst: string
            
            @return: The ancestor uri.
            @rtype: string
            """ 
            uri = os.path.dirname(uri.replace('\\', '/'))
            pathLayers = uri.rsplit("/")        
            ancestorUri = ""
            for pathLayer in pathLayers:
                if pathLayer == ancestorName:
                    break
                ancestorUri += pathLayer + "/"
            return ancestorUri




        @staticmethod    
        def adjustPathSlashes( str):
            """  Replaces '\\' path
            """
            return str.replace("\\", "/").replace("//", "/")




    class file(object):
        """
        """

        @staticmethod    
        def writeZip(src, dst = None, deleteFolders = False):
            """ 
            Writes a given path to a zip file based on the basename
            of the 'src' argument.
            
            from: http://stackoverflow.com/questions/296499/how-do-i-zip-the-contents-of-a-folder-using-python-version-2-5
            
            
            @param src: The source directory of the zip files.
            @type src: string
            
            @param dst: (Optional) The dst uri of the zip.  
            Defaults to '$parent_directory/$srcDirectoryName + .zip'
            @type dst: string

            
            @return: The dst file.
            @rtype: string
            """
            zipURI = src + ".zip"
            assert os.path.isdir(src)
            with closing(zipfile.ZipFile(zipURI, "w", zipfile.ZIP_DEFLATED)) as z:
                for root, dirs, files in os.walk(src):
                    for fileName in files: #NOTE: ignore empty directories
                        absfileName = os.path.join(root, fileName)
                        zfileName = absfileName[len(src)+len(os.sep):] # : relative path
                        z.write(absfileName, zfileName)

            dst = zipUri if dst == None else dst
            shutil.move(src, dst)
            return dst




        @staticmethod    
        def decompress(src, dst = None):
            """ 
            Emplots various methods to decompress a given file
            based on the file extension.  
            
            @param src: The source directory of the deompressible file.
            @type src: string
            
            @param dst: (Optional) The dst uri of the file to decompress.  
                Defaults to '$src_parent_directory/$src_name_without_extension'
            @type dst: string
            
            """
            if src.endswith(".zip"):
                import zipfile
                z = zipfile.ZipFile(src)      
                if not dst: dst = os.path.dirname(src)
                z.extractall(dst)
            elif src.endswith(".gz"):
                import gzip 
                a = gzip.GzipFile(src, 'rb')
                content = a.read()
                a.close()                                          
                f = open(src.split(".gz")[0], 'wb')
                f.write(content) 
                f.close()



    class string(object):
        """
        """

        @staticmethod    
        def getDateTimeStr():
            """ 
            Returns the Date and time as string in a more palattable / readable
            format.
            
            @return: The the date and time currently.
            @rtype: string
            """
            strList = str(datetime.datetime.today()).rsplit(" ")
            timeStr = strList[1]
            timeStr = timeStr.replace(":", " ")
            timeStr = timeStr.replace(".", " ")
            timeList = timeStr.rsplit(" ")
            shortTime = timeList[0]+ "-" + timeList[1]
            return strList[0] + "_" + shortTime




        @staticmethod    
        def replaceForbiddenChars( _str, replaceStr=None):
            """ As stated.
            """
            if not replaceStr: replaceStr = "_"
            _str = _str.replace(".", replaceStr)
            _str = _str.replace("/", replaceStr)
            _str = _str.replace("\\", replaceStr)
            _str = _str.replace(":", replaceStr)
            _str = _str.replace("*", replaceStr)
            _str = _str.replace("?", replaceStr)
            _str = _str.replace("\"", replaceStr)
            _str = _str.replace("<", replaceStr)
            _str = _str.replace(">", replaceStr)
            _str = _str.replace("|", replaceStr)
            return _str




    class debug(object):
        """
        """

        @staticmethod    
        def lf(*args):
            """
            For debugging purposes.  Returns the current line number and function
            when used throughout the module.
            """

            #---------------------------
            # Acquire the necessary parameters from
            # where the function is called.
            #---------------------------
            frame, filename, line_number, function_name, lines, index = inspect.getouterframes(inspect.currentframe())[1]
            returnStr = "\n"
            
            #
            # Construct a string based on the 
            # above parameters.
            #
            msg = ''
            for arg in args:
                msg += str(arg) + " "
            returnStr = "%s (%s) %s: %s"%(os.path.basename(filename), function_name, line_number, msg)
            
            print returnStr




    class convert(object):
        """
        """

        @staticmethod
        def bytesToMB( bytes):
            """ Converts bytes to MB.  Returns a float.
            """
            bytes = int(bytes)
            mb = str(bytes/(1024*1024.0)).split(".")[0] + "." + str(bytes/(1024*1024.0)).split(".")[1][:2]
            return float(mb)






