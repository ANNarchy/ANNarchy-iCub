
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
from .Module_Base_Class cimport PyModuleBase

import numpy as np

cdef class PySkinReader(PyModuleBase):

    # init method
    def __cinit__(self):
        print("Initialize iCub Interface: Skin Reader.")
        self._cpp_skin_reader = make_shared[SkinReader]()

    # close method
    def __dealloc__(self):
        print("Close iCub Interface: Skin Reader.")
        self._cpp_skin_reader.reset()


    # register skin reader module
    def _register(self, name: str, ANNiCub_wrapper iCub):
        """Register Skin Reader module at the main wrapper.
            -> For internal use only.

        Parameters
        ----------
        name : str
            name given to the Skin Reader
        iCub : ANNiCub_wrapper
            main interface wrapper

        Returns
        -------
        bool
            True/False on Success/Failure
        """
        if deref(self._cpp_skin_reader).getRegister():
            print("[Interface iCub] Skin Reader module is already registered!")
            return False
        else:
            if name in iCub._skin_reader:
                print("[Interface iCub] Skin Reader module name is already used!")
                return False
            else:
                iCub._skin_reader[name] = self
                self._name = name
                deref(self._cpp_skin_reader).setRegister(1)
                return True

    # unregister skin reader module
    def _unregister(self, ANNiCub_wrapper iCub):
        """Unregister Skin Reader module at the main wrapper.
            -> For internal use only.

        Parameters
        ----------
        iCub : ANNiCub_wrapper
            main interface wrapper

        Returns
        -------
        bool
            True/False on Success/Failure
        """
        if deref(self._cpp_skin_reader).getRegister():
            deref(self._cpp_skin_reader).setRegister(0)
            iCub._skin_reader.pop(self._name, None)
            self._name = ""
            return True
        else:
            print("[Interface iCub] Skin Reader module is not yet registered!")
            return False

    def _get_parameter(self):
        return deref(self._cpp_skin_reader).getParameter()


    '''
    # Access to skin reader member functions
    '''

    # init skin reader with given parameters
    def init(self, ANNiCub_wrapper iCub, str name, str arm, norm=True, str ini_path="../data/"):
        """Initialize skin reader with given parameters.

        Parameters
        ----------
        iCub : ANNiCub_wrapper
            main interface wrapper
        name : str
            individual name for the skin reader module
        arm : str
            character to choose the arm side (r/R for right; l/L for left)
        norm : bool
            if true, the sensor data are returned normalized (iCub [0..255]; normalized [0..1]). (Default value = True)
        ini_path : str
            Path to the "interface_param.ini"-file. (Default value = "../data/")

        Returns
        -------
        bool
            return True/False, indicating success/failure
        """
        self._part = arm
        # preregister module for some prechecks e.g. arm already in use
        if self._register(name, iCub):
            retval = deref(self._cpp_skin_reader).Init(name.encode('UTF-8'), arm.encode('UTF-8')[0], norm.__int__(), ini_path.encode('UTF-8'))
            if not retval:
                self._unregister(iCub)
            return retval
        else:
            return False

    # initialize the skin reader with given parameters, including the gRPC based connection
    def init_grpc(self, ANNiCub_wrapper iCub, str name, str arm, norm=True, str ini_path="../data/", str ip_address="0.0.0.0", unsigned int port=50015):
        """Initialize the skin reader with given parameters, including the gRPC based connection.

        Parameters
        ----------
        iCub : ANNiCub_wrapper
            main interface wrapper
        name : str
            individual name for the skin reader module
        arm : str
            character to choose the arm side (r/R for right; l/L for left)
        norm : bool
            if true, the sensor data are returned normalized (iCub [0..255]; normalized [0..1]). (Default value = True)
        ini_path : str
            Path to the "interface_param.ini"-file. (Default value = "../data/")
        ip_address : str
            gRPC server ip address. (Default value = "0.0.0.0")
        port : unsigned int
            gRPC server port. (Default value = 50015)

        Returns
        -------
        bool
            return True/False, indicating success/failure
        """
        # we need to transform py-string to c++ compatible string
        self._part = arm
        # preregister module for some prechecks e.g. arm already in use
        if self._register(name, iCub):
            retval = deref(self._cpp_skin_reader).InitGRPC(name.encode('UTF-8'), arm.encode('UTF-8')[0], norm.__int__(), ini_path.encode('UTF-8'), ip_address.encode('UTF-8'), port)
            if not retval:
                self._unregister(iCub)
            return retval
        else:
            return False

    # close and clean skin reader
    def close(self, ANNiCub_wrapper iCub):
        """Close and clean skin reader.

        Parameters
        ----------
        iCub : ANNiCub_wrapper
            main interface wrapper

        Returns
        -------

        """
        self._unregister(iCub)
        self._part = ""
        deref(self._cpp_skin_reader).Close()

    # return tactile data for upper arm skin
    def get_tactile_arm(self):
        """Return tactile data for the upper arm skin.

        Parameters
        ----------

        Returns
        -------
        type
            NDarray (vector[vector[double]]): tactile data of the arm part of the skin, values: non-normalized: 0..255 ; normalized: 0..1.0
        """
        return np.array(deref(self._cpp_skin_reader).GetTactileArm())

    # return size of tactile data for upper arm skin
    def get_tactile_arm_size(self):
        """Return size of tactile data for the upper arm skin.

        Parameters
        ----------

        Returns
        -------
        type
            unsigned int: size of sensor data vector -> upper arm section
        """
        return deref(self._cpp_skin_reader).GetTactileArmSize()

    # return tactile data for forearm skin
    def get_tactile_forearm(self):
        """Return tactile data for the forearm skin.

        Parameters
        ----------

        Returns
        -------
        type
            NDarray (vector[vector[double]]): tactile data of the forearm part of the skin, values: non-normalized: 0..255 ; normalized: 0..1.0
        """
        return np.array(deref(self._cpp_skin_reader).GetTactileForearm())

    # return size of tactile data for forearm skin
    def get_tactile_forearm_size(self):
        """Return size of tactile data for the forearm skin

        Parameters
        ----------

        Returns
        -------
        type
            unsigned int: size of sensor data vector -> forearm section
        """
        return deref(self._cpp_skin_reader).GetTactileForearmSize()

    # return tactile data for hand skin
    def get_tactile_hand(self):
        """Return tactile data for the hand skin.

        Parameters
        ----------

        Returns
        -------
        type
            NDarray (vector[vector[double]]): tactile data of the hand part of the skin, values: non-normalized: 0..255 ; normalized: 0..1.0
        """
        return np.array(deref(self._cpp_skin_reader).GetTactileHand())

    # return size of tactile data for hand skin
    def get_tactile_hand_size(self):
        """Return size of tactile data for the hand skin.

        Parameters
        ----------

        Returns
        -------
        type
            unsigned int: size of sensor data vector -> hand section
        """
        return deref(self._cpp_skin_reader).GetTactileHandSize()

    # return the taxel positions given by the ini files
    def get_taxel_pos(self, str skin_part):
        """Return the taxel positions given by the ini files from the icub-main repo.

        Parameters
        ----------
        skin_part : str:
            skin part to load the data for ("arm", "forearm", "hand")

        Returns
        -------
        type
            NDarray (vector[vector[double]]): Vector containing taxel positions -> reference frame depending on skin part
        """
        # we need to transform py-string to c++ compatible string
        cdef string s1 = skin_part.encode('UTF-8')
        return np.array(deref(self._cpp_skin_reader).GetTaxelPos(s1))

    # read sensor data
    def read_tactile(self):
        """Read sensor data for one step

        Parameters
        ----------

        Returns
        -------
        bool
            return True/False, indicating success/failure
        """
        return deref(self._cpp_skin_reader).ReadTactile()

    # read tactile data for upper arm skin
    def read_skin_arm(self):
        """Read tactile data for upper arm skin.

        Parameters
        ----------

        Returns
        -------
        NDarray : vector[double]
            tactile data of the arm part of the skin, values: non-normalized: 0..255 ; normalized: 0..1.0
        """
        return np.array(deref(self._cpp_skin_reader).ReadSkinArm())

    # read tactile data for forearm skin
    def read_skin_forearm(self):
        """Read tactile data for forearm skin.

        Parameters
        ----------

        Returns
        -------
        NDarray : vector[double]
            tactile data of the forearm part of the skin, values: non-normalized: 0..255 ; normalized: 0..1.0
        """
        return np.array(deref(self._cpp_skin_reader).ReadSkinForearm())

    # read tactile data for hand skin
    def read_skin_hand(self):
        """Read tactile data for hand skin.

        Parameters
        ----------

        Returns
        -------
        NDarray : vector[double]
            tactile data of the hand part of the skin, values: non-normalized: 0..255 ; normalized: 0..1.0
        """
        return np.array(deref(self._cpp_skin_reader).ReadSkinHand())
