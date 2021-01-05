# distutils: language = c++
# cython: language_level = 3

"""
   Copyright (C) 2019-2021 Torsten Fietzek; Helge Ülo Dinkelbach

   Joint_Writer.pyx is part of the iCub ANNarchy interface

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

cdef extern from "Joint_Writer.hpp":

    cdef cppclass JointWriter:
        JointWriter() except +

        # Initialize the joint writer with given parameters
        bool_t Init(string, int, double, double, string)

        # Close joint writer with cleanup
        void Close()

        # Return number of controlled joints
        int GetJointCount()

        # Return the resolution in degree of the populations encoding the joint angles.
        vector[double] GetJointsDegRes()

        # Return the size of the populations encoding the joint angles
        vector[int] GetNeuronsPerJoint()

        # Return the size of the populations encoding the joint angles
        bool_t SetJointVelocity(double, int)

        # Return the size of the populations encoding the joint angles
        bool_t SetJointControlMode(string, int)

        # Write all joints with double values.
        bool_t WriteDoubleAll(vector[double], bool_t, string)


        # Write all joints with double values.
        bool_t WriteDoubleMultiple(vector[double], vector[int], bool_t, string)


        # Write one joint with double value.
        bool_t WriteDoubleOne(double, int, bool_t, string)


        # Write all joints with joint angles encoded in populations
        bool_t WritePopAll(vector[vector[double]], bool_t, string)


        # Write all joints with joint angles encoded in populations
        bool_t WritePopMultiple(vector[vector[double]], vector[int], bool_t, string)


        # Write one joint with the joint angle encoded in a population.
        bool_t WritePopOne(vector[double], int, bool_t, string)


cdef class PyJointWriter:
    cdef shared_ptr[JointWriter] cpp_joint_writer

    @staticmethod
    cdef PyJointWriter from_ptr(shared_ptr[JointWriter] _ptr)
