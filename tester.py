__author__ = "Sunil Kumar (kumar.sunil.p@gmail.com)"
__copyright__ = "Copyright 2014, Washington University in St. Louis"
__credits__ = ["Sunil Kumar", "Steve Pieper", "Dan Marcus"]
__license__ = "XNAT Software License Agreement " +               "(see: http://xnat.org/about/license.php_)"
__version__ = "2.1.1"
__maintainer__ = "Rick Herrick"
__email__ = "herrickr@mir.wustl.edu"
__status__ = "Production"


class tester(object):
    """
    """
    TEST = ['TEST']
    def __init__(self):
        print "iniot"
        
    def test(self):
        self.TEST.append('test2')
        print self.TEST
