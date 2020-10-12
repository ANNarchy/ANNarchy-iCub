# distutils: language = c++
# cython: language_level = 3

"""
   Copyright (C) 2019-2020 Torsten Follak; Helge Ülo Dinkelbach

   Visual_Reader.pyx is part of the iCub ANNarchy interface

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   The iCub ANNarchy interface is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this headers. If not, see <http://www.gnu.org/licenses/>.
 """

from libcpp.string cimport string
from libcpp.vector cimport vector
from libcpp cimport bool as bool_t
from libcpp.memory cimport shared_ptr
from libc.stdlib cimport malloc, free
from cython.operator cimport dereference as deref

from Visual_Reader cimport VisualReader

import numpy as np

cdef class PyVisualReader:

    def __cinit__(self):
        print("Initialize iCub Interface: Visual Reader.")

    @staticmethod
    cdef PyVisualReader from_ptr(shared_ptr[VisualReader] _ptr):
        # adapted from https://cython.readthedocs.io/en/latest/src/userguide/extension_types.html
        # Call to __new__ bypasses __init__ constructor
        cdef PyVisualReader wrapper = PyVisualReader.__new__(PyVisualReader)
        wrapper.cpp_visual_reader = _ptr
        return wrapper

    ### Access to visual reader member functions
    # init Visual reader with given parameters for image resolution, field of view and eye selection
    def init(self, eye, fov_width=60, fov_height=48, img_width=320, img_height=240, max_buffer_size=10, fast_filter=True):
        """
            Calls bool VisualReader::Init(char eye, double fov_width, double fov_height, int img_width, int max_buffer_size, int img_height)

            function:
                Initialize Visual reader with given parameters for image resolution, field of view and eye selection

            params:
                char eye            -- characteer representing the selected eye (l/L; r/R)
                double fov_width    -- output field of view width in degree [0, 60] (input fov width: 60°)
                double fov_height   -- output field of view height in degree [0, 48] (input fov height: 48°)
                int img_width       -- output image width in pixel (input width: 320px)
                int img_height      -- output image height in pixel (input height: 240px)
                fast_filter         -- flag to select the filter for image upscaling; True for a faster filter; default value is True

            return:
                bool                -- return True, if successful
        """
        cdef char e = eye.encode('UTF-8')[0]

        # call the interface
        return deref(self.cpp_visual_reader).Init(e, fov_width, fov_height, img_width, img_height, max_buffer_size, fast_filter)

    # return image vector from the image buffer and remove it from the buffer
    def read_from_buffer(self):
        """
            Calls std::vector<precision> VisualReader::ReadFromBuf()

            function:
                Return image vector from the image buffer and remove it from the buffer. 
                The return type depends on the selected precision (float/double).

            return:
                std::vector<precision>     -- image (1D-vector) from the image buffer
        """

        # call the interface
        return np.array(deref(self.cpp_visual_reader).ReadFromBuf())

    # start reading images from the iCub with a YARP-RFModule
    def start(self):
        """
            Calls void VisualReader::Start(int argc, char *argv[])

            function:
                Start reading images from the iCub with a YARP-RFModule
        """
        argv=[]
        # Declare char**
        cdef char** c_argv
        argc = len(argv)
        # Allocate memory
        c_argv = <char**>malloc(argc * sizeof(char*))
        # Check if allocation went fine
        if c_argv is NULL:
            raise MemoryError()
        # Convert str to char* and store it into our char**
        for i in range(argc):
            argv[i] = argv[i].encode('UTF-8')
            c_argv[i] = argv[i]
        # call the interface
        start = deref(self.cpp_visual_reader).Start(argc, c_argv)
        # Let him go
        free(c_argv)
        return start

    # stop reading images from the iCub, by terminating the RFModule
    def stop(self):
        """
            Calls void VisualReader::Stop()

            function:
                Stop reading images from the iCub, by terminating the RFModule
        """

        # call the interface
        deref(self.cpp_visual_reader).Stop()

    def imgs_in_buffer(self):
        """
            Calls void VisualReader::Stop()

            function:
                Stop reading images from the iCub, by terminating the RFModule
        """

        # call the interface
        return deref(self.cpp_visual_reader).ImgsInBuffer()

    ### end access to visual reader member functions