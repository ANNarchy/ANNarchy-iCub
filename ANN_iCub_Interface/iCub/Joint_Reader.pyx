# distutils: language = c++
# cython: language_level = 3
# cython: binding=True
# cython: embedsignature=True

"""
   Copyright (C) 2019-2023 Torsten Fietzek; Helge Ülo Dinkelbach

   Joint_Reader.pyx is part of the ANNarchy iCub interface

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   The ANNarchy iCub interface is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this headers. If not, see [http://www.gnu.org/licenses/].
 """

import numpy as np

from libcpp.memory cimport make_shared

from cython.operator cimport dereference as deref

from .Joint_Reader cimport JointReader
from .iCub_Interface cimport ANNiCub_wrapper


cdef class PyJointReader:
    """Wrapper class for Joint Reader module."""

    # init method
    def __cinit__(self):
        print("Initialize iCub Interface: Joint Reader.")
        self._cpp_joint_reader = make_shared[JointReader]()

    # close method
    def __dealloc__(self):
        print("Close iCub Interface: Joint Reader.")
        self._cpp_joint_reader.reset()

    '''
    # Access to joint reader member functions
    '''

    # Initialize the joint reader with given parameters
    def init(self, ANNiCub_wrapper iCub, str name, str part, double sigma, unsigned int n_pop, double degr_per_neuron=0.0, str ini_path="../data/"):
        """Initialize the joint reader with given parameters.

        Args:
            iCub (ANNiCub_wrapper): main interface wrapper
            name (str): name for the joint reader module
            part (str): string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso}
            sigma (double): sigma for the joints angles populations coding
            n_pop (unsigned int): number of neurons per population, encoding each one joint angle only works if parameter "deg_per_neuron" is not set
            degr_per_neuron (double, optional): degree per neuron in the populations, encoding the joints angles
                                                if set: population size depends on joint working range. Defaults to 0.0.
            ini_path (str, optional): Path to the "interface_param.ini"-file. Defaults to "../data/".

        Returns:
            bool: return True, if successful
        """
        self._part = part
        # preregister module for some prechecks e.g. part already in use
        if iCub.register_jreader(name, self):
            retval = deref(self._cpp_joint_reader).Init(part.encode('UTF-8'), sigma, n_pop, degr_per_neuron, ini_path.encode('UTF-8'))
            if not retval:
                iCub.unregister_jreader(self)
            return retval
        else:
            return False

    # Initialize the joint reader with given parameters for use with gRPC
    def init_grpc(self, ANNiCub_wrapper iCub, str name, str part, double sigma, unsigned int n_pop, double degr_per_neuron=0.0, str ini_path="../data/",
                  str ip_address="0.0.0.0", unsigned int port=50005):
        """Initialize the joint reader with given parameters, including the gRPC based connection.

        Args:
            iCub (ANNiCub_wrapper): main interface wrapper
            name (str): name for the joint reader module
            part (str): string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso}
            sigma (double): sigma for the joints angles populations coding
            n_pop (unsigned int): number of neurons per population, encoding each one joint angle only works if parameter "deg_per_neuron" is not set
            degr_per_neuron (double, optional): degree per neuron in the populations, encoding the joints angles
                                                if set: population size depends on joint working range. Defaults to 0.0.
            ini_path (str, optional): Path to the "interface_param.ini"-file. Defaults to "../data/".
            ip_address (str, optional): gRPC server ip address. Defaults to "0.0.0.0".
            port (unsigned int, optional): gRPC server port. Defaults to 50005.

        Returns:
            bool: return True, if successful
        """
        self._part = part
        # preregister module for some prechecks e.g. part already in use
        if iCub.register_jreader(name, self):
            retval = deref(self._cpp_joint_reader).InitGRPC(part.encode('UTF-8'), sigma, n_pop, degr_per_neuron, ini_path.encode('UTF-8'), ip_address.encode('UTF-8'), port)
            if not retval:
                iCub.unregister_jreader(self)
            return retval
        else:
            return False

    # close joint reader with cleanup
    def close(self, ANNiCub_wrapper iCub):
        """Close joint reader with cleanup

        Args:
            iCub (ANNiCub_wrapper): main interface wrapper
        """
        iCub.unregister_jreader(self)
        self._part = ""
        deref(self._cpp_joint_reader).Close()

    # get the number of controlled joints
    def get_joint_count(self):
        """Return the number of controlled joints

        Returns:
            int: return number of joints, being controlled by the reader
        """
        return deref(self._cpp_joint_reader).GetJointCount()

    # get the resolution in degree of the populations encoding the joint angles
    def get_joints_deg_res(self):
        """Return the resolution in degree of the populations encoding the joint angles

        Returns:
            NDarray (vector[double]): return vector, containing the resolution for every joints population coding in degree
        """
        return np.array(deref(self._cpp_joint_reader).GetJointsDegRes())

    # get the size of the populations encoding the joint angles
    def get_neurons_per_joint(self):
        """Return the size of the populations encoding the joint angles

        Returns:
            NDarray (vector[int]): return vector, containing the population size for every joint
        """
        return np.array(deref(self._cpp_joint_reader).GetNeuronsPerJoint())

    # read all joints and return joint angles directly as double values
    def read_double_all(self):
        """Read all joints and return joint angles directly as double values

        Returns:
            NDarray (vector[double]): joint angles read from the robot; empty vector at error
        """
        return np.array(deref(self._cpp_joint_reader).ReadDoubleAll(), dtype=np.float64)

    # read multiple joints and return joint angles directly as double values
    def read_double_multiple(self, joints):
        """Read multiple joints and return joint angles directly as double value.

        Args:
            joints (list (vector[int])): joint numbers of the robot part

        Returns:
            NDarray (vector[double]): joint angle read from the robot; empty vector at error
        """
        return np.array(deref(self._cpp_joint_reader).ReadDoubleMultiple(joints), dtype=np.float64)

    # read one joint and return joint angle directly as double value
    def read_double_one(self, int joint):
        """Read one joint and return joint angle directly as double value.

        Args:
            joint (int): joint number of the robot part

        Returns:
            double: joint angle read from the robot; NAN at error
        """
        return deref(self._cpp_joint_reader).ReadDoubleOne(joint)

    # read all joints and return the joint angles encoded in vectors (population coding)
    def read_pop_all(self):
        """Read all joints and return the joint angles encoded in vectors (population coding)

        Returns:
            NDarray (vector[vector[double]]): population vectors encoding every joint angle from associated robot part
        """
        return np.array(deref(self._cpp_joint_reader).ReadPopAll())

    # read multiple joints and return the joint angles encoded in a vector (population coding)
    def read_pop_multiple(self, joints):
        """Read multiple joints and return the joint angles encoded in vectors (population coding).

        Args:
            joints (list (vector[int])): joint numbers of the robot part

        Returns:
            NDarray (vector[vector[double]]): population vectors encoding selected joint angles from associated robot part
        """
        return np.array(deref(self._cpp_joint_reader).ReadPopMultiple(joints))

    # read one joint and return the joint angle encoded in a vector (population coding)
    def read_pop_one(self, int joint):
        """Read one joint and return the joint angle encoded in a vector (population coding).

        Args:
            joint (int): joint number of the robot part

        Returns:
            NDarray (vector[double]): population vector encoding the joint angle
        """
        return np.array(deref(self._cpp_joint_reader).ReadPopOne(joint))
