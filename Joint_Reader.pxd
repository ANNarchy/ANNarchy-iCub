# distutils: language = c++
# cython: language_level = 3

"""
   Copyright (C) 2020 Torsten Follak Helge Ülo Dinkelbach

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
from libcpp cimport bool as bool_t
from libcpp.map cimport map as cmap

import numpy as np


cdef extern from "Joint_Reader.hpp":

    cdef cppclass JointReader:
        JointReader() except +
        
        # Initialize the joint reader with given parameters
        bool_t Init(string, double, int, double)

        # Close joint reader with cleanup
        void Close()

        # Return number of controlled joints
        int GetJointCount()

        # Return the resolution in degree of the populations encoding the joint angles.
        vector[double] GetJointsDegRes()

        # Return the size of the populations encoding the joint angles
        vector[int] GetNeuronsPerJoint()

        # Read all joints and return joint angles directly in degree as double values
        vector[double] ReadDoubleAll()

        # Read one joint and return joint angle directly in degree as double value
        double ReadDoubleOne(int joint)

        # Read all joints and return the joint angles encoded in populations.
        vector[vector[double]] ReadPopAll()

        # Read one joint and return the joint angle encoded in a population.
        vector[double] ReadPopOne(int joint)


    # ### Access to joint reader member functions
    # # Initialize the joint reader with given parameters
    # def jointR_init(self, name, part, sigma, n_pop, degr_per_neuron=0.0):
    #     """
    #         Calls bool iCubANN::JointRInit(string name, string part, double sigma, int pop_n, double deg_per_neuron)

    #         function:
    #             Initialize the joint reader with given parameters

    #         params:
    #             string name        -- name of the selected joint reader
    #             string part        -- string representing the robot part, has to match iCub part naming
    #                                         {left_(arm/leg), right_(arm/leg), head, torso}
    #             sigma                   -- sigma for the joints angles populations coding
    #             int pop_size            -- number of neurons per population, encoding each one joint angle
    #                                         only works if parameter "deg_per_neuron" is not set
    #             double deg_per_neuron   -- degree per neuron in the populations, encoding the joints angles
    #                                         if set: population size depends on joint working range

    #         return:
    #             bool                    -- return True, if successful
    #     """
    #     # we need to transform py-string to c++ compatible string
    #     cdef string c_name = name.encode('UTF-8')
    #     cdef string key = part.encode('UTF-8')

    #     return my_interface.JointRInit(c_name, key, sigma, n_pop, degr_per_neuron)

    # # close joint reader with cleanup
    # def jointR_close(self, name):
    #     """
    #         Calls iCubANN::JointRClose(string name)

    #         function:
    #             Close joint reader with cleanup

    #         params:
    #             string name    -- name of the selected joint reader
    #    """
    #     # we need to transform py-string to c++ compatible string
    #     cdef string s = name.encode('UTF-8')

    #     # call the interface
    #     my_interface.JointRClose(s)

    # # get the number of controlled joints
    # def jointR_get_joint_count(self, name):
    #     """
    #         Calls vector[double] iCubANN::JointRGetJointCount(string name)

    #         function:
    #             Return the number of controlled joints

    #         params:
    #             string name        -- name of the selected joint reader

    #         return:
    #             int                     -- return number of joints, being controlled by the reader
    #     """
    #     # we need to transform py-string to c++ compatible string
    #     cdef string s = name.encode('UTF-8')

    #     # call the interface
    #     return my_interface.JointRGetJointCount(s)

    # # get the resolution in degree of the populations encoding the joint angles
    # def jointR_get_joints_deg_res(self, name):
    #     """
    #         Calls vector[double] iCubANN::JointRGetJointsDegRes(string name)

    #         function:
    #             Return the resolution in degree of the populations encoding the joint angles

    #         params:
    #             string name        -- name of the selected joint reader

    #         return:
    #             vector[double]     -- return vector, containing the resolution for every joints population codimg in degree
    #     """
    #     # we need to transform py-string to c++ compatible string
    #     cdef string s = name.encode('UTF-8')

    #     # call the interface
    #     return np.array(my_interface.JointRGetJointsDegRes(s))

    # # get the size of the populations encoding the joint angles
    # def jointR_get_neurons_per_joint(self, name):
    #     """
    #         Calls vector[int] iCubANN:: JointRGetNeuronsPerJoint(string name)

    #         function:
    #             Return the size of the populations encoding the joint angles

    #         params:
    #             string name        -- name of the selected joint reader

    #         return:
    #             vector[int]        -- return vector, containing the population size for every joint
    #     """
    #     # we need to transform py-string to c++ compatible string
    #     cdef string s = name.encode('UTF-8')

    #     # call the interface
    #     return np.array(my_interface.JointRGetNeuronsPerJoint(s))

    # # read all joints and return joint angles directly as double values
    # def jointR_read_double_all(self, name):
    #     """
    #         Calls double iCubANN::JointRReadDoubleAll(string name)

    #         function:
    #             Read all joints and return joint angles directly as double values

    #         params:
    #             string name    -- name of the selected joint reader

    #         return:
    #             double              -- joint angles read from the robot empty vector at error
    #     """
    #     # we need to transform py-string to c++ compatible string
    #     cdef string s = name.encode('UTF-8')

    #     # call the interface
    #     return my_interface.JointRReadDoubleAll(s)

    # # read one joint and return joint angle directly as double value
    # def jointR_read_double_one(self, name, joint):
    #     """
    #         Calls double iCubANN::JointRReadDoubleOne(string name, int joint)

    #         function:
    #             Read one joint and return joint angle directly as double value

    #         params:
    #             string name    -- name of the selected joint reader
    #             int joint           -- joint number of the robot part

    #         return:
    #             double              -- joint angle read from the robot NAN at error
    #     """
    #     # we need to transform py-string to c++ compatible string
    #     cdef string s = name.encode('UTF-8')

    #     # call the interface
    #     return my_interface.JointRReadDoubleOne(s, joint)

    # # read all joints and return the joint angles encoded in vectors (population coding)
    # def jointR_read_pop_all(self, name):
    #     """
    #         Calls vector[vector[double]] iCubANN::JointRReadPopAll(string name)

    #         function:
    #             Read all joints and return the joint angles encoded in vectors (population coding)

    #         params:
    #             string name        -- name of the selected joint reader

    #         return:
    #             vector[vector[double]]    -- population vectors encoding every joint angle from associated robot part

    #     """
    #     # we need to transform py-string to c++ compatible string
    #     cdef string s = name.encode('UTF-8')

    #     # call the interface
    #     return my_interface.JointRReadPopAll(s)


    # # read one joint and return the joint angle encoded in a vector (population coding)
    # def jointR_read_pop_one(self, name, joint):
    #     """
    #         Calls vector[double] iCubANN::JointRReadPopOne(string name, int joint)

    #         function:
    #             Read one joint and return the joint angle encoded in a vector (population coding)

    #         params:
    #             string name        -- name of the selected joint reader
    #             int joint               -- joint number of the robot part

    #         return:
    #             vector[double]     -- population vector encoding the joint angle
    #     """
    #     # we need to transform py-string to c++ compatible string
    #     cdef string s = name.encode('UTF-8')

    #     # call the interface
    #     return my_interface.JointRReadPopOne(s, joint)

    # ### end access to joint reader member functions
