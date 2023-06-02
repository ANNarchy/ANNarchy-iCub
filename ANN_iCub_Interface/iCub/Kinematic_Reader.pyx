# distutils: language = c++
# cython: language_level = 3
# cython: binding=True

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

from libcpp.string cimport string
from libcpp.vector cimport vector
from libcpp.memory cimport shared_ptr, make_shared
from cython.operator cimport dereference as deref

from .Kinematic_Reader cimport KinematicReader
from .iCub_Interface cimport ANNiCub_wrapper

import numpy as np

cdef class PyKinematicReader:

    # constructor method
    def __cinit__(self):
        print("Initialize iCub Interface: Kinematic Reader.")
        self.cpp_kin_reader = make_shared[KinematicReader]()

    # destructor method
    def __dealloc__(self):
        print("Close iCub Interface: Kinematic Reader.")
        self.cpp_kin_reader.reset()

    ### Access to Kinematic reader member functions
    # Init Kinematic reader with given parameters for image resolution, field of view and eye selection
    def init(self, ANNiCub_wrapper iCub, str name, str part, float version, str ini_path ="../data/", offline_mode=False):
        """
            Calls bool KinematicReader::Init(std::string part, float version, std::string ini_path)

            function:
                Initialize the Kinematic Reader with given parameters

            params:
                ANNiCub_wrapper iCub    -- main interface wrapper
                str name                -- name for the kinematic reader
                string part             -- string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso}
                float version           -- version of the robot hardware
                string ini_path         -- path to the interface ini-files
                bool offline_mode       -- Flag, if iCub network is offline

            return:
                bool            -- return True, if successful
        """

        self.part = part
        # preregister module for some prechecks e.g. name already in use
        if iCub.register_kin_reader(name, self):
            # call the interface
            retval = deref(self.cpp_kin_reader).Init(part.encode('UTF-8'), version, ini_path.encode('UTF-8'), offline_mode.__int__())
            if not retval:
                iCub.unregister_kin_reader(self)
            return retval
        else:
            return False

    # Init Kinematic reader with given parameters for image resolution, field of view and eye selection
    def init_grpc(self, ANNiCub_wrapper iCub, str name, str part, float version, str ini_path ="../data/", str ip_address="0.0.0.0", unsigned int port=50000, offline_mode=False):
        """
            Calls bool KinematicReader::InitGRPC(std::string part, float version, std::string ini_path, std::string ip_address, unsigned int port)

            function:
                Initialize the Kinematic Reader with given parameters

            params:
                ANNiCub_wrapper iCub    -- main interface wrapper
                string name             -- individual module name
                string part             -- string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso}
                float version           -- version of the robot hardware
                string ini_path         -- path to the interface ini-files
                string ip_address       -- gRPC server ip address
                unsigned int port       -- gRPC server port
                bool offline_mode       -- Flag, if iCub network is offline

            return:
                bool                    -- return True, if successful
        """

        self.part = part
        # preregister module for some prechecks e.g. eye already in use
        if iCub.register_kin_reader(name, self):
            # call the interface
            retval = deref(self.cpp_kin_reader).InitGRPC(part.encode('UTF-8'), version, ini_path.encode('UTF-8'), ip_address.encode('UTF-8'), port, offline_mode.__int__())
            if not retval:
                iCub.unregister_kin_reader(self)
            return retval
        else:
            return False

    # Close module
    def close(self, ANNiCub_wrapper iCub):
        """
            Calls void KinematicReader::Close()

            function:
                close the module module.

            params:
                ANNiCub_wrapper iCub    -- main interface wrapper
        """

        iCub.unregister_kin_reader(self)

        # call the interface
        deref(self.cpp_kin_reader).Close()

    # Get End-Effector cartesian position
    def get_handposition(self):
        """
            Calls void KinematicReader::GetHandPosition()

            function:

            return:

        """
        # call the interface
        return np.array(deref(self.cpp_kin_reader).GetHandPosition())

    # Get cartesian position of given joint
    def get_jointposition(self, unsigned int joint):
        """
            Calls void KinematicReader::GetCartesianPosition()

            function:

            return:

        """
        # call the interface
        return np.array(deref(self.cpp_kin_reader).GetCartesianPosition(joint))

    # Return number of DOF
    def get_DOF(self):
        """
            Calls void KinematicReader::GetDOF()

            function:

            return:

        """
        # call the interface
        return deref(self.cpp_kin_reader).GetDOF()

    # Get current joint angles
    def get_jointangles(self):
        """
            Calls std::vector<double> KinematicReader::GetJointAngles()

            function: Get current joint angles of active kinematic chain -> radians

            return:

        """
        # call the interface
        return np.array(deref(self.cpp_kin_reader).GetJointAngles())

    # Set joint angles for forward kinematic in offline mode
    def set_jointangles(self, joint_angles):
        """
            Calls void KinematicReader::SetJointAngles(std::vector<double> joint_angles)

            function: Set joint angles for forward kinematic in offline mode

            return: void

        """
        # call the interface
        deref(self.cpp_kin_reader).SetJointAngles(joint_angles)

    # Get blocked links
    def get_blocked_links(self):
        """
            Calls std::vector<int>  KinematicReader::GetBlockedLinks()

            function: get blocked links

            return:

        """
        # call the interface
        return np.array(deref(self.cpp_kin_reader).GetBlockedLinks())

    # Block links
    def block_links(self, blocked_joints):
        """
            Calls void KinematicReader::BlockLinks(std::vector<int> blocked_joints)

            function: Set

            return:

        """
        # call the interface
        deref(self.cpp_kin_reader).BlockLinks(blocked_joints)

    # Get joints being part of active kinematic chain
    def get_DOF_links(self):
        """
            Calls std::vector<int>  KinematicReader::GetDOFLinks()

            function: Get

            return:

        """
        # call the interface
        return np.array(deref(self.cpp_kin_reader).GetDOFLinks())

    # Release links of kinematic chain
    def release_links(self, release_joints):
        """
            Calls void KinematicReader::ReleaseLinks(std::vector<int> release_joints)

            function: Set

            return:

        """
        # call the interface
        deref(self.cpp_kin_reader).ReleaseLinks(release_joints)

    ### end access to kinematic reader member functions