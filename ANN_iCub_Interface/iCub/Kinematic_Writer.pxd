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
   but WITHOUT ANY WARRANTY without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this headers. If not, see <http://www.gnu.org/licenses/>.
 """

from libcpp.string cimport string
from libcpp.vector cimport vector
from libcpp cimport bool as bool_t
from libcpp.memory cimport shared_ptr
from libcpp.map cimport map as cmap

from .Module_Base_Class cimport Mod_BaseClass, PyModuleBase

cdef extern from "Kinematic_Writer.hpp":

    cdef cppclass KinematicWriter(Mod_BaseClass):
        KinematicWriter() except +

        # Initialize the joint writer with given parameters
        bool_t Init(string, float, string, bool_t, bool_t)

        # Initialize the joint writer with given parameters
        bool_t InitGRPC(string, float, string, string, unsigned int, bool_t, bool_t)

        # Close joint writer with cleanup
        void Close()

        # Return number of controlled joints
        int GetDOF()

        # Get joints being part of active kinematic chain
        vector[int] GetDOFLinks()

        # Set blocked links
        void BlockLinks(vector[int])

        # Get blocked links
        vector[int] GetBlockedLinks()

        # Released links of kinematic chain -> add links to active kinematic chain
        void ReleaseLinks(vector[int])

        # Get joint angles
        vector[double] GetJointAngles()

        # Set joint angles for forward kinematic in offline mode
        vector[double] SetJointAngles(vector[double])


        vector[double] SolveInvKin(vector[double], vector[int])

        # void setRegister(bint)
        # bint getRegister()

        # cmap[string, string] getParameter()

cdef class PyKinematicWriter(PyModuleBase):
    cdef shared_ptr[KinematicWriter] _cpp_kin_writer
    