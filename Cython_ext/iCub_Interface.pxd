# distutils: language = c++
# cython: language_level = 3

"""
   Copyright (C) 2019-2021 Torsten Fietzek; Helge Ülo Dinkelbach

   iCubCPP.pxd is part of the iCub ANNarchy interface

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   The iCub ANNarchy interface is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this headers. If not, see [http://www.gnu.org/licenses/].
 """

from Visual_Reader cimport PyVisualReader

cdef extern from "Interface_iCub.hpp":

    cdef cppclass iCubANN:
        iCubANN() except +

    # Instances:
    iCubANN my_interface # defined in Interface_iCub.cpp


cdef class iCubANN_wrapper:

    cdef dict __dict__

    cdef dict joint_reader
    cdef dict joint_reader_parts

    cdef dict joint_writer
    cdef dict joint_writer_parts

    cdef dict skin_reader
    cdef dict skin_reader_parts

    cdef PyVisualReader visual_input
