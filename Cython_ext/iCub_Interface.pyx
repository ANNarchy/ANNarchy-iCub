# distutils: language = c++
# cython: language_level = 3

"""
   Copyright (C) 2019-2021 Torsten Fietzek; Helge Ülo Dinkelbach

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
from libcpp.unordered_map cimport unordered_map as cmap

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

import xml.etree.ElementTree as ET
import os

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
    visual_input = None


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

    def clear(self):
        print("Clear iCub interface")
        for key, reader in self.parts_reader.items():
            reader.close()
        for key, writer in self.parts_writer.items():
            writer.close()
        for key, tactile in self.tactile_reader.items():
            tactile.close()

        self.parts_reader.clear()
        self.parts_writer.clear()
        self.tactile_reader.clear()

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

    # initialize interface for a robot configuration defined in a XML-file
    def init_robot_from_file(self, xml_file):
        name_dict = {}
        if os.path.isfile(xml_file):
            tree = ET.parse(xml_file)
            robot = tree.getroot()

            if not robot == None:
                # init joint reader
                name_JReader = {}
                for jread in robot.iter('JReader'):
                    no_error_jread = True
                    if(self.add_joint_reader(jread.attrib['name'])):
                        if(jread.find('part') == None):
                            print("Element part is missing")
                            no_error_jread = False
                        else:
                            part = jread.find('part').text
                        if(jread.find('sigma') == None):
                            print("Element sigma is missing")
                            no_error_jread = False
                        else:
                            sigma = float(jread.find('sigma').text)
                        if(jread.find('popsize') == None):
                            print("Element popsize is missing")
                            no_error_jread = False
                        else:
                            popsize = int(jread.find('popsize').text)
                        if(jread.find('ini_path') == None):
                            print("Element ini_path is missing")
                            no_error_jread = False
                        else:
                            ini_path = jread.find('ini_path').text
                        if(jread.find('deg_per_neuron') == None):
                            if(no_error_jread):
                                self.parts_reader[jread.attrib['name']].init(part, sigma, popsize, ini_path=ini_path)
                                name_JReader[part] = jread.attrib['name']
                            else:
                                print("Skipped Joint Reader '" + jread.attrib['name'] + "' init due to missing element")
                        else:
                            deg_per_neuron = float(jread.find('deg_per_neuron').text)
                            if(no_error_jread):
                                self.parts_reader[jread.attrib['name']].init(part, sigma, popsize, deg_per_neuron=deg_per_neuron, ini_path=ini_path)
                            else:
                                print("Skipped Joint Reader '" + jread.attrib['name'] + "' init due to missing element")

                # init joint writer
                name_JWriter = {}
                for jwrite in robot.iter('JWriter'):
                    if(self.add_joint_writer(jwrite.attrib['name'])):
                        no_error_jwrite = True
                        if(jwrite.find('part') == None):
                            print("Element part is missing")
                            no_error_jwrite = False
                        else:
                            part = jwrite.find('part').text
                        if(jwrite.find('popsize') == None):
                            print("Element popsize is missing")
                            no_error_jwrite = False
                        else:
                            popsize = int(jwrite.find('popsize').text)
                        if(jwrite.find('speed') == None):
                            print("Element speed is missing")
                            no_error_jwrite = False
                        else:
                            speed = float(jwrite.find('speed').text)
                        if(jwrite.find('ini_path') == None):
                            print("Element ini_path is missing")
                            no_error_jwrite = False
                        else:
                            ini_path = jwrite.find('ini_path').text
                        if(jwrite.find('deg_per_neuron') == None):
                            if(no_error_jwrite):
                                self.parts_writer[jwrite.attrib['name']].init(part, popsize, speed=speed,ini_path=ini_path)
                                name_JWriter[part] = jwrite.attrib['name']
                            else:
                                print("Skipped Joint Writer '" + jwrite.attrib['name'] + "' init due to missing element")
                        else:
                            deg_per_neuron = float(jwrite.find('deg_per_neuron').text)
                            if(no_error_jwrite):
                                self.parts_writer[jwrite.attrib['name']].init(part, popsize, speed=speed, deg_per_neuron=deg_per_neuron, ini_path=ini_path)
                            else:
                                print("Skipped Joint Writer '" + jwrite.attrib['name'] + "' init due to missing element")

                # init visual reader
                for vread in robot.iter('VisReader'):
                    if(self.add_visual_reader()):
                        no_error_vread = True
                        if(vread.find('eye') == None):
                            print("Element eye is missing")
                            no_error_vread = False
                        else:
                            eye = vread.find('eye').text
                        if(vread.find('fov_width') == None or vread.find('fov_height')):
                            print("Element fov_width or fov_height is missing")
                            no_error_vread = False
                        else:
                            fov_width = float(vread.find('fov_width').text)
                            fov_height = float(vread.find('fov_height').text)
                        if(vread.find('img_width') == None or vread.find('img_height')):
                            print("Element img_width or img_height is missing")
                            no_error_vread = False
                        else:
                            img_width = float(vread.find('img_width').text)
                            img_height = float(vread.find('img_height').text)
                        if(vread.find('max_buffer_size') == None):
                            print("Element max_buffer_size is missing")
                            no_error_vread = False
                        else:
                            max_buffer_size = int(vread.find('max_buffer_size').text)
                        if(vread.find('fast_filter') == None):
                            print("Element fast_filter is missing")
                            no_error_vread = False
                        else:
                            fast_filter = bool(vread.find('fast_filter').text)
                        if(vread.find('ini_path') == None):
                            print("Element ini_path is missing")
                            no_error_vread = False
                        else:
                            ini_path = vread.find('ini_path').text
                        if(no_error_vread):
                            self.visual_input.init(eye, fov_width, fov_height, img_width, img_height, max_buffer_size, fast_filter)
                        else:
                            print("Skipped Visual Reader init due to missing element")

                # init tactiel reader
                name_SReader = {}
                for sread in robot.iter('TacReader'):
                    if(self.add_skin_reader(sread.attrib['name'])):
                        no_error_sread = True
                        if(sread.find('arm') == None):
                            print("Element arm is missing")
                            no_error_sread = False
                        else:
                            arm = sread.find('arm').text
                        if(sread.find('normalize') == None):
                            print("Element norm is missing")
                            no_error_sread = False
                        else:
                            norm = bool(sread.find('normalize').text)
                        if(sread.find('ini_path') == None):
                            print("Element ini_path is missing")
                            no_error_sread = False
                        else:
                            ini_path = sread.find('ini_path').text
                        if(no_error_sread):
                            self.tactile_reader[sread.attrib['name']].init(arm, norm, ini_path)
                            name_SReader[part] = sread.attrib['name']
                        else:
                            print("Skipped Skin Reader '" + sread.attrib['name'] + "' init due to missing element")

                name_dict['JointReader'] = name_JReader
                name_dict['JointWriter'] = name_JWriter
                name_dict['SkinReader'] = name_SReader

                return True, name_dict
            else:
                print("Failed to read XML-file")
                return False, name_dict
        else:
            print("Not a valid XML-Filepath given!")
            return False, name_dict
