import os
import sys
import subprocess
from pathlib import Path

# iCub interaction Classes
from . import iCub

# Classes for Synchronization
from . import Sync

# Python "constants":
#   - joint numbers
#   - iCub part strings
#   - skin sections
from . import Vocabs

# Create python file with instance creation and initilization
from .Special_Features import create_robot_interface_file

# iCub specific ANNarchy Populations
from . import ANNarchy_iCub_Populations

# Version
from ._version import __version__
from ._use_grpc import __use_grpc__

__all__ = ['iCub',
           'Sync',
           'Vocabs',
           'ANNarchy_iCub_Populations'
           ]

# Package root path -> used for grpc includes
__root_path__ = str(Path(__file__).resolve().parents[1]) + "/"

# Set variables for ANNarchy-iCub-Population compilation
if __use_grpc__:
    _grpc_cpp_plugin = subprocess.check_output(["which", "grpc_cpp_plugin"]).strip().decode(sys.stdout.encoding)
    _grpc_path = str(Path(_grpc_cpp_plugin).resolve().parents[1]) + "/"
    __grpc_include_path__ = _grpc_path + "/include"
    __grpc_lib_path__ = _grpc_path + "/lib"

    __ann_compile_args__ = "-march=native -O2 " + "-I" + __root_path__ + " -Wl,-rpath," + __root_path__ + "/ANN_iCub_Interface/grpc/ -I" + __grpc_include_path__
    __ann_extra_libs__ = "-L" + __grpc_lib_path__ + " -lprotobuf -lgrpc++ -lgrpc++_reflection -L" + __root_path__ + "ANN_iCub_Interface/grpc/ -liCub_ANN_grpc"

print('ANNarchy to iCub interface ' + __version__ + ' on ' + sys.platform + ' (' + os.name + ').')
