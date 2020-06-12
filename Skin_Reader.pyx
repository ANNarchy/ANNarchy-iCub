
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


    ### Access to skin reader member functions
    # init skin reader with given parameters
    def skinR_init(self, name, arm, norm=True):
        """
            Calls bool iCubANN::SkinRInit(std::string name, char arm, bool norm_data)

            function:
                Initialize skin reader with given parameters

            params:
                std::string name        -- name of the selected skin reader
                char arm                -- string representing the robot part, has to match iCub part naming
                bool norm_data          -- if true, the sensor data are returned normalized (iCub [0..255]; normalized [0..1])

            return:
                bool                    -- return True, if successful
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')
        cdef char a = arm.encode('UTF-8')[0]

        # call the interface
        return my_interface.SkinRInit(s, a, norm)

    # close and clean skin reader
    def skinR_close(self, name):
        """
            Calls void iCubANN::SkinRClose(std::string name)

            function:
                Close and clean skin reader

            params:
                std::string name        -- name of the selected skin reader
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')

        # call the interface
        my_interface.SkinRClose(s)

    # return tactile data for upper arm skin
    def skinR_get_tactile_arm(self, name):
        """
            Calls std::vector<std::vector<double>> iCubANN::SkinRGetTactileArm(std::string name)

            function:
                Return tactile data for the upper arm skin

            params:
                std::string name        -- name of the selected skin reader

            return:
                std::vector<std::vector<double>>     -- tactile data of the arm part of the skin, values: non-normalized: 0..255 ; normalized: 0..1.0
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')

        # call the interface
        return np.array(my_interface.SkinRGetTactileArm(s))

    # return tactile data for forearm skin
    def skinR_get_tactile_forearm(self, name):
        """
            Calls std::vector<std::vector<double>> iCubANN::SkinRGetTactileForearm(std::string name)

            function:
                Return tactile data for the forearm skin

            params:
                std::string name        -- name of the selected skin reader

            return:
                std::vector<std::vector<double>>     -- tactile data of the forearm part of the skin, values: non-normalized: 0..255 ; normalized: 0..1.0
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')

        # call the interface
        return np.array(my_interface.SkinRGetTactileForearm(s))

    # return tactile data for hand skin
    def skinR_get_tactile_hand(self, name):
        """
            Calls std::vector<std::vector<double>> iCubANN::SkinRGetTactileHand(std::string name)

            function:
                Return tactile data for the hand skin

            params:
                std::string name        -- name of the selected skin reader

            return:
                std::vector<std::vector<double>>     -- tactile data of the hand part of the skin, values: non-normalized: 0..255 ; normalized: 0..1.0
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')

        # call the interface
        return np.array(my_interface.SkinRGetTactileHand(s))

    # return the taxel positions given by the ini files
    def skinR_get_taxel_pos(self, name, skin_part):
        """
            Calls std::vector<std::vector<double>> iCubANN::SkinRGetTaxelPos(std::string name, std::string skin_part)

            function:
                Return the taxel positions given by the ini files from the iCub-simulator

            params:
                std::string name                    -- name of the selected skin reader
                std::string skin_part               -- skin part to load the data for ("arm", "forearm", "hand")

            return:
                std::vector<std::vector<double>>    -- Vector containing taxel positions -> reference frame depending on skin part
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')
        cdef string s1 = skin_part.encode('UTF-8')

        # call the interface
        return np.array(my_interface.SkinRGetTaxelPos(s, s1))

    # read sensor data
    def skinR_read_tactile(self, name):
        """
            Calls bool iCubANN::SkinRReadTactile(std::string name)

            function:
                Read sensor data for one step

            params:
                std::string name        -- name of the selected skin reader
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')

        # call the interface
        return my_interface.SkinRReadTactile(s)

    ### end access to skin reader member functions