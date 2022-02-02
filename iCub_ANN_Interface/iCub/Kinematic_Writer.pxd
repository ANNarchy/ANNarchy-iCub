# distutils: language = c++
# cython: language_level = 3

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

cdef extern from "Kinematic_Writer.hpp":

    cdef cppclass KinematicWriter:
        KinematicWriter() except +

        # Initialize the joint writer with given parameters
        bool_t Init(string, float, string)

        # Initialize the joint writer with given parameters
        bool_t InitGRPC(string, float, string, string, unsigned int)

        # Close joint writer with cleanup
        void Close()

        # Return number of controlled joints
        int GetDOF()

        vector[double] solveInvKin(vector[double], vector[int])

        void setRegister(bint)
        bint getRegister()

        cmap[string, string] getParameter()

cdef class PyKinematicWriter:
    cdef shared_ptr[KinematicWriter] cpp_kin_writer
    cdef str name
    cdef str part

