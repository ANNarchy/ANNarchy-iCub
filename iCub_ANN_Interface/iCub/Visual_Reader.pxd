# distutils: language = c++
# cython: language_level = 3

"""
   Copyright (C) 2019-2021 Torsten Fietzek; Helge Ülo Dinkelbach

   Visual_Reader.pyx is part of the iCub ANNarchy interface

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

cdef extern from "Visual_Reader.hpp":

    cdef cppclass VisualReader:
        ctypedef double precision

        VisualReader() except +

        # Init Visual reader with given parameters for image resolution, field of view and eye selection.
        bool_t Init(char, double, double, int, int, int, bool_t, string)

        # Init Visual reader with given parameters for image resolution, field of view and eye selection and grpc communication.
        bool_t InitGRPC(char, double, double, int, int, int, bool_t, string, string , unsigned int)

        # Read image vector from the image buffer and remove it from the internal buffer. Call twice in binocular mode (first right eye image second left eye image)
        vector[precision] ReadFromBuf(bool_t, int)

        # Start reading images from the iCub with YARP-RFModule.
        bool_t Start(int argc, char *[])

        # Stop reading images from the iCub, by terminating the RFModule.
        void Stop()

        # Return the image count in the image buffer.
        int ImgsInBuffer()

        # Read a set of images from the robot cameras.
        vector[vector[precision]] ReadRobotEyes()

        # Close Visual Reader module.
        void Close()

        void setRegister(bint)
        bint getRegister()

cdef class PyVisualReader:
    cdef shared_ptr[VisualReader] cpp_visual_reader
    cdef str name
    cdef str part

