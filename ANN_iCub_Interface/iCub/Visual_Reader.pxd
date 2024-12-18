# distutils: language = c++
# cython: language_level = 3
# cython: binding=True
# cython: embedsignature=True

"""
   Copyright (C) 2019-2022 Torsten Fietzek; Helge Ülo Dinkelbach

   Visual_Reader.pyx is part of the ANNarchy iCub interface

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
from libc.stdint cimport uint8_t

from .Module_Base_Class cimport Mod_BaseClass, PyModuleBase

cdef extern from "Visual_Reader.hpp":

    cdef cppclass VisualReader(Mod_BaseClass):
        ctypedef double precision

        VisualReader() except +

        # Init Visual reader with given parameters for image resolution, field of view and eye selection.
        bool_t Init(char, double, double, int, int, bool_t, string)

        # Init Visual reader with given parameters for image resolution, field of view and eye selection and grpc communication.
        bool_t InitGRPC(char, double, double, int, int, bool_t, string, string, unsigned int)

        # Read a set of images from the robot cameras.
        vector[vector[precision]] ReadRobotEyes()

        vector[uint8_t] RetrieveRobotEye()

        # Close Visual Reader module.
        void Close()

        # void setRegister(bint)
        # bint getRegister()

        # cmap[string, string] getParameter()

cdef class PyVisualReader(PyModuleBase):
    cdef shared_ptr[VisualReader] _cpp_visual_reader
