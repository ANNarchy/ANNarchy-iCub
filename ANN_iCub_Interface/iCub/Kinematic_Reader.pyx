# distutils: language = c++
# cython: language_level = 3
# cython: binding=True
# cython: embedsignature=True

"""
   Copyright (C) 2019-2022 Torsten Fietzek; Helge Ülo Dinkelbach

   Kinematic_Reader.pyx is part of the iCub ANNarchy interface

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   The iCub ANNarchy interface is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this headers. If not, see <http://www.gnu.org/licenses/>.
 """

from libcpp.memory cimport make_shared
from cython.operator cimport dereference as deref

from .Kinematic_Reader cimport KinematicReader
from .iCub_Interface cimport ANNiCub_wrapper

import numpy as np

cdef class PyKinematicReader:
    """Wrapper class for Kinematic Reader module."""

    # constructor method
    def __cinit__(self):
        print("Initialize iCub Interface: Kinematic Reader.")
        self._cpp_kin_reader = make_shared[KinematicReader]()

    # destructor method
    def __dealloc__(self):
        print("Close iCub Interface: Kinematic Reader.")
        self._cpp_kin_reader.reset()

    '''
    # Access to kinematic reader member functions
    '''

    # Init Kinematic reader with given parameters
    def init(self, ANNiCub_wrapper iCub, str name, str part, float version, str ini_path ="../data/", offline_mode=False):
        """Initialize the Kinematic Reader with given parameters

        Args:
            iCub (ANNiCub_wrapper): main interface wrapper
            name (str): individual name for the kinematic reader
            part (str): string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso}
            version (float): version of the robot hardware
            ini_path (str, optional): path to the interface ini-file. Defaults to "../data/".
            offline_mode (bool, optional): flag, if iCub network is offline. Defaults to False.

        Returns:
            bool: return True/False, indicating success/failure
        """
        self._part = part
        # preregister module for some prechecks e.g. name already in use
        if iCub.register_kin_reader(name, self):
            # call the interface
            retval = deref(self._cpp_kin_reader).Init(part.encode('UTF-8'), version, ini_path.encode('UTF-8'), offline_mode.__int__())
            if not retval:
                iCub.unregister_kin_reader(self)
            return retval
        else:
            return False

    # Init Kinematic reader with given parameters, including the gRPC based connection
    def init_grpc(self, ANNiCub_wrapper iCub, str name, str part, float version, str ini_path ="../data/", str ip_address="0.0.0.0",
                  unsigned int port=50020, offline_mode=False):
        """Initialize the Kinematic Reader with given parameters, including the gRPC based connection.

        Args:
            iCub (ANNiCub_wrapper): main interface wrapper
            name (str): individual name for the kinematic reader
            part (str): string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso}
            version (float): version of the robot hardware
            ini_path (str, optional): path to the interface ini-file. Defaults to "../data/".
            ip_address (str, optional): gRPC server ip address. Defaults to "0.0.0.0".
            port (unsigned int, optional): gRPC server port. Defaults to 50000.
            offline_mode (bool, optional): flag, if iCub network is offline. Defaults to False.

        Returns:
            bool: return True/False, indicating success/failure
        """
        self._part = part
        # preregister module for some prechecks e.g. eye already in use
        if iCub.register_kin_reader(name, self):
            # call the interface
            retval = deref(self._cpp_kin_reader).InitGRPC(part.encode('UTF-8'), version, ini_path.encode('UTF-8'), ip_address.encode('UTF-8'), port, offline_mode.__int__())
            if not retval:
                iCub.unregister_kin_reader(self)
            return retval
        else:
            return False

    # Close module
    def close(self, ANNiCub_wrapper iCub):
        """Close the module

        Args:
            iCub (ANNiCub_wrapper): main interface wrapper
        """
        iCub.unregister_kin_reader(self)
        self._part = ""
        deref(self._cpp_kin_reader).Close()

    # Get End-Effector cartesian position
    def get_handposition(self):
        """Get End-Effector cartesian position.

        Returns:
            NDarray: Cartesian position of the end-effector in robot reference frame
        """
        return np.array(deref(self._cpp_kin_reader).GetHandPosition())

    # Get cartesian position of given joint
    def get_jointposition(self, unsigned int joint):
        """Get cartesian position for the given joint.

        Args:
            joint (unsigned int): joint number of the robot part

        Returns:
            NDarray: Cartesian position of the joint in robot reference frame
        """
        return np.array(deref(self._cpp_kin_reader).GetCartesianPosition(joint))

    # Return DOF of the kinematic chain
    def get_DOF(self):
        """Return the DOF of the kinematic chain

        Returns:
            int: degree of freedom (DOF) of the kinematic chain
        """
        return deref(self._cpp_kin_reader).GetDOF()

    # Get current joint angles
    def get_jointangles(self):
        """Get current joint angles of active kinematic chain -> radians.

        Returns:
            NDarray: joint angles in radians
        """
        return np.array(deref(self._cpp_kin_reader).GetJointAngles())

    # Set joint angles for forward kinematic in offline mode
    def set_jointangles(self, joint_angles):
        """Set joint angles for forward kinematic in offline mode.

        Args:
            joint_angles (list/NDarray): joint angles
        """
        deref(self._cpp_kin_reader).SetJointAngles(joint_angles)

    # Get blocked links
    def get_blocked_links(self):
        """Get blocked links.

        Returns:
            NDarray: vector containing the blocked links
        """
        return np.array(deref(self._cpp_kin_reader).GetBlockedLinks())

    # Block links
    def block_links(self, blocked_joints):
        """Block specific set of joints in the kinematic chain.

        Args:
            blocked_joints (list): joints that should be blocked
        """
        deref(self._cpp_kin_reader).BlockLinks(blocked_joints)

    # Get joints being part of active kinematic chain
    def get_DOF_links(self):
        """Get joints being part of active kinematic chain.

        Returns:
            NDarray: vector with the active joints
        """
        return np.array(deref(self._cpp_kin_reader).GetDOFLinks())

    # Release links of kinematic chain
    def release_links(self, release_joints):
        """Release links of kinematic chain

        Args:
            release_joints (list): joints that should be released
        """
        deref(self._cpp_kin_reader).ReleaseLinks(release_joints)
