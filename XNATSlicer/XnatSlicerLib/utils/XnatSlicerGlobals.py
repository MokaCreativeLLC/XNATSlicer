import os
from __main__ import qt

class XnatSlicerGlobals(object):
    """
    XnatSlicerGlobals contains static properites relevant to 
    the XnatSlicer module.
    """
    
    LIB_URI =  os.path.dirname(os.path.dirname(os.path.abspath( __file__ )))
    ROOT_URI =  os.path.dirname(LIB_URI)
    CACHE_URI =  os.path.join(ROOT_URI, 'Cache')
    RESOURCES_URI =  os.path.join(ROOT_URI, 'Resources')

    LOCAL_URIS = {
        "home" : ROOT_URI,
        "settings": os.path.join(ROOT_URI, "Settings"),
        "projects" : os.path.join(CACHE_URI, "projects"),
        "downloads" : os.path.join(CACHE_URI, "downloads"),
        "uploads" : os.path.join(CACHE_URI, "uploads"), 
        "icons" : os.path.join(RESOURCES_URI, "Icons"),                       
    }
    
    
    
    DICOM_EXTENSIONS =  [".dcm", ".ima", ".dicom"]
    ANALYZE_EXTENSIONS =  [".hdr", ".img"]
    MISC_LOADABLE_EXTENSIONS =   [".nii", 
                 ".nrrd", 
                 ".img", 
                 ".nhdr", 
                 ".dc", 
                 ".raw.gz", 
                 ".gz", 
                 ".vtk",
                 ".stl", 
                 ".acsv"]
    

    DECOMPRESSIBLE_EXTENSIONS =   [".gz", ".zip", ".tar"]
    MRML_EXTENSIONS =  [".mrml"]    
    ALL_LOADABLE_EXTENSIONS =  DICOM_EXTENSIONS + ANALYZE_EXTENSIONS + MISC_LOADABLE_EXTENSIONS  

    BUTTON_SIZE_MED =  qt.QSize(45, 45)
    BUTTON_SIZE_SMALL =  qt.QSize(28, 28)


    FONT_NAME =  "Arial"
    FONT_SIZE =  10

    LABEL_FONT =  qt.QFont(FONT_NAME, FONT_SIZE, 10, False)        
    LABEL_FONT_LARGE =  qt.QFont(FONT_NAME, FONT_SIZE + 2, 10, False)
    LABEL_FONT_BOLD =  qt.QFont(FONT_NAME, FONT_SIZE, 100, False)
    LABEL_FONT_ITALIC =  qt.QFont(FONT_NAME, FONT_SIZE, 10, True)
    LABEL_FONT_ITALIC_LARGE =  qt.QFont(FONT_NAME, FONT_SIZE + 2, 10, True)

    
    
    CUSTOM_METADATA_SETTINGS_PREFIX =  'customMetadataTags_'


    SLICER_FOLDER_NAME = "Slicer"
    REQUIRED_SLICER_FOLDERS = [SLICER_FOLDER_NAME]
    DEFAULT_XNAT_SAVE_LEVEL = "experiments"
    

    DEFAULT_SLICER_EXTENSION = ".mrb"
    SLICER_PACKAGE_EXTENSIONS = [".zip", ".mrb"]

    DEFAULT_SCENE_NAME =  "SlicerScene_"
