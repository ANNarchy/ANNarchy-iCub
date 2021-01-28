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
from libcpp cimport bool as bool_t
from libcpp.memory cimport shared_ptr

cdef extern from "Joint_Reader.hpp":

    cdef cppclass JointReader:
        JointReader() except +

        # Initialize the joint reader with given parameters
        bool_t Init(string, double, int, double, string)

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


cdef class PyJointReader:
    cdef shared_ptr[JointReader] cpp_joint_reader

