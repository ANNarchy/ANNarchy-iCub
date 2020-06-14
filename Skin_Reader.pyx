
# distutils: language = c++
# cython: language_level = 3

"""
   Copyright (C) 2020 Torsten Follak; Helge Ülo Dinkelbach

   Skin_Reader.pyx is part of the iCub ANNarchy interface

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
from cython.operator cimport dereference as deref

from Skin_Reader cimport SkinReader

import numpy as np

cdef class PySkinReader:

    def __cinit__(self):
        print("Initialize iCub Interface: Skin Reader.")

    @staticmethod
    cdef PySkinReader from_ptr(shared_ptr[SkinReader] _ptr):
        # Call to __new__ bypasses __init__ constructor
        cdef PySkinReader wrapper = PySkinReader.__new__(PySkinReader)
        wrapper.cpp_skin_reader = _ptr
        return wrapper

    ### Access to skin reader member functions
    # init skin reader with given parameters
    def init(self, arm, norm=True):
        """
            Calls bool SkinReader::Init(char arm, bool norm_data)

            function:
                Initialize skin reader with given parameters

            params:
                char arm        -- string representing the robot part, has to match iCub part naming
                bool norm_data  -- if true, the sensor data are returned normalized (iCub [0..255]; normalized [0..1])

            return:
                bool            -- return True, if successful
        """
        # we need to transform py-string to c++ compatible string
        cdef char a = arm.encode('UTF-8')[0]

        # call the interface
        return deref(self.cpp_skin_reader).Init(a, norm)

    # close and clean skin reader
    def close(self):
        """
            Calls void SkinReader::Close()

            function:
                Close and clean skin reader

        """

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

    # return the taxel positions given by the ini files
    def get_taxel_pos(self, skin_part):
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