# distutils: language = c++
# cython: language_level = 3
# cython: binding=True
# cython: embedsignature=True

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

from libcpp.memory cimport make_shared
from cython.operator cimport dereference as deref

from .Kinematic_Writer cimport KinematicWriter
from .iCub_Interface cimport ANNiCub_wrapper

import numpy as np

cdef class PyKinematicWriter:

    # init method
    def __cinit__(self):
        print("Initialize iCub Interface: Kinematic Writer.")
        self._cpp_kin_writer = make_shared[KinematicWriter]()

    # close method
    def __dealloc__(self):
        print("Close iCub Interface: Kinematic Writer.")
        self._cpp_kin_writer.reset()

    '''
    # Access to Kinematic writer member functions 
    '''

    # init kinematic writer with given parameters
    def init(self, ANNiCub_wrapper iCub, str name, str part, float version, str ini_path ="../data/"):
        """Initialize the Kinematic Writer with given parameters.

        Args:
            iCub (ANNiCub_wrapper): main interface wrapper
            name (str): individual name for the kinematic reader
            part (str): string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso}
            version (float): version of the robot hardware
            ini_path (str, optional): path to the interface ini-file. Defaults to "../data/".

        Returns:
            bool: return True/False, indicating success/failure
        """
        self._part = part
        # preregister module for some prechecks e.g. name already in use
        if iCub.register_kin_writer(name, self):
            retval = deref(self._cpp_kin_writer).Init(part.encode('UTF-8'), version, ini_path.encode('UTF-8'))
            if not retval:
                iCub.unregister_kin_writer(self)
            return retval
        else:
            return False

    # init kinematic writer with given parameters, including the gRPC based connection
    def init_grpc(self, ANNiCub_wrapper iCub, str name, str part, float version, str ini_path ="../data/", str ip_address="0.0.0.0", unsigned int port=50025):
        """Initialize the Kinematic Writer with given parameters, including the gRPC based connection.

        Args:
            iCub (ANNiCub_wrapper): main interface wrapper
            name (str): individual name for the kinematic reader
            part (str): string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso}
            version (float): version of the robot hardware
            ini_path (str, optional): path to the interface ini-file. Defaults to "../data/".
            ip_address (str, optional): gRPC server ip address. Defaults to "0.0.0.0".
            port (unsigned int, optional): gRPC server port. Defaults to 50000.

        Returns:
            bool: return True/False, indicating success/failure
        """
        self._part = part
        # preregister module for some prechecks e.g. eye already in use
        if iCub.register_kin_writer(name, self):
            retval = deref(self._cpp_kin_writer).InitGRPC(part.encode('UTF-8'), version, ini_path.encode('UTF-8'), ip_address.encode('UTF-8'), port)
            if not retval:
                iCub.unregister_kin_writer(self)
            return retval
        else:
            return False

    # close module
    def close(self, ANNiCub_wrapper iCub):
        """Close the module.

        Args:
            iCub (ANNiCub_wrapper): main interface wrapper
        """
        iCub.unregister_kin_writer(self)
        self._part = ""
        deref(self._cpp_kin_writer).Close()

    # solve inverse kinematics for given position
    def solve_InvKin(self, position, blocked_links):
        """Compute the joint configuration for a given 3D End-Effector position (Inverse Kinematics).

        Args:
            position (list): target cartesian position for the end-effector/hand
            blocked_links (list): links of the kinematic chain, which should be blocked for inverse kinematic

        Returns:
            NDarray: active joint positions (in radians)
        """
        return np.array(deref(self._cpp_kin_writer).solveInvKin(position, blocked_links))

    # return DOF of kinematic chain
    def get_DOF(self):
        """Return the DOF of the kinematic chain.

        Returns:
            int: DOF of the kinematic chain
        """
        return deref(self._cpp_kin_writer).GetDOF()
