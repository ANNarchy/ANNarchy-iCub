"""
Created on Mon Apr 28 2020

@author: Torsten Fietzek

parameterfile for python iCub examples
"""

import os
import sys

import iCub_Python_Lib.iCub_transformation_matrices as iTransform


######################################################################
# General parameter
######################################################################

# True if the Gazebo simulator is used; False for the iCub-simulator
GAZEBO_SIM = True
# normally no need to change; only if multiple user work in the same YARP-network
CLIENT_PREFIX = "client"
# set to robot name: normally "iCubSim" for simulation and "icub" for real robot
ROBOT_PREFIX = "icubSim"

use_grpc = False
INTERFACE_INI_PATH = os.path.abspath("../../data/") + "/"

PATH_TO_INTERFACE_BUILD = ""    # "/path/to/Interface_ANNarchy_iCub/build" -> required only, if needed for import
if len(PATH_TO_INTERFACE_BUILD) > 0:
    sys.path.append(PATH_TO_INTERFACE_BUILD)


######################################################################
# Specific parameter only needed for some examples
######################################################################

# general gRPC connection parameter
ip_address = "0.0.0.0"

# joint position control
joints_head = [2, 3, 4]
popsize = 60
sigma = 3.5
steps_pos = 50

# Run kinematic in offline mode
offline = True
steps_kin = 40

# Set transformation matrices according to selected simulator
if GAZEBO_SIM:
    Transfermat_robot2world = iTransform.Transfermat_robot2gazebo
else:
    Transfermat_robot2world = iTransform.Transfermat_robot2iCubSim

if use_grpc:
    if not os.path.isdir("./annarchy"):
        os.mkdir("./annarchy")
