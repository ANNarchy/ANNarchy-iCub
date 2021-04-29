"""
Created on Thu Jul 9 20:26:04 CEST 2020

@author: Torsten Fietzek

config file for the package compilation process
"""

import os
import sys

# Add compiler flags to the g++ commands
verbose = False
pedantic = False

# Use gRPC for direct iCub to ANNarchy communication
use_grpc = False

# Select typ precision for images returned by the visual reader
double_precision = True

# Set the OpenCV include directory -> only set this if the setup fails due to missing OpenCV path
cv_include = "default"

# Set the prefix of the YARP installation -> only set this if the setup fails due to missing YARP path
yarp_prefix = "default"

# Build process
rebuild_grpc = False # set to true if the grpc code changed and need a rebuild, e.g. after an update of the repository

## Helper functions to determine the OpenCV and YARP include paths
def set_yarp_prefix():
    # Yarp install direction
    yarp_prefix = None

    if "ROBOTOLOGY_SUPERBUILD_INSTALL_PREFIX" in os.environ:
        yarp_prefix = os.environ["ROBOTOLOGY_SUPERBUILD_INSTALL_PREFIX"]
    elif "YARP_DATA_DIRS" in os.environ:
        yarp_data = os.environ['YARP_DATA_DIRS'].split(':')[0].split('/')
        if yarp_data[-1] == "iCub" or yarp_data[-1] == "yarp":
            yarp_prefix = "/".join(yarp_data[:-3])
        else:
            yarp_prefix = "/".join(yarp_data[:-2])
    elif os.path.isdir("/usr/local/include/yarp"):
        yarp_prefix = "/usr/local"
    elif os.path.isdir("/usr/include/yarp"):
        yarp_prefix = "/usr"
    else:
        if yarp_prefix == None:
            print("Did not find YARP include path! Please set yarp_prefix manually!")
            print("Please type the YARP prefix in the form /path/to/include/and/lib:")
            yarp_prefix = input()
            if not os.path.isdir(yarp_prefix + "/include/yarp"):
                sys.exit("Did not find YARP in given path! Please set yarp_prefix manually in make_config.py or retry!")
    return yarp_prefix

def set_opencv_prefix():
    # OpenCV direction
    cv_include = None

    if os.path.isdir("/usr/include/opencv2"):
        cv_include = "/usr/include"
    elif os.path.isdir("/usr/include/opencv4"):
        cv_include = "/usr/include/opencv4"
    elif os.path.isdir("/usr/local/include/opencv2"):
        cv_include = "/usr/local/include"
    elif os.path.isdir("/usr/local/include/opencv4"):
        cv_include = "/usr/local/include/opencv4"
    else:
        if cv_include == None:
            print("Did not find OpenCV include path! Please set cv_include manually!")
            print("Please type the OpenCV prefix e.g. /usr/include for /usr/include/opencv2:")
            cv_include = input()
            if not os.path.isdir(cv_include + "/opencv2"):
                sys.exit("Did not find OpenCV in given path! Please set cv_include manually in make_config.py or retry!")
    return cv_include
