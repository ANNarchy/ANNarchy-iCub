# distutils: language = c++
# cython: language_level = 3

"""
   Copyright (C) 2019-2021 Torsten Fietzek; Helge Ülo Dinkelbach

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
from libc.stdlib cimport malloc, free
from cython.operator cimport dereference as deref

from .Kinematic_Reader cimport KinReader
from .iCub_Interface cimport iCubANN_wrapper

import numpy as np

cdef class PyKinematicReader:

    # init method
    def __cinit__(self):
        print("Initialize iCub Interface: Kinematic Reader.")
        self.cpp_kin_reader = make_shared[KinReader]()

    # close method
    def __dealloc__(self):
        print("Close iCub Interface: Kinematic Reader.")
        self.cpp_kin_reader.reset()

    ### Access to Kinematic reader member functions
    # init Kinematic reader with given parameters for image resolution, field of view and eye selection
    def init(self, iCubANN_wrapper iCub, str name, str part, float version, str ini_path = "../data/"):
        """
            Calls bool KinReader::Init(std::string part, float version, std::string ini_path)

            function:
                Initialize the Kinematic Reader with given parameters

            params:
                string part     -- string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso}
                float version   --
                string ini_path -- 

            return:
                bool            -- return True, if successful
        """

        self.part = part
        # preregister module for some prechecks e.g. name already in use
        if iCub.register_kin_reader(name, self):
            # call the interface
            retval = deref(self.cpp_kin_reader).Init(part.encode('UTF-8'), version, ini_path.encode('UTF-8'))
            if not retval:
                iCub.unregister_kin_reader(self)
            return retval
        else:
            return False

    # init Kinematic reader with given parameters for image resolution, field of view and eye selection
    def init_grpc(self, iCubANN_wrapper iCub, str name, str part, float version, str ini_path = "../data/", str ip_address="0.0.0.0", unsigned int port=50000):
        """
            Calls bool KinReader::InitGRPC(std::string part, float version, std::string ini_path, std::string ip_address, unsigned int port)

            function:
                Initialize the Kinematic Reader with given parameters

            params:
                iCubANN_wrapper iCub    -- main interface wrapper
                string name             -- individual module name
                string part             -- string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso}
                float version           --
                string ini_path         -- 
                string ip_address       -- gRPC server ip address
                unsigned int port       -- gRPC server port

            return:
                bool                    -- return True, if successful
        """

        self.part = part
        # preregister module for some prechecks e.g. eye already in use
        if iCub.register_kin_reader(name, self):
            # call the interface
            retval = deref(self.cpp_kin_reader).InitGRPC(part.encode('UTF-8'), version, ini_path.encode('UTF-8'), ip_address.encode('UTF-8'), port)
            if not retval:
                iCub.unregister_kin_reader(self)
            return retval
        else:
            return False

    # deinitialize module
    def close(self, iCubANN_wrapper iCub):
        """
            Calls void KinematicReader::Close()

            function:
                close the module module.

            params:
                iCubANN_wrapper iCub    -- main interface wrapper
        """

        iCub.unregister_kin_reader(self)

        # call the interface
        deref(self.cpp_kin_reader).Close()

    #
    def get_handposition(self):
        """
            Calls void KinematicReader::GetHandPosition()

            function:
                
            return:

        """
        # call the interface
        return np.array(deref(self.cpp_kin_reader).GetHandPosition())

    #
    def get_jointposition(self, unsigned int joint):
        """
            Calls void KinematicReader::GetHandPosition()

            function:
                
            return:

        """
        # call the interface
        return np.array(deref(self.cpp_kin_reader).GetCartesianPosition(joint))

    #
    def get_DOF(self):
        """
            Calls void KinematicReader::GetDOF()

            function:
                
            return:

        """
        # call the interface
        return deref(self.cpp_kin_reader).GetDOF()

    ### end access to kinematic reader member functions