from GLOB import *
import os
from __main__ import vtk, ctk, qt, slicer




comment = """
XnatGlobals contains static properites relevant o 
interacting with XNAT.

TODO : 
"""



    
GLOB_LIB_URI =  os.path.dirname(os.path.dirname(os.path.abspath( __file__ )))
GLOB_ROOT_URI =  os.path.dirname(GLOB_LIB_URI)
GLOB_CACHE_URI =  os.path.join(GLOB_ROOT_URI, 'Cache')
GLOB_RESOURCES_URI =  os.path.join(GLOB_ROOT_URI, 'Resources')

GLOB_LOCAL_URIS = {
        "home" : GLOB_ROOT_URI,
        "settings": os.path.join(GLOB_ROOT_URI, "Settings"),
        "projects" : os.path.join(GLOB_CACHE_URI, "projects"),
        "downloads" : os.path.join(GLOB_CACHE_URI, "downloads"),
        "uploads" : os.path.join(GLOB_CACHE_URI, "uploads"), 
        "icons" : os.path.join(GLOB_RESOURCES_URI, "Icons"),                       
        }
    
    
    
GLOB_DICOM_EXTENSIONS =  [".dcm", ".ima", ".dicom"]
GLOB_ANALYZE_EXTENSIONS =  [".hdr", ".img"]
GLOB_MISC_LOADABLE_EXTENSIONS =   [".nii", 
                 ".nrrd", 
                 ".img", 
                 ".nhdr", 
                 ".dc", 
                 ".raw.gz", 
                 ".gz", 
                 ".vtk",
                 ".stl", 
                 ".acsv"]
    

GLOB_DECOMPRESSIBLE_EXTENSIONS =   [".gz", ".zip", ".tar"]
GLOB_MRML_EXTENSIONS =  [".mrml"]    
GLOB_ALL_LOADABLE_EXTENSIONS =  GLOB_DICOM_EXTENSIONS + GLOB_ANALYZE_EXTENSIONS + GLOB_MISC_LOADABLE_EXTENSIONS  

GLOB_BUTTON_SIZE_MED =  qt.QSize(45, 45)
GLOB_BUTTON_SIZE_SMALL =  qt.QSize(28, 28)


GLOB_FONT_NAME =  "Arial"
GLOB_FONT_SIZE =  10

GLOB_LABEL_FONT =  qt.QFont(GLOB_FONT_NAME, GLOB_FONT_SIZE, 10, False)        
GLOB_LABEL_FONT_LARGE =  qt.QFont(GLOB_FONT_NAME, GLOB_FONT_SIZE + 2, 10, False)
GLOB_LABEL_FONT_BOLD =  qt.QFont(GLOB_FONT_NAME, GLOB_FONT_SIZE, 100, False)
GLOB_LABEL_FONT_ITALIC =  qt.QFont(GLOB_FONT_NAME, GLOB_FONT_SIZE, 10, True)
GLOB_LABEL_FONT_ITALIC_LARGE =  qt.QFont(GLOB_FONT_NAME, GLOB_FONT_SIZE + 2, 10, True)

    
GLOB_XNAT_LEVELS =  ['projects', 'subjects', 'experiments', 'scans', 'slicer', 'files']
GLOB_CUSTOM_METADATA_SETTINGS_PREFIX =  'customMetadataTags_'
GLOB_XNAT_XSI_TYPES =  {'MR Session': 'xnat:mrSessionData',
                'PET Session': 'xnat:petSessionData',
                'CT Session' : 'xnat:ctSessionData'
                }

GLOB_DEFAULT_PATH_DICT = {"projects":None, "subjects":None, "experiments":None, "scans":None, "resources":None, "files":None}



GLOB_SLICER_FOLDER_NAME = "Slicer"

    
GLOB_REQUIRED_SLICER_FOLDERS = [GLOB_SLICER_FOLDER_NAME]

GLOB_DEFAULT_XNAT_SAVE_LEVEL = "experiments"
    

GLOB_DEFAULT_XNAT_METADATA =  {
            
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

    
GLOB_DATE_TAGS =  [ 'last_accessed_497', 'insert_date']
