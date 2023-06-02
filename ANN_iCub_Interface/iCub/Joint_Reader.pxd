# distutils: language = c++
# cython: language_level = 3
# cython: binding=True
# cython: embedsignature=True

"""
   Copyright (C) 2019-2022 Torsten Fietzek; Helge Ülo Dinkelbach

   Joint_Reader.pxd is part of the ANNarchy iCub interface

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

from libcpp.string cimport string
from libcpp.vector cimport vector
from libcpp cimport bool as bool_t
from libcpp.memory cimport shared_ptr
from libcpp.map cimport map as cmap

cdef extern from "Joint_Reader.hpp":

    cdef cppclass JointReader:
        JointReader() except +

        # Initialize the joint reader with given parameters
        bool_t Init(string, double, unsigned int, double, string)

        # Initialize the joint reader with given parameters and grpc communication.
        bool_t InitGRPC(string, double, unsigned int, double, string, string , unsigned int)

        # Close joint reader with cleanup
        void Close()

        # Return number of controlled joints
        int GetJointCount()

        # Return the resolution in degree of the populations encoding the joint angles.
        vector[double] GetJointsDegRes()

        # Return the size of the populations encoding the joint angles
        vector[unsigned int] GetNeuronsPerJoint()

        # Read all joints and return joint angles directly in degree as double values
        vector[double] ReadDoubleAll()

        # Read multiple joints and return joint angles directly in degree as double values
        vector[double] ReadDoubleMultiple(vector[int])

        # Read one joint and return joint angle directly in degree as double value
        double ReadDoubleOne(int)

        # Read all joints and return the joint angles encoded in populations.
        vector[vector[double]] ReadPopAll()

        # Read multiple joints and return the joint angles encoded in populations.
        vector[vector[double]] ReadPopMultiple(vector[int])

        # Read one joint and return the joint angle encoded in a population.
        vector[double] ReadPopOne(int)

        void setRegister(bint)
        bint getRegister()

        cmap[string, string] getParameter()

cdef class PyJointReader:
    cdef shared_ptr[JointReader] cpp_joint_reader
    cdef str name
    cdef str part


