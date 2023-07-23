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
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this headers. If not, see <http://www.gnu.org/licenses/>.
 """

from libcpp.memory cimport make_shared
from cython.operator cimport dereference as deref

from .Visual_Reader cimport VisualReader
from .iCub_Interface cimport ANNiCub_wrapper

import numpy as np

cdef class PyVisualReader:

    # init method
    def __cinit__(self):
        print("Initialize iCub Interface: Visual Reader.")
        self._cpp_visual_reader = make_shared[VisualReader]()

    # close method
    def __dealloc__(self):
        print("Close iCub Interface: Visual Reader.")
        self._cpp_visual_reader.reset()

    '''
    # Access to visual reader member functions
    '''

    # init Visual reader with given parameters for image resolution, field of view and eye selection
    def init(self, ANNiCub_wrapper iCub, str name, str eye, double fov_width=60., double fov_height=48., int img_width=320, int img_height=240, fast_filter=True,
             str ini_path="../data/"):
        """Initialize Visual reader with given parameters.

        Parameters
        ----------
        ANNiCub_wrapperiCub : _type_
            main interface wrapper
        name : str
            name for the visual reader module
        eye : str
            character representing the selected eye (l/L; r/R; b/B)
        fov_width : double
            output field of view width in degree [0, 60] (input fov width: 60°). (Default value = 60)
        fov_height : double
            output field of view height in degree [0, 48] (input fov height: 48°). (Default value = 48)
        img_width : int
            output image width in pixel (input width: 320px). (Default value = 320)
        img_height : int
            output image height in pixel (input height: 240px). (Default value = 240)
        fast_filter : bool
            flag to select the filter for image upscaling; True for a faster filter. (Default value = True)
        ini_path : str
            Path to the "interface_param.ini"-file. (Default value = "../data/")

        Returns
        -------
        bool
            return True/False, indicating success/failure
        """
        # ini_path = os.path.abspath(ini_path)
        self._part = eye
        # preregister module for some prechecks e.g. name already in use
        if iCub.register_vis_reader(name, self):
            # call the interface
            retval = deref(self._cpp_visual_reader).Init(eye.encode('UTF-8')[0], fov_width, fov_height, img_width, img_height, fast_filter, ini_path.encode('UTF-8'))
            if not retval:
                iCub.unregister_vis_reader(self)
            return retval
        else:
            return False

    # init Visual reader with given parameters for image resolution, field of view and eye selection
    def init_grpc(self, ANNiCub_wrapper iCub, str name, str eye, double fov_width=60, double fov_height=48, int img_width=320, int img_height=240, fast_filter=True,
                  str ini_path="../data/", str ip_address="0.0.0.0", unsigned int port=50000):
        """Initialize the visual reader with given parameters, including the gRPC based connection.

        Parameters
        ----------
        ANNiCub_wrapperiCub : _type_
            main interface wrapper
        name : str
            name for the visual reader module
        eye : str
            character representing the selected eye (l/L; r/R; b/B)
        fov_width : double
            output field of view width in degree [0, 60] (input fov width: 60°). (Default value = 60)
        fov_height : double
            output field of view height in degree [0, 48] (input fov height: 48°). (Default value = 48)
        img_width : int
            output image width in pixel (input width: 320px). (Default value = 320)
        img_height : int
            output image height in pixel (input height: 240px). (Default value = 240)
        fast_filter : bool
            flag to select the filter for image upscaling; True for a faster filter. (Default value = True)
        ini_path : str
            Path to the "interface_param.ini"-file. (Default value = "../data/")
        strip_address : str
            gRPC server ip address. (Default value = "0.0.0.0")
        unsignedintport : int
            gRPC server port. (Default value = 50000)

        Returns
        -------
        bool
            return True/False, indicating success/failure
        """
        self._part = eye
        # preregister module for some prechecks e.g. eye already in use
        if iCub.register_vis_reader(name, self):
            retval = deref(self._cpp_visual_reader).InitGRPC(eye.encode('UTF-8')[0], fov_width, fov_height, img_width, img_height, fast_filter, ini_path.encode('UTF-8'),
                                                             ip_address.encode('UTF-8'), port)
            if not retval:
                iCub.unregister_vis_reader(self)
            return retval
        else:
            return False

    # return camera image_s in a vector
    def read_robot_eyes(self):
        """Return image_s from the iCub camera_s. The return type depends on the selected precision (float/double).

        Parameters
        ----------

        Returns
        -------
        type
            NDarray (vector[vector[precision]]): image_s from the camera_s in the form vector of image_s and as flattened image
        """
        # return np.array(deref(self._cpp_visual_reader).ReadRobotEyes(), dtype=np.float64)
        return np.array(deref(self._cpp_visual_reader).ReadRobotEyes())

    # return flattened RGB-image
    def retrieve_robot_eye(self):
        """Return RGB-image from one of the iCub cameras. Does not work in 'B' mode.

        Parameters
        ----------

        Returns
        -------
        type
            NDarrray (vector[int]): RGB-camera image flattened
        """
        return np.array(deref(self._cpp_visual_reader).RetrieveRobotEye(), dtype=np.uint8)
        # return deref(self._cpp_visual_reader).RetrieveRobotEye()

    # close module
    def close(self, ANNiCub_wrapper iCub):
        """Close the visual reader module

        Parameters
        ----------
        iCub : ANNiCub_wrapper
            main interface wrapper

        Returns
        -------

        """
        iCub.unregister_vis_reader(self)
        self._part = ""
        deref(self._cpp_visual_reader).Close()
