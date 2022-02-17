# distutils: language = c++
# cython: language_level = 3

"""
   Copyright (C) 2019-2022 Torsten Fietzek; Helge Ülo Dinkelbach

   Kinematic_Reader.pyx is part of the ANNarchy iCub interface

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   The ANNarchy iCub interface is distributed in the hope that it will be useful,
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

cdef extern from "Kinematic_Reader.hpp":

    cdef cppclass KinematicReader:
        KinematicReader() except +

        # Initialize the joint reader with given parameters
        bool_t Init(string, float, string)

        # Initialize the joint reader with given parameters
        bool_t InitGRPC(string, float, string, string, unsigned int)

        # Close joint reader with cleanup
        void Close()

        # Return number of controlled joints
        int GetDOF()

        vector[double] GetCartesianPosition(unsigned int)
        vector[double] GetHandPosition()

        void setRegister(bint)
        bint getRegister()

        cmap[string, string] getParameter()

cdef class PyKinematicReader:
    cdef shared_ptr[KinematicReader] cpp_kin_reader
    cdef str name
    cdef str part

