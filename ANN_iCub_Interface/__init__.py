import os
import sys
from pathlib import Path

# iCub interaction Classes
from . import iCub

# Classes for Synchronization
from . import Sync

# python "constants": 
#   - joint numbers
#   - iCub part strings 
from . import Vocabs

# create python file with instance creation and initilization
from .Special_Features import create_robot_interface_file

# iCub specific ANNarchy Populations
from . import ANNarchy_iCub_Populations

# Version
from .version import __version__

__all__ = [
    # Modules
    'iCub',
    'Sync',
    'Vocabs',
    'ANNarchy_iCub_Populations'
]

# package root path -> used for grpc includes 
__root_path__ = str(Path(__file__).resolve().parents[1]) + "/"

print( 'ANNarchy to iCub interface ' + __version__ + ' on ' + sys.platform + ' (' + os.name + ').' )
