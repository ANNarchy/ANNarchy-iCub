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
import tomlkit

from libcpp.memory cimport make_shared

from cython.operator cimport dereference as deref

from .Joint_Reader cimport JointReader
from .iCub_Interface cimport ANNiCub_wrapper
from .Module_Base_Class cimport PyModuleBase


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


    # register joint reader module
    def _register(self, name: str, ANNiCub_wrapper iCub):
        """Register Joint Reader module at the main wrapper.
            -> For internal use only.

        Parameters
        ----------
        name : str
            name given to the Joint Reader
        iCub : ANNiCub_wrapper
            main interface wrapper

        Returns
        -------
        bool
            True/False on Success/Failure
        """
        if deref(self._cpp_joint_reader).getRegister():
            print("[Interface iCub] Joint Reader module is already registered!")
            return False
        else:
            if name in iCub._joint_reader:
                print("[Interface iCub] Joint Reader module name is already used!")
                return False
            else:
                if self._part in iCub._joint_reader_parts:
                    print("[Interface iCub] Joint Reader module part is already used!")
                    return False
                else:
                    iCub._joint_reader[name] = self
                    self._name = name
                    iCub._joint_reader_parts[self._part] = name
                    deref(self._cpp_joint_reader).setRegister(1)
                    print("Register", deref(self._cpp_joint_reader).getRegister())
                    return True

    # unregister joint reader  module
    def _unregister(self, ANNiCub_wrapper iCub):
        """Unregister Joint Reader module at the main wrapper.
            -> For internal use only.

        Parameters
        ----------
        module : PyJointReader
            Joint Reader instance

        Returns
        -------
        bool
            True/False on Success/Failure
        """
        if deref(self._cpp_joint_reader).getRegister():
            deref(self._cpp_joint_reader).setRegister(0)
            iCub._joint_reader.pop(self._name, None)
            iCub._joint_reader_parts.pop(self._part, None)
            self._name = ""
            return True
        else:
            print("[Interface iCub] Joint Reader module is not yet registered!")
            return False

    def _get_parameter(self):
        return deref(self._cpp_joint_reader).getParameter()

    '''
    # Access to joint reader member functions
    '''

    # Initialize the joint reader with given parameters
    def init(self, ANNiCub_wrapper iCub, str name, str part, double sigma, unsigned int n_pop, double degr_per_neuron=0.0, str ini_path="../data/"):
        """Initialize the joint reader with given parameters.

        Parameters
        ----------
        iCub : ANNiCub_wrapper
            main interface wrapper
        name : str
            name for the joint reader module
        part : str
            string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso}
        sigma : double
            sigma for the joints angles populations coding
        n_pop : unsigned int
            number of neurons per population, encoding each one joint angle only works if parameter "deg_per_neuron" is not set
        degr_per_neuron : double
            degree per neuron in the populations, encoding the joints angles
            if set: population size depends on joint working range. (Default value = 0.0)
        ini_path : str
            Path to the "interface_param.ini"-file. (Default value = "../data/")

        Returns
        -------
        bool
            return True, if successful
        """
        self._part = part
        # preregister module for some prechecks e.g. part already in use
        if self._register(name, iCub):
            retval = deref(self._cpp_joint_reader).Init(part.encode('UTF-8'), sigma, n_pop, degr_per_neuron, ini_path.encode('UTF-8'))
            if not retval:
                self._unregister(iCub)
            return retval
        else:
            return False

    # Initialize the joint reader with given parameters for use with gRPC
    def init_grpc(self, ANNiCub_wrapper iCub, str name, str part, double sigma, unsigned int n_pop, double degr_per_neuron=0.0, str ini_path="../data/",
                  str ip_address="0.0.0.0", unsigned int port=50005):
        """Initialize the joint reader with given parameters, including the gRPC based connection.

        Parameters
        ----------
        iCub : ANNiCub_wrapper
            main interface wrapper
        name : str
            name for the joint reader module
        part : str
            string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso}
        sigma : double
            sigma for the joints angles populations coding
        n_pop : unsigned int
            number of neurons per population, encoding each one joint angle only works if parameter "deg_per_neuron" is not set
        degr_per_neuron : double
            degree per neuron in the populations, encoding the joints angles
            if set: population size depends on joint working range. (Default value = 0.0)
        ini_path : str
            Path to the "interface_param.ini"-file. (Default value = "../data/")
        ip_address : str
            gRPC server ip address. (Default value = "0.0.0.0")
        port : unsigned int
            gRPC server port. (Default value = 50005)

        Returns
        -------
        bool
            return True, if successful
        """
        self._part = part
        # preregister module for some prechecks e.g. part already in use
        if self._register(name, iCub):
            retval = deref(self._cpp_joint_reader).InitGRPC(part.encode('UTF-8'), sigma, n_pop, degr_per_neuron, ini_path.encode('UTF-8'), ip_address.encode('UTF-8'), port)
            if not retval:
                self._unregister(iCub)
            return retval
        else:
            return False

    # Initialize the joint reader with given parameters
    def init_file(self, str filename):
        with open(filename, mode="rt", encoding="utf-8") as fp:
            config = tomlkit.load(fp)

    # close joint reader with cleanup
    def close(self, iCub):
        """Close joint reader with cleanup

        Parameters
        ----------
        iCub : ANNiCub_wrapper
            main interface wrapper

        Returns
        -------

        """
        self._unregister(iCub)
        self._part = ""
        deref(self._cpp_joint_reader).Close()

    # get the number of controlled joints
    def get_joint_count(self):
        """Return the number of controlled joints

        Parameters
        ----------

        Returns
        -------
        type
            int: return number of joints, being controlled by the reader
        """
        return deref(self._cpp_joint_reader).GetJointCount()

    # get the resolution in degree of the populations encoding the joint angles
    def get_joints_deg_res(self):
        """Return the resolution in degree of the populations encoding the joint angles

        Parameters
        ----------

        Returns
        -------
        type
            NDarray (vector[double]): return vector, containing the resolution for every joints population coding in degree
        """
        return np.array(deref(self._cpp_joint_reader).GetJointsDegRes())

    # get the size of the populations encoding the joint angles
    def get_neurons_per_joint(self):
        """Return the size of the populations encoding the joint angles

        Parameters
        ----------

        Returns
        -------
        type
            NDarray (vector[int]): return vector, containing the population size for every joint
        """
        return np.array(deref(self._cpp_joint_reader).GetNeuronsPerJoint())

    # read all joints and return joint angles directly as double values
    def read_double_all(self):
        """Read all joints and return joint angles directly as double values

        Parameters
        ----------

        Returns
        -------
        NDarray : vector[double]
            joint angles read from the robot; empty vector at error
        """
        return np.array(deref(self._cpp_joint_reader).ReadDoubleAll(), dtype=np.float64)

    # read multiple joints and return joint angles directly as double values
    def read_double_multiple(self, joints):
        """Read multiple joints and return joint angles directly as double value.

        Parameters
        ----------
        joints : list (vector[int]
            joint numbers of the robot part

        Returns
        -------
        NDarray : vector[double]
            joint angle read from the robot; empty vector at error
        """
        return np.array(deref(self._cpp_joint_reader).ReadDoubleMultiple(joints), dtype=np.float64)

    # read one joint and return joint angle directly as double value
    def read_double_one(self, int joint):
        """Read one joint and return joint angle directly as double value.

        Parameters
        ----------
        joint : int
            joint number of the robot part

        Returns
        -------
        double
            joint angle read from the robot; NAN at error
        """
        return deref(self._cpp_joint_reader).ReadDoubleOne(joint)

    # read all joints and return the joint angles encoded in vectors (population coding)
    def read_pop_all(self):
        """Read all joints and return the joint angles encoded in vectors (population coding)

        Parameters
        ----------

        Returns
        -------
        NDarray : vector[vector[double]]
            population vectors encoding every joint angle from associated robot part
        """
        return np.array(deref(self._cpp_joint_reader).ReadPopAll())

    # read multiple joints and return the joint angles encoded in a vector (population coding)
    def read_pop_multiple(self, joints):
        """Read multiple joints and return the joint angles encoded in vectors (population coding).

        Parameters
        ----------
        joints : list (vector[int]
            joint numbers of the robot part

        Returns
        -------
        NDarray : vector[vector[double]]
            population vectors encoding selected joint angles from associated robot part
        """
        return np.array(deref(self._cpp_joint_reader).ReadPopMultiple(joints))

    # read one joint and return the joint angle encoded in a vector (population coding)
    def read_pop_one(self, int joint):
        """Read one joint and return the joint angle encoded in a vector (population coding).

        Parameters
        ----------
        joint : int
            joint number of the robot part

        Returns
        -------
        NDarray : vector[double]
            population vector encoding the joint angle
        """
        return np.array(deref(self._cpp_joint_reader).ReadPopOne(joint))
