# distutils: language = c++
# cython: language_level = 3

"""
   Copyright (C) 2019-2020 Torsten Follak; Helge Ülo Dinkelbach

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
   along with this headers. If not, see [http://www.gnu.org/licenses/].
 """


from libcpp.string cimport string
from libcpp.vector cimport vector
from libcpp cimport bool as bool_t
from libcpp.memory cimport shared_ptr
from libcpp.map cimport map as cmap
# from libc.stdlib cimport malloc, free

cimport numpy as np
import numpy as np

from cython.operator cimport dereference as deref

from Joint_Reader cimport JointReader
from Joint_Reader cimport PyJointReader

from Joint_Writer cimport JointWriter
from Joint_Writer cimport PyJointWriter

from Skin_Reader cimport SkinReader
from Skin_Reader cimport PySkinReader

from Visual_Reader cimport VisualReader
from Visual_Reader cimport PyVisualReader

cdef extern from "Interface_iCub.hpp":

    cdef cppclass iCubANN:
        iCubANN() except +
        ### Manage instances of the reader/writer modules ###
        # add an instance of joint reader
        bool_t AddJointReader(string)
        # add an instance of joint writer
        bool_t AddJointWriter(string)
        # add an instance of skin reader
        bool_t AddSkinReader(string)
        # add the instance of visual reader
        bool_t AddVisualReader()

        # remove an instance of joint reader
        bool_t RemoveJointReader(string)
        # remove an instance of joint writer
        bool_t RemoveJointWriter(string)
        # remove an instance of skin reader
        bool_t RemoveSkinReader(string)
        # remove the instance of visual reader
        bool_t RemoveVisualReader()

        vector[vector[double]] WriteActionSyncOne(string, string, double, int, double)
        vector[vector[double]] WriteActionSyncMult(string, string, vector[double], vector[int], double)
        vector[vector[double]] WriteActionSyncAll(string, string, vector[double], double)

        cmap[string, shared_ptr[JointReader]] parts_reader
        cmap[string, shared_ptr[JointWriter]] parts_writer
        cmap[string, shared_ptr[SkinReader]] tactile_reader
        shared_ptr[VisualReader] visual_input

    # Instances:
    iCubANN my_interface # defined in Interface_iCub.cpp


cdef class iCubANN_wrapper:

    cdef dict __dict__

    parts_reader = {}
    parts_writer = {}
    tactile_reader = {}


    # part keys for the iCub, which are needed for joint reader/writer initialization
    PART_KEY_HEAD = "head"            # part key for iCub head
    PART_KEY_TORSO = "torso"          # part key for iCub torso
    PART_KEY_RIGHT_ARM = "right_arm"  # part key for iCub right arm
    PART_KEY_LEFT_ARM = "left_arm"    # part key for iCub left arm
    PART_KEY_RIGHT_LEG = "right_leg"  # part key for iCub right leg
    PART_KEY_LEFT_LEG = "left_leg"    # part key for iCub left leg

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
    # add an instance of joint reader
    def add_joint_reader(self, name):
        """
            Calls iCubANN::AddJointReader(std::string name)

            function:
                Add an instance of joint reader with a given name

            params: std::string name        -- name for the added joint reader in the map, can be freely selected
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')

        # call the interface
        if my_interface.AddJointReader(s):
            self.parts_reader[name] = PyJointReader.from_ptr(my_interface.parts_reader[s])
            return True
        else:
            return False

    # add an instance of joint writer
    def add_joint_writer(self, name):
        """
            Calls iCubANN::AddJointWriter(std::string name)

            function:
                Add an instance of joint writer with a given name

            params:
                std::string name        -- name for the added joint writer in the map, can be freely selected
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')

        # call the interface
        if my_interface.AddJointWriter(s):
            self.parts_writer[name] = PyJointWriter.from_ptr(my_interface.parts_writer[s])
            return True
        else:
            return False


    # add an instance of skin reader
    def add_skin_reader(self, name):
        """
            Calls iCubANN::AddSkinReader(std::string name)

            function:
                Add an instance of skin reader with a given name

            params:
                std::string name        -- name for the added skin reader in the map, can be freely selected
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')

        # call the interface
        if my_interface.AddSkinReader(s):
            self.tactile_reader[name] = PySkinReader.from_ptr(my_interface.tactile_reader[s])
            return True
        else:
            return False

    # add an instance of visual reader
    def add_visual_reader(self):
        """
            Calls iCubANN::AddVisualReader()

            function:
                Add an instance of visual reader
        """
        # call the interface
        if my_interface.AddVisualReader():
            self.visual_input = PyVisualReader.from_ptr(my_interface.visual_input)
            return True
        else:
            return False

    # remove an instance of joint reader
    def rm_joint_reader(self, name):
        """
            Calls iCubANN::RemoveJointReader(std::string name)

            function:
                Remove the instance of joint reader with the given name

            params: std::string name        -- name of the joint reader in the map, which should be remove
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')

        # call the interface
        if my_interface.RemoveJointReader(s):
            del self.parts_reader[name]
            return True
        else:
            return False

    # remove an instance of joint writer
    def rm_joint_writer(self, name):
        """
            Calls iCubANN::RemoveJointWriter(std::string name)

            function:
                Remove the instance of joint writer with the given name

            params:
                std::string name        -- name of the joint writer in the map, which should be remove
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')

        # call the interface
        if my_interface.RemoveJointWriter(s):
            del self.parts_writer[name]
            return True
        else:
            return False

    # remove an instance of skin reader
    def rm_skin_reader(self, name):
        """
            Calls iCubANN::RemoveSkinReader(std::string name)

            function:
                Remove the instance of skin reader with the given name

            params:
                std::string name        -- name of the skin reader in the map, which should be remove
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')

        # call the interface
        if my_interface.RemoveSkinReader(s):
            del self.tactile_reader[name]
            return True
        else:
            return False

    # remove the instance of visual reader
    def rm_visual_reader(self):
        """
            Calls iCubANN::AddVisualReader()

            function:
                Remove the visual reader instance
        """
        # call the interface
        if my_interface.RemoveVisualReader():
            del self.visual_input
            return True
        else:
            return False

    ### end Manage instances of the reader/writer module

    def write_action_sync_one(self, jwriter_name, jreader_name, angle, joint, dt):
        cdef string s1 = jwriter_name.encode('UTF-8')
        cdef string s2 = jreader_name.encode('UTF-8')
        return np.array(my_interface.WriteActionSyncOne(s1, s2, angle, joint, dt))

    def write_action_sync_mult(self, jwriter_name, jreader_name, angles, joints, dt):
        cdef string s1 = jwriter_name.encode('UTF-8')
        cdef string s2 = jreader_name.encode('UTF-8')
        return np.array(my_interface.WriteActionSyncMult(s1, s2, angles, joints, dt))

    def write_action_sync_all(self, jwriter_name, jreader_name, angles, dt):
        cdef string s1 = jwriter_name.encode('UTF-8')
        cdef string s2 = jreader_name.encode('UTF-8')
        return np.array(my_interface.WriteActionSyncAll(s1, s2, angles, dt))
