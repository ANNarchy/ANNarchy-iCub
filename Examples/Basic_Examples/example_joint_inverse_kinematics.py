"""
Created on Thu Sep 22 17:53:33 CEST 2022

@author: Torsten Fietzek

example for joint inverse kinematics

"""

import sys
import numpy as np

import example_parameter as params

import ANN_iCub_Interface.Vocabs as iCub_Const
from ANN_iCub_Interface.iCub import Kinematic_Writer, iCub_Interface


######################################################################
# Example implementation using the ANNarchy-iCub-Interface
def inverse_kin_ANN_iCub_Interface():

    ######################################################################
    # Add interface instances

    # Interface main wrapper, is needed once
    iCub = iCub_Interface.ANNiCub_wrapper()

    # Add kinematic writer instance
    kinwriter = Kinematic_Writer.PyKinematicWriter()

    # Init kinematic writer
    print('Init kinematic writer')
    if not kinwriter.init(iCub, "invkin", part=iCub_Const.PART_KEY_RIGHT_ARM, version=2, ini_path=params.INTERFACE_INI_PATH, offline_mode=params.offline):
        sys.exit("Initialization failed")

    target_position = [-0.3, 0.0, 0.05]
    blocked_joints = [0, 1, 2, 7, 8, 9]  # [0, 1, 2] -> all joints of the torso part; [7, 8, 9] -> joints [4, 5, 6] of arm part
    joint_angles = np.deg2rad(np.array([-20., 5., 30., 30.]))

    print("Current joint angles:", np.rad2deg(kinwriter.get_jointangles()))
    print("DOF:", kinwriter.get_DOF())

    ######################################################################
    # Perform inverse kinematic: Either offline with manually set starting angles or online with the current angles retrieved from the robot
    if params.offline:
        kinwriter.block_links(blocked_joints)
        kinwriter.set_jointangles(joint_angles)
        joint_angles = kinwriter.solve_InvKin(target_position)
    else:
        joint_angles = kinwriter.solve_InvKin(target_position, blocked_joints)
    print("Estimated joint angles:", np.rad2deg(joint_angles))

    ######################################################################
    # Close interface instances
    iCub.clear()


if __name__ == '__main__':
    inverse_kin_ANN_iCub_Interface()
