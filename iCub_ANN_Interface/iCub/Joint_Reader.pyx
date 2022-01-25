# distutils: language = c++
# cython: language_level = 3

"""
   Copyright (C) 2019-2021 Torsten Fietzek; Helge Ülo Dinkelbach

   Joint_Reader.pyx is part of the iCub ANNarchy interface

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   The iCub ANNarchy interface is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this headers. If not, see [http://www.gnu.org/licenses/].
 """

from libcpp.string cimport string
from libcpp.vector cimport vector
from libcpp.memory cimport shared_ptr, make_shared
from cython.operator cimport dereference as deref

from .Joint_Reader cimport JointReader
from .iCub_Interface cimport iCubANN_wrapper

import numpy as np

cdef class PyJointReader:

    # init method
    def __cinit__(self):
        print("Initialize iCub Interface: Joint Reader.")
        self.cpp_joint_reader = make_shared[JointReader]()

    # close method
    def __dealloc__(self):
        print("Close iCub Interface: Joint Reader.")
        self.cpp_joint_reader.reset()


    ### Access to joint reader member functions
    # Initialize the joint reader with given parameters
    def init(self, iCubANN_wrapper iCub, str name, str part, double sigma, unsigned int n_pop, double degr_per_neuron=0.0, str ini_path="../data/"):
        """
            Calls bool JointReader::Init(string part, double sigma, int pop_n, double deg_per_neuron, std::string ini_path)

            function:
                Initialize the joint reader with given parameters

            params:
                iCubANN_wrapper iCub    -- main interface wrapper
                str name                -- name for the joint reader module
                string part             -- string representing the robot part, has to match iCub part naming
                                            {left_(arm/leg), right_(arm/leg), head, torso}
                sigma                   -- sigma for the joints angles populations coding
                unsigned int pop_size   -- number of neurons per population, encoding each one joint angle 
                                            only works if parameter "deg_per_neuron" is not set
                double deg_per_neuron   -- degree per neuron in the populations, encoding the joints angles
                                            if set: population size depends on joint working range
                ini_path                -- Path to the "interface_param.ini"-file

            return:
                bool                    -- return True, if successful
        """

        self.part = part
        # preregister module for some prechecks e.g. part already in use
        if iCub.register_jreader(name, self):
            # call the interface
            retval = deref(self.cpp_joint_reader).Init(part.encode('UTF-8'), sigma, n_pop, degr_per_neuron, ini_path.encode('UTF-8'))
            if not retval:
                iCub.unregister_jreader(self)
            return retval
        else:
            return False

    # Initialize the joint reader with given parameters for use with gRPC
    def init_grpc(self, iCubANN_wrapper iCub, str name, str part, double sigma, unsigned int n_pop, double degr_per_neuron=0.0, str ini_path="../data/", str ip_address="0.0.0.0", unsigned int port=50005):
        """
            Calls bool InitGRPC(string part, double sigma, int pop_n, double deg_per_neuron, std::string ini_path, std::string ip_address, unsigned int port)

            function:
                Initialize the joint reader with given parameters

            params:
                iCubANN_wrapper iCub    -- main interface wrapper
                str name                -- name for the joint reader module
                string part             -- string representing the robot part, has to match iCub part naming
                                            {left_(arm/leg), right_(arm/leg), head, torso}
                sigma                   -- sigma for the joints angles populations coding
                unsigned int pop_size   -- number of neurons per population, encoding each one joint angle
                                            only works if parameter "deg_per_neuron" is not set
                double deg_per_neuron   -- degree per neuron in the populations, encoding the joints angles
                                            if set: population size depends on joint working range
                ini_path                -- Path to the "interface_param.ini"-file
                string ip_address       -- gRPC server ip address
                unsigned int port       -- gRPC server port

            return:
                bool                    -- return True, if successful
        """

        self.part = part
        # preregister module for some prechecks e.g. part already in use
        if iCub.register_jreader(name, self):
            # call the interface
            retval = deref(self.cpp_joint_reader).InitGRPC(part.encode('UTF-8'), sigma, n_pop, degr_per_neuron, ini_path.encode('UTF-8'), ip_address.encode('UTF-8'), port)
            if not retval:
                iCub.unregister_jreader(self)
            return retval
        else:
            return False

    # close joint reader with cleanup
    def close(self, iCubANN_wrapper iCub):
        """
            Calls JointReader::Close()

            function:
                Close joint reader with cleanup

            params:
                iCubANN_wrapper iCub    -- main interface wrapper
       """

        iCub.unregister_jreader(self)

        # call the interface
        deref(self.cpp_joint_reader).Close()
        self.part = ""

    # get the number of controlled joints
    def get_joint_count(self):
        """
            Calls vector[double] JointReader::GetJointCount()

            function:
                Return the number of controlled joints

            return:
                int             -- return number of joints, being controlled by the reader
        """
        # call the interface
        return deref(self.cpp_joint_reader).GetJointCount()

    # get the resolution in degree of the populations encoding the joint angles
    def get_joints_deg_res(self):
        """
            Calls vector[double] JointReader::GetJointsDegRes()

            function:
                Return the resolution in degree of the populations encoding the joint angles

            return:
                vector[double]  -- return vector, containing the resolution for every joints population coding in degree
        """

        # call the interface
        return np.array(deref(self.cpp_joint_reader).GetJointsDegRes())

    # get the size of the populations encoding the joint angles
    def get_neurons_per_joint(self):
        """
            Calls vector[int] JointReader:: GetNeuronsPerJoint()

            function:
                Return the size of the populations encoding the joint angles

            return:
                vector[int]     -- return vector, containing the population size for every joint
        """

        # call the interface
        return np.array(deref(self.cpp_joint_reader).GetNeuronsPerJoint())

    # read all joints and return joint angles directly as double values
    def read_double_all(self):
        """
            Calls double JointReader::ReadDoubleAll()

            function:
                Read all joints and return joint angles directly as double values

            return:
                vector[double]  -- joint angles read from the robot; empty vector at error
        """

        # call the interface
        return np.array(deref(self.cpp_joint_reader).ReadDoubleAll(), dtype=np.float64)

    # read multiple joints and return joint angles directly as double values
    def read_double_multiple(self, joints):
        """
            Calls double JointReader::ReadDoubleMultiple(vector[int] joints)

            function:
                Read multiple joints and return joint angles directly as double value

            params:
                vector[int] joints       -- joint numbers of the robot part

            return:
                vector[double]          -- joint angle read from the robot; empty vector at error
        """

        # call the interface
        return np.array(deref(self.cpp_joint_reader).ReadDoubleMultiple(joints))

    # read one joint and return joint angle directly as double value
    def read_double_one(self, int joint):
        """
            Calls double JointReader::ReadDoubleOne(int joint)

            function:
                Read one joint and return joint angle directly as double value

            params:
                int joint       -- joint number of the robot part

            return:
                double          -- joint angle read from the robot; NAN at error
        """

        # call the interface
        return deref(self.cpp_joint_reader).ReadDoubleOne(joint)

    # read all joints and return the joint angles encoded in vectors (population coding)
    def read_pop_all(self):
        """
            Calls vector[vector[double]] JointReader::ReadPopAll()

            function:
                Read all joints and return the joint angles encoded in vectors (population coding)

            return:
                vector[vector[double]]  -- population vectors encoding every joint angle from associated robot part

        """

        # call the interface
        return np.array(deref(self.cpp_joint_reader).ReadPopAll())

    # read multiple joints and return the joint angles encoded in a vector (population coding)
    def read_pop_multiple(self, joints):
        """
            Calls vector[vector[double]] JointReader::ReadPopMultiple(vector[int])

            function:
                Read multiple joints and return the joint angles encoded in vectors (population coding)

            params:
                vector[int] joints       -- joint numbers of the robot part

            return:
                vector[vector[double]]  -- population vectors encoding selected joint angles from associated robot part

        """

        # call the interface
        return np.array(deref(self.cpp_joint_reader).ReadPopMultiple(joints))

    # read one joint and return the joint angle encoded in a vector (population coding)
    def read_pop_one(self, int joint):
        """
            Calls vector[double] JointReader::ReadPopOne(int joint)

            function:
                Read one joint and return the joint angle encoded in a vector (population coding)

            params:
                int joint       -- joint number of the robot part

            return:
                vector[double]  -- population vector encoding the joint angle
        """

        # call the interface
        return np.array(deref(self.cpp_joint_reader).ReadPopOne(joint))

    ### end access to joint reader member functions
