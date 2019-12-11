# distutils: language = c++
# cython: language_level = 3

"""
   Copyright (C) 2019 Torsten Follak; Helge Ülo Dinkelbach

   iCubCPP.pyx is part of the iCub ANNarchy interface

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
from libc.stdlib cimport malloc, free
import sys
import cython
import numpy as np



cdef extern from "Interface_iCub.hpp":

    cdef struct iCubANN:

        ### Manage instances of the reader/writer modules ###
        # add an instance of joint reader
        void AddJointReader(string)
        # add an instance of joint writer
        void AddJointWriter(string)
        # add an instance of skin reader
        void AddSkinReader(string)
        # add the instance of visual reader
        void AddVisualReader()

        # remove the instance of visual reader
        void RemoveVisualReader()


        ### Access to joint reader member functions ###
        # initialize the joint reader with given parameters
        bint JointRInit(string, string, double, int, double)
        # close joint reader with cleanup
        void JointRClose(string)
        # get number of controlled joints
        int JointRGetJointCount(string)
        # get the resolution in degree of the populations encoding the joint angles
        vector[double] JointRGetJointsDegRes(string)
        # get the size of the populations encoding the joint angles
        vector[int] JointRGetNeuronsPerJoint(string)
        # read one joint and return joint angle directly as double value
        double JointRReadDouble(string , int)
        # read all joints and return the joint angles encoded in vectors
        vector[vector[double]] JointRReadPopAll(string)
        # read one joint and return the joint angle encoded in a vector
        vector[double] JointRReadPopOne(string, int)


        ### Access to joint writer member functions ###
        # initialize the joint writer with given parameters
        bint JointWInit(string, string, int, double, double)
        # close joint writer with cleanup
        void JointWClose(string)
        # get number of controlled joints
        int JointWGetJointCount(string)
        # get the resolution in degree of the populations encoding the joint angles
        vector[double] JointWGetJointsDegRes(string)
        # get the size of the populations encoding the joint angles
        vector[int] JointWGetNeuronsPerJoint(string)
        # set joint velocity
        bint JointWSetJointVelocity(string, double, int)
        # write all joints with double values
        bint JointWWriteDoubleAll(string, vector[double], bint)
        # write one joint with double value
        bint JointWWriteDouble(string, double, int, bint)
        # write all joints with joint angles encoded in populations
        bint JointWWritePopAll(string, vector[vector[double]], bint)
        # write one joint with the joint angle encoded in a population
        bint JointWWritePopOne(string, vector[double], int, bint)


        ### Access to skin reader member functions ###
        # init skin reader with given parameters
        bint SkinRInit(string, char, bint)
        # close and clean skin reader
        void SkinRClose(string)
        # return tactile data for upper arm skin
        vector[vector[double]] SkinRGetTactileArm(string)
        # return tactile data for forearm skin
        vector[vector[double]] SkinRGetTactileForearm(string)
        # return tactile data for hand skin
        vector[vector[double]] SkinRGetTactileHand(string)
        # return the taxel positions given by the ini files
        vector[vector[double]] SkinRGetTaxelPos(string, string)
        # read sensor data
        bint SkinRReadTactile(string)


        ### Access to visual reader member functions ###
        # init Visual reader with given parameters for image resolution, field of view and eye selection
        bint VisualRInit(char, double, double, int, int, bint)
        # read image vector from the image buffer and remove it from the buffer
        vector[double] VisualRReadFromBuf()
        # start reading images from the iCub with YARP-RFModule
        bint VisualRStart(int, char**)
        # stop reading images from the iCub, by terminating the RFModule
        void VisualRStop()

    # Instances:
    iCubANN my_interface # defined in Interface_iCub.cpp

cdef class iCubANN_wrapper:

    # part keys for the iCub, which are needed for joint reader/writer initialization
    PART_KEY_HEAD = "head"            # part key for iCub head
    PART_KEY_TORSO = "torso"          # part key for iCub torso
    PART_KEY_RIGHT_ARM = "right_arm"  # part key for iCub right arm
    PART_KEY_LEFT_ARM = "left_arm"    # part key for iCub left arm
    PART_KEY_RIGHT_LEG = "right_leg"  # part key for iCub right leg
    PART_KEY_LEFT_LEG = "left_leg"    # part key for iCub left leg

    # TODO: comments which movements
    # numbers for head joints
    JOINT_NUM_NECK_PITCH = 0
    JOINT_NUM_NECK_ROLL = 1
    JOINT_NUM_NECK_YAW = 2
    JOINT_NUM_EYES_TILT = 3
    JOINT_NUM_EYES_VERSION  = 4
    JOINT_NUM_EYES_VERGENCE  = 5

    # numbers for arm joints (left/right identical)
    JOINT_NUM_SHOULDER_PITCH = 0
    JOINT_NUM_SHOULDER_ROLL = 1
    JOINT_NUM_SHOULDER_YAW = 2
    JOINT_NUM_ELBOW = 3
    JOINT_NUM_WRIST_PROSUP = 4
    JOINT_NUM_WRIST_PITCH = 5
    JOINT_NUM_WRIST_YAW = 6
    JOINT_NUM_HAND_FINGER = 7
    JOINT_NUM_THUMB_OPPOSE = 8
    JOINT_NUM_THUMB_PROXIMAL = 9
    JOINT_NUM_THUMB_DISTAL = 10
    JOINT_NUM_INDEX_PROXIMAL = 11
    JOINT_NUM_INDEX_DISTAL = 12
    JOINT_NUM_MIDDLE_PROXIMAL = 13
    JOINT_NUM_MIDDLE_DISTAL = 14
    JOINT_NUM_PINKY = 15

    # numbers for leg joints (left/right identical)
    JOINT_NUM_HIP_PITCH = 0
    JOINT_NUM_HIP_ROLL = 1
    JOINT_NUM_HIP_YAW = 2
    JOINT_NUM_KNEE = 3
    JOINT_NUM_ANKLE_PITCH = 4
    JOINT_NUM_ANKLE_ROLL = 5

    # numbers for torso joints
    JOINT_NUM_TORSO_YAW = 0
    JOINT_NUM_TORSO_ROLL = 1
    JOINT_NUM_TORSO_PITCH = 2

    def __cinit__(self):
        print("Initialize iCub Interface.")
        #my_interface.init() - we need a special init?

    ### Manage instances of the reader/writer modules ###
    def add_joint_reader(self, name):
        """
            Calls iCubANN::AddJointReader(std::string name)

            params: std::string name        -- name for the added joint reader in the map, can be freely selected
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')

        # call the interface
        my_interface.AddJointReader(s)

    def add_joint_writer(self, name):
        """
            Calls iCubANN::AddJointWriter(std::string name)

            params:
                std::string name        -- name for the added joint writer in the map, can be freely selected
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')

        # call the interface
        my_interface.AddJointWriter(s)

    def add_skin_reader(self, name):
        """
            Calls iCubANN::AddSkinReader(std::string name)

            params:
                std::string name        -- name for the added skin reader in the map, can be freely selected
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')

        # call the interface
        my_interface.AddSkinReader(s)

    def add_visual_reader(self):
        """
            Calls iCubANN::AddVisualReader()

            params:
                std::string name        -- name for the added visual reader in the map, can be freely selected
        """
        # call the interface
        my_interface.AddVisualReader()


    def rm_visual_reader(self):
        # call the interface
        my_interface.RemoveVisualReader()
    
    ### end Manage instances of the reader/writer module


    ### Access to joint reader member functions
    # Initialize the joint reader with given parameters
    def jointR_init(self, name, part, sigma, n_pop, degr_per_neuron=0.0):
        """
            Calls bool iCubANN::JointRInit(std::string name, std::string part, double sigma, int pop_n, double deg_per_neuron)

            function:
                Initialize the joint reader with given parameters

            params:
                std::string name        -- name of the selected joint reader
                std::string part        -- string representing the robot part, has to match iCub part naming
                                            {left_(arm/leg), right_(arm/leg), head, torso}
                sigma                   -- sigma for the joints angles populations coding
                int pop_size            -- number of neurons per population, encoding each one joint angle;
                                            only works if parameter "deg_per_neuron" is not set
                double deg_per_neuron   -- degree per neuron in the populations, encoding the joints angles;
                                            if set: population size depends on joint working range

            return:
                bool                    -- return True, if successful
        """
        # we need to transform py-string to c++ compatible string
        cdef string c_name = name.encode('UTF-8')
        cdef string key = part.encode('UTF-8')

        return my_interface.JointRInit(c_name, key, sigma, n_pop, degr_per_neuron)

    # close joint reader with cleanup
    def jointR_close(self, name):
        """
            Calls iCubANN::JointRClose(std::string name)

            function:
                Close joint reader with cleanup

            params:
                std::string name    -- name of the selected joint reader
       """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')

        # call the interface
        my_interface.JointRClose(s)

    # get the number of controlled joints
    def jointR_get_joint_count(self, name):
        """
            Calls std::vector<double> iCubANN::JointRGetJointCount(std::string name)

            function:
                Return the number of controlled joints

            params:
                std::string name        -- name of the selected joint reader

            return:
                int                     -- return number of joints, being controlled by the reader
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')

        # call the interface
        return my_interface.JointRGetJointCount(s)
    
    # get the resolution in degree of the populations encoding the joint angles
    def jointR_get_joints_deg_res(self, name):
        """
            Calls std::vector<double> iCubANN::JointRGetJointsDegRes(std::string name)

            function:
                Return the resolution in degree of the populations encoding the joint angles

            params:
                std::string name        -- name of the selected joint reader

            return:
                std::vector<double>     -- return vector, containing the resolution for every joints population codimg in degree
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')

        # call the interface
        return np.array(my_interface.JointRGetJointsDegRes(s))

    # get the size of the populations encoding the joint angles
    def jointR_get_neurons_per_joint(self, name):
        """
            Calls std::vector<int> iCubANN:: JointRGetNeuronsPerJoint(std::string name)

            function:
                Return the size of the populations encoding the joint angles

            params:
                std::string name        -- name of the selected joint reader

            return:
                std::vector<int>        -- return vector, containing the population size for every joint
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')

        # call the interface
        return np.array(my_interface.JointRGetNeuronsPerJoint(s))

    # read one joint and return joint angle directly as double value
    def jointR_read_double(self, name, joint):
        """
            Calls double iCubANN::JointRReadDouble(std::string name, int joint)

            function:
                Read one joint and return joint angle directly as double value

            params:
                std::string name    -- name of the selected joint reader
                int joint           -- joint number of the robot part

            return:
                double              -- joint angle read from the robot
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')

        # call the interface
        return my_interface.JointRReadDouble(s, joint)

    # read all joints and return the joint angles encoded in vectors (population coding)
    def jointR_read_pop_all(self, name):
        """
            Calls std::vector<std::vector<double>> iCubANN::JointRReadPopAll(std::string name)

            function:
                Read all joints and return the joint angles encoded in vectors (population coding)

            params:
                std::string name        -- name of the selected joint reader

            return:
                std::vector<std::vector<double>>    -- population vectors encoding every joint angle from associated robot part

        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')

        # call the interface
        return my_interface.JointRReadPopAll(s)


    # read one joint and return the joint angle encoded in a vector (population coding)
    def jointR_read_pop_one(self, name, joint):
        """
            Calls std::vector<double> iCubANN::JointRReadPopOne(std::string name, int joint)

            function:
                Read one joint and return the joint angle encoded in a vector (population coding)

            params:
                std::string name        -- name of the selected joint reader
                int joint               -- joint number of the robot part

            return:
                std::vector<double>     -- population vector encoding the joint angle
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')

        # call the interface
        return my_interface.JointRReadPopOne(s, joint)

    ### end access to joint reader member functions


    ### Access to joint writer member functions
    # initialize the joint writer with given parameters
    def jointW_init(self, name, part, n_pop, degr_per_neuron=0.0, speed=10.0):
        """
            Calls bool iCubANN::JointWInit(std::string name, std::string part, int pop_size, double deg_per_neuron, double speed)

            function:
                Initialize the joint writer with given parameters

            params:
                std::string name        -- name of the selected joint writer
                std::string part        -- string representing the robot part, has to match iCub part naming
                                            {left_(arm/leg), right_(arm/leg), head, torso}
                int pop_size            -- number of neurons per population, encoding each one joint angle;
                                            only works if parameter "deg_per_neuron" is not set
                double deg_per_neuron   -- degree per neuron in the populations, encoding the joints angles;
                                            if set: population size depends on joint working range
                double speed            -- velocity for the joint movements

            return:
                bool                    -- return True, if successful
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')
        cdef string key = part.encode('UTF-8')

        # call the interface
        return my_interface.JointWInit(s, key, n_pop, degr_per_neuron, speed)

    # close joint reader with cleanup
    def jointW_close(self, name):
        """
            Calls iCubANN::JointWClose(std::string name)

            function:
                Close joint reader with cleanup

            params:
                std::string name        -- name of the selected joint writer
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')

        # call the interface
        my_interface.JointWClose(s)

    # return number of controlled joints
    def jointW_get_joint_count(self, name):
        """
            Calls std::vector<double> iCubANN::JointWGetJointCount(std::string name)

            function:
                Return number of controlled joints

            params:
                std::string name        -- name of the selected joint writer

            return:
                int                     -- return number of joints, being controlled by the writer
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')

        # call the interface
        return my_interface.JointWGetJointCount(s)

    # get the resolution in degree of the populations encoding the joint angles
    def jointW_get_joints_deg_res(self, name):
        """
            Calls std::vector<double> iCubANN::JointWGetJointsDegRes(std::string name)

            function:
                Return the resolution in degree of the populations encoding the joint angles

            params:
                std::string name        -- name of the selected joint writer

            return:
                std::vector<double>     -- return vector, containing the resolution for every joints population codimg in degree
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')

        # call the interface
        return np.array(my_interface.JointWGetJointsDegRes(s))

    # get the size of the populations encoding the joint angles
    def jointW_get_neurons_per_joint(self, name):
        """
            Calls std::vector<int> iCubANN::JointWGetNeuronsPerJoint(std::string name)

            function:
                Return the size of the populations encoding the joint angles

            params:
                std::string name        -- name of the selected joint writer

            return:
                std::vector<int>        -- return vector, containing the population size for every joint
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')

        # call the interface
        return np.array(my_interface.JointWGetNeuronsPerJoint(s))

    # set joint velocity
    def jointW_set_joint_velocity(self, name, speed, joint=(-1)):
        """
            Calls bool iCubANN::JointWSetJointVelocity(std::string name, double speed, int joint)

            function:
                Set iCub joint velocity

            params:
                std::string name    -- name of the selected joint writer
                double speed        -- velocity value to be set
                int joint           -- joint number of the robot part, default -1 for all joints

            return:
                bool                -- return True, if successful
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')
        # call the interface
        return my_interface.JointWSetJointVelocity(s, speed, joint)

    # write all joints with double values
    def jointW_write_double_all(self, name, position, blocking=True):
        """
            Calls bool iCubANN::JointWWriteDoubleAll(std::string name, std::vector<double> position, bool blocking)

            function:
                Write all joints with double values

            params:
                std::string name                -- name of the selected joint writer
                std::vector<double> position    -- joint angles to write to the robot joints
                bool blocking                   -- if True, function waits for end of motion; default True

            return:
                bool                            -- return True, if successful
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')

        cdef bint block = blocking.__int__()

        # call the interface
        return my_interface.JointWWriteDoubleAll(s, position, block)

    # write one joint with double value
    def jointW_write_double(self, name, position, joint, blocking=True):
        """
            Calls bool iCubANN::JointWWriteDouble(std::string name, double position, int joint, bool blocking)

            function:
                Write one joint with double value

            params:
                std::string name    -- name of the selected joint writer
                double position     -- joint angle to write to the robot joint
                int joint           -- joint number of the robot part
                bool blocking       -- if True, function waits for end of motion; default True

            return:
                bool                -- return True, if successful
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')

        cdef bint block = blocking.__int__()

        # call the interface
        return my_interface.JointWWriteDouble(s, position, joint, block)

    # write all joints with joint angles encoded in populations vectors
    def jointW_write_pop_all(self, name, position_pops, blocking=True):
        """
            Calls bool iCubANN::JointWWritePopAll(std::string name, std::vector<std::vector<double>> position_pops, bool blocking)

            function:
                Write all joints with joint angles encoded in populations vectors

            params:
                std::string name                    -- name of the selected joint writer
                std::vector<std::vector<double>>    -- populations encoding every joint angle for writing them to the associated robot part
                bool blocking                       -- if True, function waits for end of motion; default True

            return:
                bool                                -- return True, if successful
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')

        cdef bint block = blocking.__int__()

        # call the interface
        return my_interface.JointWWritePopAll(s, position_pops, block)


    # write one joint with the joint angle encoded in a population vector
    def jointW_write_pop_one(self, name, position_pop, joint, blocking=True):
        """
            Calls bool iCubANN::JointWWritePopOne(std::string name, std::vector<double> position_pop, int joint, bool blocking)

            function:
                Write one joint with the joint angle encoded in a population vector

            params:
                std::string name        -- name of the selected joint writer
                std::vector<double>     -- population encoded joint angle for writing to the robot joint
                int joint               -- joint number of the robot part
                bool blocking           -- if True, function waits for end of motion; default True

            return:
                bool                    -- return True, if successful
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')

        cdef bint block = blocking.__int__()

        # call the interface
        return my_interface.JointWWritePopOne(s, position_pop, joint, block)

    ### end access to joint writer member functions


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


    ### Access to visual reader member functions
    # init Visual reader with given parameters for image resolution, field of view and eye selection
    def visualR_init(self, eye, fov_width=60, fov_height=48, img_width=320, img_height=240, fast_filter=True):
        """
            Calls bool iCubANN::VisualRInit(char eye, double fov_width, double fov_height, int img_width, int img_height)

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
        return my_interface.VisualRInit(e, fov_width, fov_height, img_width, img_height, fast_filter)

    # return image vector from the image buffer and remove it from the buffer
    def visualR_read_fromBuf(self):
        """
            Calls std::vector<double> iCubANN::VisualRReadFromBuf()

            function:
                Return image vector from the image buffer and remove it from the buffer

            return:
                std::vector<double>     -- image (1D-vector) from the image buffer
        """

        # call the interface
        return np.array(my_interface.VisualRReadFromBuf())

    # start reading images from the iCub with a YARP-RFModule
    def visualR_start(self):
        """
            Calls void iCubANN::VisualRStart(int argc, char *argv[])

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
        start = my_interface.VisualRStart(argc, c_argv)
        # Let him go
        free(c_argv)
        return start

    # stop reading images from the iCub, by terminating the RFModule
    def visualR_stop(self):
        """
            Calls void iCubANN::VisualRStop()

            function:
                Stop reading images from the iCub, by terminating the RFModule
        """

        # call the interface
        my_interface.VisualRStop()

    ### end access to visual reader member functions