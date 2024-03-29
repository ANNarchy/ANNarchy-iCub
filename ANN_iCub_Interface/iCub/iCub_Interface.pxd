# distutils: language = c++
# cython: language_level = 3
# cython: binding=True
# cython: embedsignature=True
# cython: embedsignature.format=python

"""
   Copyright (C) 2019-2022 Torsten Fietzek; Helge Ülo Dinkelbach

   iCubCPP.pxd is part of the ANNarchy iCub interface

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   The ANNarchy iCub interface is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this headers. If not, see [http://www.gnu.org/licenses/].
 """

cdef extern from "Interface_iCub.hpp":

    cdef cppclass ANNiCub:
        ANNiCub() except +

    # Instances:
    ANNiCub my_interface    # defined in Interface_iCub.cpp


cdef class ANNiCub_wrapper:

    cdef dict __dict__

    cdef dict _joint_reader
    cdef dict _joint_reader_parts

    cdef dict _joint_writer
    cdef dict _joint_writer_parts

    cdef dict _skin_reader
    cdef dict _skin_reader_parts

    cdef dict _visual_reader

    cdef dict _kinematic_reader
    cdef dict _kinematic_writer
