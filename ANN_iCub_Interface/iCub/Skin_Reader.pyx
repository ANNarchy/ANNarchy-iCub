
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
from libcpp.vector cimport vector
from libcpp.memory cimport shared_ptr, make_shared
from cython.operator cimport dereference as deref

from .Skin_Reader cimport SkinReader
from .iCub_Interface cimport ANNiCub_wrapper

import numpy as np

cdef class PySkinReader:

    # init method
    def __cinit__(self):
        print("Initialize iCub Interface: Skin Reader.")
        self.cpp_skin_reader = make_shared[SkinReader]()

    # close method
    def __dealloc__(self):
        print("Close iCub Interface: Skin Reader.")
        self.cpp_skin_reader.reset()


    ### Access to skin reader member functions
    # init skin reader with given parameters
    def init(self, ANNiCub_wrapper iCub, str name, str arm, norm=True, str ini_path="../data/"):
        """
            Calls bool SkinReader::Init(char arm, bool norm_data)

            function:
                Initialize skin reader with given parameters

            params:
                ANNiCub_wrapper iCub    -- main interface wrapper
                str name                -- name for the skin reader module
                char arm                -- character to choose the arm side (r/R for right; l/L for left)
                bool norm_data          -- if true, the sensor data are returned normalized (iCub [0..255]; normalized [0..1])
                ini_path                -- Path to the "interface_param.ini"-file

            return:
                bool                    -- return True, if successful
        """

        self.part = arm
        # preregister module for some prechecks e.g. arm already in use
        if iCub.register_skin_reader(name, self):
            # call the interface
            retval = deref(self.cpp_skin_reader).Init(name.encode('UTF-8'), arm.encode('UTF-8')[0], norm.__int__(), ini_path.encode('UTF-8'))
            if not retval:
                iCub.unregister_skin_reader(self)
            return retval
        else:
            return False

    # Initialize the skin reader with given parameters for use with gRPC
    def init_grpc(self, ANNiCub_wrapper iCub, str name, str arm, norm=True, str ini_path="../data/", str ip_address="0.0.0.0", unsigned int port=50015):
        """
            Calls bool SkinReader::Init(char arm, bool norm_data)

            function:
                Initialize skin reader with given parameters

            params:
                ANNiCub_wrapper iCub    -- main interface wrapper
                str name                -- name for the skin reader module
                char arm                -- character to choose the arm side (r/R for right; l/L for left)
                bool norm_data          -- if true, the sensor data are returned normalized (iCub [0..255]; normalized [0..1])
                ini_path                -- Path to the "interface_param.ini"-file
                string ip_address       -- gRPC server ip address
                unsigned int port       -- gRPC server port

            return:
                bool                    -- return True, if successful
        """
        # we need to transform py-string to c++ compatible string
        self.part = arm
        # preregister module for some prechecks e.g. arm already in use
        if iCub.register_skin_reader(name, self):
            # call the interface
            retval = deref(self.cpp_skin_reader).InitGRPC(name.encode('UTF-8'), arm.encode('UTF-8')[0], norm.__int__(), ini_path.encode('UTF-8'), ip_address.encode('UTF-8'), port)
            if not retval:
                iCub.unregister_skin_reader(self)
            return retval
        else:
            return False


    # close and clean skin reader
    def close(self, ANNiCub_wrapper iCub):
        """
            Calls void SkinReader::Close()

            function:
                Close and clean skin reader

            params:
                ANNiCub_wrapper iCub    -- main interface wrapper
        """

        iCub.unregister_skin_reader(self)

        # call the interface
        deref(self.cpp_skin_reader).Close()

    # return tactile data for upper arm skin
    def get_tactile_arm(self):
        """
            Calls std::vector<std::vector<double>> SkinReader::GetTactileArm()

            function:
                Return tactile data for the upper arm skin

            return:
                std::vector<std::vector<double>>     -- tactile data of the arm part of the skin, values: non-normalized: 0..255 ; normalized: 0..1.0
        """

        # call the interface
        return np.array(deref(self.cpp_skin_reader).GetTactileArm())

    # return size of tactile data for upper arm skin
    def get_tactile_arm_size(self):
        """
            Calls unsigned int SkinReader::GetTactileArmSize()

            function:
                Return size of tactile data for the arm skin

            return:
                unsigned int     -- size of sensor data vector -> arm section
        """

        # call the interface
        return deref(self.cpp_skin_reader).GetTactileArmSize()

    # return tactile data for forearm skin
    def get_tactile_forearm(self):
        """
            Calls std::vector<std::vector<double>> SkinReader::GetTactileForearm()

            function:
                Return tactile data for the forearm skin

            return:
                std::vector<std::vector<double>>     -- tactile data of the forearm part of the skin, values: non-normalized: 0..255 ; normalized: 0..1.0
        """
        # call the interface
        return np.array(deref(self.cpp_skin_reader).GetTactileForearm())

    # return size of tactile data for forearm skin
    def get_tactile_forearm_size(self):
        """
            Calls unsigned int SkinReader::GetTactileForearmSize()

            function:
                Return size of tactile data for the forearm skin

            return:
                unsigned int     -- size of sensor data vector -> forearm section
        """
        # call the interface
        return deref(self.cpp_skin_reader).GetTactileForearmSize()

    # return tactile data for hand skin
    def get_tactile_hand(self):
        """
            Calls std::vector<std::vector<double>> SkinReader::GetTactileHand()

            function:
                Return tactile data for the hand skin

            return:
                std::vector<std::vector<double>>     -- tactile data of the hand part of the skin, values: non-normalized: 0..255 ; normalized: 0..1.0
        """

        # call the interface
        return np.array(deref(self.cpp_skin_reader).GetTactileHand())

    # return size of tactile data for hand skin
    def get_tactile_hand_size(self):
        """
            Calls unsigned int SkinReader::GetTactileHandSize()

            function:
                Return size of tactile data for the hand skin

            return:
                unsigned int     -- size of sensor data vector -> hand section
        """

        # call the interface
        return deref(self.cpp_skin_reader).GetTactileHandSize()

    # return the taxel positions given by the ini files
    def get_taxel_pos(self, str skin_part):
        """
            Calls std::vector<std::vector<double>> SkinReader::GetTaxelPos(std::string skin_part)

            function:
                Return the taxel positions given by the ini files from the iCub-simulator

            params:
                std::string skin_part               -- skin part to load the data for ("arm", "forearm", "hand")

            return:
                std::vector<std::vector<double>>    -- Vector containing taxel positions -> reference frame depending on skin part
        """
        # we need to transform py-string to c++ compatible string
        cdef string s1 = skin_part.encode('UTF-8')

        # call the interface
        return np.array(deref(self.cpp_skin_reader).GetTaxelPos(s1))

    # read sensor data
    def read_tactile(self):
        """
            Calls bool SkinReader::ReadTactile()

            function:
                Read sensor data for one step

        """

        # call the interface
        return deref(self.cpp_skin_reader).ReadTactile()



    ### end access to skin reader member functions