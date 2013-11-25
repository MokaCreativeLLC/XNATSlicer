from __main__ import vtk, ctk, qt, slicer



comment = """
XnatError is a class that manages an errors resultant from
the XnatIo.  Rather than passing strings alone, XnatError
handles other relevant data to a specific Xnat IO error, such as the
Xnat host and the user who logs into the host.

TODO: Consider futher variables to track as part of an error.  Consider
further errors to keep track of.
"""



class XnatError(object):
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
