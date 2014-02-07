# python
from collections import OrderedDict

# application
from __main__ import qt

# module
from XnatSlicerGlobals import *
from XnatSlicerUtils import *
from Settings import *
from MetadataEditorSet import *
from CheckBoxSetting import *


        
class Settings_Cache(CheckBoxSetting, Settings):
    """
    Manages settings related to cached images.
    """

    CHECKBOXES = OrderedDict([
        ('images', {
            'tag': 'useImageCache',
            'desc': 'Use cached images (DICOM, Analyze).',
            'checked': True,
            'event': 'USECACHEDIMAGES'
        })
    ])


    def setup(self):
        """
        Setup function inherited from parent class.
            -Adds a checkbox and its relevant callbacks to the widget.
        """   
        self.createCheckBoxes()

