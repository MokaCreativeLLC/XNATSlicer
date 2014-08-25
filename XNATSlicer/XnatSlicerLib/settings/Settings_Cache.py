__author__ = "Sunil Kumar (kumar.sunil.p@gmail.com)"
__copyright__ = "Copyright 2014, Washington University in St. Louis"
__credits__ = ["Sunil Kumar", "Steve Pieper", "Dan Marcus"]
__license__ = "XNAT Software License Agreement " + \
              "(see: http://xnat.org/about/license.php)"
__version__ = "2.1.1"
__maintainer__ = "Rick Herrick"
__email__ = "herrickr@mir.wustl.edu"
__status__ = "Production"


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

