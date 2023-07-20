# distutils: language = c++
# cython: language_level = 3
# cython: binding=True
# cython: embedsignature=True

"""
   Copyright (C) 2019-2022 Torsten Fietzek; Helge Ülo Dinkelbach

   Joint_Writer.pyx is part of the ANNarchy iCub interface

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

cdef extern from "Joint_Writer.hpp":

    cdef cppclass JointWriter:
        JointWriter() except +

        # Initialize the joint writer with given parameters
        bool_t Init(string, unsigned int, double, double, string)

        # Initialize the joint writer with given parameters for use with gRPC
        bool_t InitGRPC(string, unsigned int, vector[int], string, bool_t, double, double, string, string, unsigned int)

        # Close joint writer with cleanup
        void Close()

        # Return number of controlled joints
        int GetJointCount()

        # Return the resolution in degree of the populations encoding the joint angles.
        vector[double] GetJointsDegRes()

        # Return the size of the populations encoding the joint angles
        vector[unsigned int] GetNeuronsPerJoint()


        # Return the limits of joint angles in degree.
        vector[vector[double]] GetJointLimits()


        # Return the lower limits of joint angles in degree.
        vector[double] GetJointLimitsMin()


        # Return the upper limits of joint angles in degree.
        vector[double] GetJointLimitsMax()

        # Set the joint velocity
        bool_t SetJointVelocity(double, int)

        # Set the joint acceleration
        bool_t SetJointAcceleration(double, int)

        # Set the control mode for the respective joint/Joints -> e.g. position or velocity
        bool_t SetJointControlMode(string, int)

        # Write all joints with double values.
        bool_t WriteDoubleAll(vector[double], string, bool_t)

        # Write all joints with double values.
        bool_t WriteDoubleMultiple(vector[double], vector[int], string, bool_t)

        # Write one joint with double value.
        bool_t WriteDoubleOne(double, int, string, bool_t)

        # Write all joints with joint angles encoded in populations
        bool_t WritePopAll(vector[vector[double]], string, bool_t)

        # Write all joints with joint angles encoded in populations
        bool_t WritePopMultiple(vector[vector[double]], vector[int], string, bool_t)

        # Write one joint with the joint angle encoded in a population.
        bool_t WritePopOne(vector[double], int, string, bool_t)

        void setRegister(bint)
        bint getRegister()

        # Return decoded joint angle
        double Decode_ext(vector[double], int)

        void Retrieve_ANNarchy_Input_SJ()
        void Write_ANNarchy_Input_SJ()

        void Retrieve_ANNarchy_Input_SJ_enc()
        void Write_ANNarchy_Input_SJ_enc()

        void Retrieve_ANNarchy_Input_MJ()
        void Write_ANNarchy_Input_MJ()

        void Retrieve_ANNarchy_Input_MJ_enc()
        void Write_ANNarchy_Input_MJ_enc()

        void Retrieve_ANNarchy_Input_AJ()
        void Write_ANNarchy_Input_AJ()

        void Retrieve_ANNarchy_Input_AJ_enc()
        void Write_ANNarchy_Input_AJ_enc()

        cmap[string, string] getParameter()

cdef class PyJointWriter:
    cdef shared_ptr[JointWriter] _cpp_joint_writer
    cdef str _name
    cdef str _part
