
# distutils: language = c++
# cython: language_level = 3

"""
   Copyright (C) 2019-2020 Torsten Fietzek; Helge Ülo Dinkelbach

   Skin_Reader.pyx is part of the iCub ANNarchy interface

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


cdef extern from "Skin_Reader.hpp":

    cdef cppclass SkinReader:
        SkinReader() except +

        # Initialize skin reader with given parameters.
        bool_t Init(char, bool_t, string)

        #  Close and clean skin reader
        void Close()

        # Return tactile data for upper arm skin.
        vector[vector[double]] GetTactileArm()

        # Return tactile data for forearm skin.
        vector[vector[double]] GetTactileForearm()

        # Return tactile data for hand skin.
        vector[vector[double]] GetTactileHand()

        # Return the taxel positions given by the ini files.
        vector[vector[double]] GetTaxelPos(string)

        # The sensor data is read and buffered inside. It can be accessed through GetTactileArm, GetTactileForearm and GetTactileHand.
        bool_t ReadTactile()


cdef class PySkinReader:
    cdef shared_ptr[SkinReader] cpp_skin_reader

    @staticmethod
    cdef PySkinReader from_ptr(shared_ptr[SkinReader] _ptr)
