import os
import sys

# iCub interaction Classes
from . import iCub

# Classes for Synchronization
from . import Sync

# python "constants": 
#   - joint numbers
#   - iCub part strings 
from . import Vocabs

# iCub specific ANNarchy Populations
from . import ANNarchy_iCub_Populations

# Version
__version__ = '0.1'

print( 'ANNarchy to iCub interface ' + __version__ + ' on ' + sys.platform + ' (' + os.name + ').' )
