"""
Created on Thu Sep 22 17:53:33 CEST 2022

@author: Torsten Fietzek

example for joint inverse kinematics

"""

import sys

import example_parameter as params
import iCub_Python_Lib.iCub_transformation_matrices as iTransform

import ANN_iCub_Interface.Vocabs as iCub_const
from ANN_iCub_Interface.iCub import Kinematic_Writer, iCub_Interface


######################################################################
# Example implementation using the ANNarchy-iCub-Interface
def inverse_kin_ANN_iCub_Interface():

    ######################################################################
    # Add interface instances

    # Interface main wrapper, is needed once
    iCub = iCub_Interface.ANNiCub_wrapper()

    # Add kinematic reader instance
    kinwriter = Kinematic_Writer.PyKinematicWriter()

    # Init kinematic writer
    print('Init kinematic reader')
    if not kinwriter.init(iCub, "invkin", part=iCub_const.PART_KEY_RIGHT_ARM, version=2, ini_path=params.INTERFACE_INI_PATH):
        sys.exit("Initialization failed")

    print("DOF:", kinwriter.get_DOF())

    ######################################################################
    # Perform inverse kinematic

    target_position = [-0.3, 0.0, 0.05]
    blocked_joints = [0, 1, 2, 7, 8, 9]  # [0, 1, 2] -> all joints of the torso part; [7, 8, 9] -> joints [4, 5, 6] of arm part
    kinwriter.solve_InvKin(target_position, blocked_joints)

    ######################################################################
    # Close interface instances
    iCub.clear()


if __name__ == '__main__':
    inverse_kin_ANN_iCub_Interface()
