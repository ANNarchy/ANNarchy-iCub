
# distutils: language = c++
# cython: language_level = 3
# cython: binding=True
# cython: embedsignature=True

"""
   Copyright (C) 2019-2022 Torsten Fietzek; Helge Ülo Dinkelbach

   Skin_Reader.pyx is part of the ANNarchy iCub interface

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
from libcpp.string cimport string
from libcpp.memory cimport make_shared
from cython.operator cimport dereference as deref

from .Skin_Reader cimport SkinReader
from .iCub_Interface cimport ANNiCub_wrapper

import numpy as np

cdef class PySkinReader:

    # init method
    def __cinit__(self):
        print("Initialize iCub Interface: Skin Reader.")
        self._cpp_skin_reader = make_shared[SkinReader]()

    # close method
    def __dealloc__(self):
        print("Close iCub Interface: Skin Reader.")
        self._cpp_skin_reader.reset()

    '''
    # Access to skin reader member functions
    '''

    # init skin reader with given parameters
    def init(self, ANNiCub_wrapper iCub, str name, str arm, norm=True, str ini_path="../data/"):
        """Initialize skin reader with given parameters.

        Args:
            iCub (ANNiCub_wrapper): main interface wrapper
            name (str): individual name for the skin reader module
            arm (str): character to choose the arm side (r/R for right; l/L for left)
            norm (bool, optional): if true, the sensor data are returned normalized (iCub [0..255]; normalized [0..1]). Defaults to True.
            ini_path (str, optional): Path to the "interface_param.ini"-file. Defaults to "../data/".

        Returns:
            bool: return True/False, indicating success/failure
        """
        self._part = arm
        # preregister module for some prechecks e.g. arm already in use
        if iCub.register_skin_reader(name, self):
            retval = deref(self._cpp_skin_reader).Init(name.encode('UTF-8'), arm.encode('UTF-8')[0], norm.__int__(), ini_path.encode('UTF-8'))
            if not retval:
                iCub.unregister_skin_reader(self)
            return retval
        else:
            return False

    # initialize the skin reader with given parameters, including the gRPC based connection
    def init_grpc(self, ANNiCub_wrapper iCub, str name, str arm, norm=True, str ini_path="../data/", str ip_address="0.0.0.0", unsigned int port=50015):
        """Initialize the skin reader with given parameters, including the gRPC based connection.

        Args:
            iCub (ANNiCub_wrapper): main interface wrapper
            name (str): individual name for the skin reader module
            arm (str): character to choose the arm side (r/R for right; l/L for left)
            norm (bool, optional): if true, the sensor data are returned normalized (iCub [0..255]; normalized [0..1]). Defaults to True.
            ini_path (str, optional): Path to the "interface_param.ini"-file. Defaults to "../data/".
            ip_address (str, optional): gRPC server ip address. Defaults to "0.0.0.0".
            port (unsigned int, optional): gRPC server port. Defaults to 50015.

        Returns:
            bool: return True/False, indicating success/failure
        """
        # we need to transform py-string to c++ compatible string
        self._part = arm
        # preregister module for some prechecks e.g. arm already in use
        if iCub.register_skin_reader(name, self):
            retval = deref(self._cpp_skin_reader).InitGRPC(name.encode('UTF-8'), arm.encode('UTF-8')[0], norm.__int__(), ini_path.encode('UTF-8'), ip_address.encode('UTF-8'), port)
            if not retval:
                iCub.unregister_skin_reader(self)
            return retval
        else:
            return False

    # close and clean skin reader
    def close(self, ANNiCub_wrapper iCub):
        """Close and clean skin reader.

        Args:
            iCub (ANNiCub_wrapper): main interface wrapper
        """
        iCub.unregister_skin_reader(self)
        self._part = ""
        deref(self._cpp_skin_reader).Close()

    # return tactile data for upper arm skin
    def get_tactile_arm(self):
        """Return tactile data for the upper arm skin.

        Returns:
            NDarray (vector[vector[double]]): tactile data of the arm part of the skin, values: non-normalized: 0..255 ; normalized: 0..1.0
        """
        return np.array(deref(self._cpp_skin_reader).GetTactileArm())

    # return size of tactile data for upper arm skin
    def get_tactile_arm_size(self):
        """Return size of tactile data for the upper arm skin.

        Returns:
            unsigned int: size of sensor data vector -> upper arm section
        """
        return deref(self._cpp_skin_reader).GetTactileArmSize()

    # return tactile data for forearm skin
    def get_tactile_forearm(self):
        """Return tactile data for the forearm skin.

        Returns:
            NDarray (vector[vector[double]]): tactile data of the forearm part of the skin, values: non-normalized: 0..255 ; normalized: 0..1.0
        """
        return np.array(deref(self._cpp_skin_reader).GetTactileForearm())

    # return size of tactile data for forearm skin
    def get_tactile_forearm_size(self):
        """Return size of tactile data for the forearm skin

        Returns:
            unsigned int: size of sensor data vector -> forearm section
        """
        return deref(self._cpp_skin_reader).GetTactileForearmSize()

    # return tactile data for hand skin
    def get_tactile_hand(self):
        """Return tactile data for the hand skin.

        Returns:
            NDarray (vector[vector[double]]): tactile data of the hand part of the skin, values: non-normalized: 0..255 ; normalized: 0..1.0
        """
        return np.array(deref(self._cpp_skin_reader).GetTactileHand())

    # return size of tactile data for hand skin
    def get_tactile_hand_size(self):
        """Return size of tactile data for the hand skin.

        Returns:
            unsigned int: size of sensor data vector -> hand section
        """
        return deref(self._cpp_skin_reader).GetTactileHandSize()

    # return the taxel positions given by the ini files
    def get_taxel_pos(self, str skin_part):
        """Return the taxel positions given by the ini files from the icub-main repo.

        Args:
            skin_part (str): skin part to load the data for ("arm", "forearm", "hand")

        Returns:
            NDarray (vector[vector[double]]): Vector containing taxel positions -> reference frame depending on skin part
        """
        # we need to transform py-string to c++ compatible string
        cdef string s1 = skin_part.encode('UTF-8')
        return np.array(deref(self._cpp_skin_reader).GetTaxelPos(s1))

    # read sensor data
    def read_tactile(self):
        """Read sensor data for one step

        Returns:
            bool: return True/False, indicating success/failure
        """        
        return deref(self._cpp_skin_reader).ReadTactile()

    # read tactile data for upper arm skin
    def read_skin_arm(self):
        """Read tactile data for upper arm skin.

        Returns:
            NDarray (vector[double]): tactile data of the arm part of the skin, values: non-normalized: 0..255 ; normalized: 0..1.0
        """
        return np.array(deref(self._cpp_skin_reader).ReadSkinArm())

    # read tactile data for forearm skin
    def read_skin_forearm(self):
        """Read tactile data for forearm skin.

        Returns:
            NDarray (vector[double]): tactile data of the forearm part of the skin, values: non-normalized: 0..255 ; normalized: 0..1.0
        """
        return np.array(deref(self._cpp_skin_reader).ReadSkinForearm())

    # read tactile data for hand skin
    def read_skin_hand(self):
        """Read tactile data for hand skin.

        Returns:
            NDarray (vector[double]): tactile data of the hand part of the skin, values: non-normalized: 0..255 ; normalized: 0..1.0
        """
        return np.array(deref(self._cpp_skin_reader).ReadSkinHand())
