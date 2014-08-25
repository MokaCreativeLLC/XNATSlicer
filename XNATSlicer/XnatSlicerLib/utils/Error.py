__author__ = "Sunil Kumar (kumar.sunil.p@gmail.com)"
__copyright__ = "Copyright 2014, Washington University in St. Louis"
__credits__ = ["Sunil Kumar", "Steve Pieper", "Dan Marcus"]
__license__ = "XNAT Software License Agreement " + \
              "(see: http://xnat.org/about/license.php)"
__version__ = "2.1.1"
__maintainer__ = "Rick Herrick"
__email__ = "herrickr@mir.wustl.edu"
__status__ = "Production"


from __main__ import vtk, ctk, qt, slicer



comment = """
Error is a class that manages an errors resultant from
the XnatIo.  Rather than passing strings alone, Error
handles other relevant data to a specific Xnat IO error, such as the
Xnat host and the user who logs into the host.

TODO: Consider futher variables to track as part of an error.  Consider
further errors to keep track of.
"""



class Error(object):
    """ Described above.
    """
    
    def __init__(self, host, username, errorString):
        """ Init function.
        """

        self.host = host
        self.username = username


        
        #----------------------
        # CASE 1: Invalid username/password.
        #----------------------
        if 'Login attempt fail' in errorString:
            #self.errorMsg  = "Login to '%s' failed! Invalid username/password."%(self.host)
            self.errorMsg  = "Invalid username/password."
