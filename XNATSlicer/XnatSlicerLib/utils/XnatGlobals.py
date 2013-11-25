import os
from __main__ import vtk, ctk, qt, slicer




comment = """
XnatGlobals contains static properites relevant o 
interacting with XNAT.

TODO : 
"""



class XnatGlobals(object):
    
    def __init__(self, parent=None):   
        pass

    
    
    @property
    def LIB_URI(self):
        return os.path.dirname(os.path.dirname(os.path.abspath( __file__ )))



    
    @property
    def ROOT_URI(self):
        return os.path.dirname(self.LIB_URI)

    

    
    @property
    def CACHE_URI(self):
        return os.path.join(self.ROOT_URI, 'Cache')



    
    @property
    def RESOURCES_URI(self):
        return os.path.join(self.ROOT_URI, 'Resources')


    
    
    @property
    def LOCAL_URIS(self):
        return {
            "home" : self.ROOT_URI,
            "settings": os.path.join(self.ROOT_URI, "Settings"),
            "projects" : os.path.join(self.CACHE_URI, "projects"),
            "downloads" : os.path.join(self.CACHE_URI, "downloads"),
            "uploads" : os.path.join(self.CACHE_URI, "uploads"), 
            "icons" : os.path.join(self.RESOURCES_URI, "Icons"),                       
        }



    
    @property
    def DICOM_EXTENSIONS(self):
        return [".dcm", ".ima", ".dicom"]



    @property
    def ANALYZE_EXTENSIONS(self):
        return [".hdr", ".img"]

    

    @property
    def ALL_LOADABLE_EXTENSIONS(self):
        return self.DICOM_EXTENSIONS + [".nii", 
                                       ".nrrd", 
                                       ".img", 
                                       ".ima",
                                       ".IMA",
                                       ".nhdr", 
                                       ".dc", 
                                       ".raw.gz", 
                                       ".gz", 
                                       ".vtk"]


    @property
    def DECOMPRESSIBLE_EXTENSIONS(self):
        return  [".gz", ".zip", ".tar"]


    
    @property
    def MRML_EXTENSIONS(self):
        return [".mrml"]




    @property
    def BUTTON_SIZE_MED(self):
        return qt.QSize(45, 45)



    
    @property
    def BUTTON_SIZE_SMALL(self):
        return qt.QSize(28, 28)


    @property
    def LABEL_FONT(self):
        return qt.QFont(self.FONT_NAME, self.FONT_SIZE, 10, False)


    
    @property
    def LABEL_FONT_LARGE(self):
        return qt.QFont(self.FONT_NAME, self.FONT_SIZE + 2, 10, False)


    
    @property
    def LABEL_FONT_BOLD(self):
        return qt.QFont(self.FONT_NAME, self.FONT_SIZE, 100, False)


    
    
    @property
    def LABEL_FONT_ITALIC(self):
        return qt.QFont(self.FONT_NAME, self.FONT_SIZE, 10, True)


    
    @property
    def LABEL_FONT_ITALIC_LARGE(self):
        return qt.QFont(self.FONT_NAME, self.FONT_SIZE + 2, 10, True)

    

    @property
    def FONT_NAME(self):
        return "Arial"

    
    
    @property
    def FONT_SIZE(self):
        return 10


    

    @property
    def XNAT_LEVELS(self):
        return ['projects', 'subjects', 'experiments', 'scans', 'slicer', 'files']

    


    @property
    def CUSTOM_METADATA_SETTINGS_PREFIX(self):
        return 'customMetadataTags_'


    

    def makeCustomMetadataTag(self, xnatLevel):
        """
        """
        return self.CUSTOM_METADATA_SETTINGS_PREFIX + xnatLevel.lower()
    



    @property
    def XNAT_XSI_TYPES(self):
        return {'MR Session': 'xnat:mrSessionData',
                'PET Session': 'xnat:petSessionData',
                'CT Session' : 'xnat:ctSessionData'
                }

        
    @property
    def DEFAULT_XNAT_METADATA(self):
        return {
            
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
                'URI'
                ],
                                    
                                    
                                    
            'slicer' : [
                'Size',
                'file_format',
                'file_content',
                'collection',
                'file_tags',
                'cat_ID',
                'URI'
                ]
                
                }

    @property
    def DATE_TAGS(self):
        return [ 'last_accessed_497', 'insert_date']
