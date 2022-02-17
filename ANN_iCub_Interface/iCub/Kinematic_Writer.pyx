# distutils: language = c++
# cython: language_level = 3

"""
   Copyright (C) 2022 Torsten Fietzek; Helge Ülo Dinkelbach

   Kinematic_Writer.pyx is part of the iCub ANNarchy interface

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

from .Kinematic_Writer cimport KinematicWriter
from .iCub_Interface cimport ANNiCub_wrapper

import numpy as np

cdef class PyKinematicWriter:

    # init method
    def __cinit__(self):
        print("Initialize iCub Interface: Kinematic Writer.")
        self.cpp_kin_writer = make_shared[KinematicWriter]()

    # close method
    def __dealloc__(self):
        print("Close iCub Interface: Kinematic Writer.")
        self.cpp_kin_writer.reset()

    ### Access to Kinematic writer member functions
    # init Kinematic writer with given parameters for image resolution, field of view and eye selection
    def init(self, ANNiCub_wrapper iCub, str name, str part, float version, str ini_path ="../data/"):
        """
            Calls bool KinematicWriter::Init(std::string part, float version, std::string ini_path)

            function:
                Initialize the Kinematic Writer with given parameters

            params:
                ANNiCub_wrapper iCub    -- main interface wrapper
                str name                -- name for the kinematic writer
                string part             -- string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso}
                float version           -- version of the robot hardware
                string ini_path         -- path to the interface ini-files

            return:
                bool            -- return True, if successful
        """

        self.part = part
        # preregister module for some prechecks e.g. name already in use
        if iCub.register_kin_writer(name, self):
            # call the interface
            retval = deref(self.cpp_kin_writer).Init(part.encode('UTF-8'), version, ini_path.encode('UTF-8'))
            if not retval:
                iCub.unregister_kin_writer(self)
            return retval
        else:
            return False

    # init Kinematic writer with given parameters for image resolution, field of view and eye selection
    def init_grpc(self, ANNiCub_wrapper iCub, str name, str part, float version, str ini_path ="../data/", str ip_address="0.0.0.0", unsigned int port=50000):
        """
            Calls bool KinematicWriter::InitGRPC(std::string part, float version, std::string ini_path, std::string ip_address, unsigned int port)

            function:
                Initialize the Kinematic Writer with given parameters

            params:
                ANNiCub_wrapper iCub    -- main interface wrapper
                string name             -- individual module name
                string part             -- string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso}
                float version           -- version of the robot hardware
                string ini_path         -- path to the interface ini-files
                string ip_address       -- gRPC server ip address
                unsigned int port       -- gRPC server port

            return:
                bool                    -- return True, if successful
        """

        self.part = part
        # preregister module for some prechecks e.g. eye already in use
        if iCub.register_kin_writer(name, self):
            # call the interface
            retval = deref(self.cpp_kin_writer).InitGRPC(part.encode('UTF-8'), version, ini_path.encode('UTF-8'), ip_address.encode('UTF-8'), port)
            if not retval:
                iCub.unregister_kin_writer(self)
            return retval
        else:
            return False

    # deinitialize module
    def close(self, ANNiCub_wrapper iCub):
        """
            Calls void KinematicWriter::Close()

            function:
                close the module module.

            params:
                ANNiCub_wrapper iCub    -- main interface wrapper
        """

        iCub.unregister_kin_writer(self)

        # call the interface
        deref(self.cpp_kin_writer).Close()


    # solve inverse kinematics for given position
    def solve_InvKin(self, position, blocked_links):
        """
            Calls std::vector<double> KinematicWriter::solveInvKin(std::vector<double> position, std::vector<int> blocked_links)

            function: Compute the joint configuration for a given 3D End-Effector position (Inverse Kinematics)

            return: active joint positions (in radians)

        """
        # call the interface
        return np.array(deref(self.cpp_kin_writer).solveInvKin(position, blocked_links))

    # return DOF of kinematic chain
    def get_DOF(self):
        """
            Calls void KinematicWriter::GetDOF()

            function: Retur the DOF of the kinematic chain

            return: DOF of the kinematic chain

        """
        # call the interface
        return deref(self.cpp_kin_writer).GetDOF()

    ### end access to kinematic writer member functions