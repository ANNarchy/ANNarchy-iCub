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


cdef class iCubANN_wrapper:


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

        self.joint_reader = {}
        self.joint_reader_parts = {}

        self.joint_writer = {}
        self.joint_writer_parts = {}

        self.skin_reader = {}
        self.skin_reader_parts = {}

    def __dealloc__(self):
        print("Close iCub Interface.")
        self.joint_reader.clear()
        self.joint_writer.clear()
        self.skin_reader.clear()
        self.visual_input = None


    def clear(self):
        print("Clear iCub interface")
        for key, reader in self.joint_reader.items():
            reader.close()
        for key, writer in self.joint_writer.items():
            writer.close()
        for key, tactile in self.skin_reader.items():
            tactile.close()

        self.joint_reader.clear()
        self.joint_writer.clear()
        self.skin_reader.clear()

        if not self.visual_input == None:
            self.visual_input.Close()
            self.visual_input = None

    ### Manage the reader/writer modules ###
    # register joint reader module
    def register_jreader(self, str name, PyJointReader module):
        if deref(module.cpp_joint_reader).getRegister():
            print("[Interface iCub] Joint Reader module is already registered!")
            return False
        else:
            if name in self.joint_reader:
                print("[Interface iCub] Joint Reader module name is already used!")
                return False
            else:
                if module.part in self.joint_reader_parts:
                    print("[Interface iCub] Joint Reader module part is already used!")
                    return False
                else:
                    self.joint_reader[name] = module
                    module.name = name
                    self.joint_reader_parts[module.part] = name
                    deref(module.cpp_joint_reader).setRegister(1)
                    return True

    # unregister joint reader  module
    def unregister_jreader(self, PyJointReader module):
        if deref(module.cpp_joint_reader).getRegister():
            deref(module.cpp_joint_reader).setRegister(0)
            self.joint_reader.pop(module.name, None)
            self.joint_reader_parts.pop(module.part, None)
            module.name = ""
            return True
        else:
            print("[Interface iCub] Joint Reader module is not yet registered!")
            return False

    # register joint writer  module
    def register_jwriter(self, str name, PyJointWriter module):
        if deref(module.cpp_joint_writer).getRegister():
            print("[Interface iCub] Joint Writer module is already registered!")
            return False
        else:
            if name in self.joint_writer:
                print("[Interface iCub] Joint Writer module name is already used!")
                return False
            else:
                if module.part in self.joint_writer_parts:
                    print("[Interface iCub] Joint Writer module part is already used!")
                    return False
                else:
                    self.joint_writer[name] = module
                    module.name = name
                    self.joint_writer_parts[module.part] = name
                    deref(module.cpp_joint_writer).setRegister(1)
                    return True

    # unregister joint writer module
    def unregister_jwriter(self, PyJointWriter module):
        if deref(module.cpp_joint_writer).getRegister():
            deref(module.cpp_joint_writer).setRegister(0)
            self.joint_writer.pop(module.name, None)
            self.joint_writer_parts.pop(module.part, None)
            module.name = ""
            return True
        else:
            print("[Interface iCub] Joint Writer module is not yet registered!")
            return False

    # register skin reader module
    def register_skin_reader(self, str name, PySkinReader module):
        if deref(module.cpp_skin_reader).getRegister():
            print("[Interface iCub] Skin Reader module is already registered!")
            return False
        else:
            if name in self.skin_reader:
                print("[Interface iCub] Skin Reader module name is already used!")
                return False
            else:
                if module.part in self.skin_reader_parts:
                    print("[Interface iCub] Skin Reader module part is already used!")
                    return False
                else:
                    self.skin_reader[name] = module
                    module.name = name
                    self.skin_reader_parts[module.part] = name
                    deref(module.cpp_skin_reader).setRegister(1)
                    return True

    # unregister skin reader module
    def unregister_skin_reader(self, PySkinReader module):
        if deref(module.cpp_skin_reader).getRegister():
            deref(module.cpp_skin_reader).setRegister(0)
            self.skin_reader.pop(module.name, None)
            self.skin_reader_parts.pop(module.part, None)
            module.name = ""
            return True
        else:
            print("[Interface iCub] Skin Reader module is not yet registered!")
            return False

    # register visual reader module
    def register_vis_reader(self, PyVisualReader module):
        if deref(module.cpp_visual_reader).getRegister():
            print("[Interface iCub] Visual Reader module is already registered!")
            return False
        else:
            if self.visual_input == None:
                self.visual_input = module
                deref(module.cpp_visual_reader).setRegister(1)
                return True
            else:
                print("[Interface iCub] Visual Reader module is already used!")
                return False

    # unregister skin reader module
    def unregister_vis_reader(self, PyVisualReader module):
        if deref(module.cpp_visual_reader).getRegister():
            deref(module.cpp_visual_reader).setRegister(0)
            self.visual_input = None
            return True
        else:
            print("[Interface iCub] Visual Reader module is not yet registered!")
            return False


    # initialize interface for a robot configuration defined in a XML-file
    # def init_robot_from_file(self, xml_file):
        # name_dict = {}
        # if os.path.isfile(xml_file):
        #     tree = ET.parse(xml_file)
        #     robot = tree.getroot()

        #     if not robot == None:
        #         # init joint reader
        #         name_JReader = {}
        #         for jread in robot.iter('JReader'):
        #             no_error_jread = True
        #             if(self.add_joint_reader(jread.attrib['name'])):
        #                 if(jread.find('part') == None):
        #                     print("Element part is missing")
        #                     no_error_jread = False
        #                 else:
        #                     part = jread.find('part').text
        #                 if(jread.find('sigma') == None):
        #                     print("Element sigma is missing")
        #                     no_error_jread = False
        #                 else:
        #                     sigma = float(jread.find('sigma').text)
        #                 if(jread.find('popsize') == None):
        #                     print("Element popsize is missing")
        #                     no_error_jread = False
        #                 else:
        #                     popsize = int(jread.find('popsize').text)
        #                 if(jread.find('ini_path') == None):
        #                     print("Element ini_path is missing")
        #                     no_error_jread = False
        #                 else:
        #                     ini_path = jread.find('ini_path').text
        #                 if(jread.find('deg_per_neuron') == None):
        #                     if(no_error_jread):
        #                         self.joint_reader[jread.attrib['name']].init(part, sigma, popsize, ini_path=ini_path)
        #                         name_JReader[part] = jread.attrib['name']
        #                     else:
        #                         print("Skipped Joint Reader '" + jread.attrib['name'] + "' init due to missing element")
        #                 else:
        #                     deg_per_neuron = float(jread.find('deg_per_neuron').text)
        #                     if(no_error_jread):
        #                         self.joint_reader[jread.attrib['name']].init(part, sigma, popsize, deg_per_neuron=deg_per_neuron, ini_path=ini_path)
        #                     else:
        #                         print("Skipped Joint Reader '" + jread.attrib['name'] + "' init due to missing element")

        #         # init joint writer
        #         name_JWriter = {}
        #         for jwrite in robot.iter('JWriter'):
        #             if(self.add_joint_writer(jwrite.attrib['name'])):
        #                 no_error_jwrite = True
        #                 if(jwrite.find('part') == None):
        #                     print("Element part is missing")
        #                     no_error_jwrite = False
        #                 else:
        #                     part = jwrite.find('part').text
        #                 if(jwrite.find('popsize') == None):
        #                     print("Element popsize is missing")
        #                     no_error_jwrite = False
        #                 else:
        #                     popsize = int(jwrite.find('popsize').text)
        #                 if(jwrite.find('speed') == None):
        #                     print("Element speed is missing")
        #                     no_error_jwrite = False
        #                 else:
        #                     speed = float(jwrite.find('speed').text)
        #                 if(jwrite.find('ini_path') == None):
        #                     print("Element ini_path is missing")
        #                     no_error_jwrite = False
        #                 else:
        #                     ini_path = jwrite.find('ini_path').text
        #                 if(jwrite.find('deg_per_neuron') == None):
        #                     if(no_error_jwrite):
        #                         self.joint_writer[jwrite.attrib['name']].init(part, popsize, speed=speed,ini_path=ini_path)
        #                         name_JWriter[part] = jwrite.attrib['name']
        #                     else:
        #                         print("Skipped Joint Writer '" + jwrite.attrib['name'] + "' init due to missing element")
        #                 else:
        #                     deg_per_neuron = float(jwrite.find('deg_per_neuron').text)
        #                     if(no_error_jwrite):
        #                         self.joint_writer[jwrite.attrib['name']].init(part, popsize, speed=speed, deg_per_neuron=deg_per_neuron, ini_path=ini_path)
        #                     else:
        #                         print("Skipped Joint Writer '" + jwrite.attrib['name'] + "' init due to missing element")

        #         # init visual reader
        #         for vread in robot.iter('VisReader'):
        #             if(self.add_visual_reader()):
        #                 no_error_vread = True
        #                 if(vread.find('eye') == None):
        #                     print("Element eye is missing")
        #                     no_error_vread = False
        #                 else:
        #                     eye = vread.find('eye').text
        #                 if(vread.find('fov_width') == None or vread.find('fov_height')):
        #                     print("Element fov_width or fov_height is missing")
        #                     no_error_vread = False
        #                 else:
        #                     fov_width = float(vread.find('fov_width').text)
        #                     fov_height = float(vread.find('fov_height').text)
        #                 if(vread.find('img_width') == None or vread.find('img_height')):
        #                     print("Element img_width or img_height is missing")
        #                     no_error_vread = False
        #                 else:
        #                     img_width = float(vread.find('img_width').text)
        #                     img_height = float(vread.find('img_height').text)
        #                 if(vread.find('max_buffer_size') == None):
        #                     print("Element max_buffer_size is missing")
        #                     no_error_vread = False
        #                 else:
        #                     max_buffer_size = int(vread.find('max_buffer_size').text)
        #                 if(vread.find('fast_filter') == None):
        #                     print("Element fast_filter is missing")
        #                     no_error_vread = False
        #                 else:
        #                     fast_filter = bool(vread.find('fast_filter').text)
        #                 if(vread.find('ini_path') == None):
        #                     print("Element ini_path is missing")
        #                     no_error_vread = False
        #                 else:
        #                     ini_path = vread.find('ini_path').text
        #                 if(no_error_vread):
        #                     self.visual_input.init(eye, fov_width, fov_height, img_width, img_height, max_buffer_size, fast_filter)
        #                 else:
        #                     print("Skipped Visual Reader init due to missing element")

        #         # init tactiel reader
        #         name_SReader = {}
        #         for sread in robot.iter('TacReader'):
        #             if(self.add_skin_reader(sread.attrib['name'])):
        #                 no_error_sread = True
        #                 if(sread.find('arm') == None):
        #                     print("Element arm is missing")
        #                     no_error_sread = False
        #                 else:
        #                     arm = sread.find('arm').text
        #                 if(sread.find('normalize') == None):
        #                     print("Element norm is missing")
        #                     no_error_sread = False
        #                 else:
        #                     norm = bool(sread.find('normalize').text)
        #                 if(sread.find('ini_path') == None):
        #                     print("Element ini_path is missing")
        #                     no_error_sread = False
        #                 else:
        #                     ini_path = sread.find('ini_path').text
        #                 if(no_error_sread):
        #                     self.tactile_reader[sread.attrib['name']].init(arm, norm, ini_path)
        #                     name_SReader[part] = sread.attrib['name']
        #                 else:
        #                     print("Skipped Skin Reader '" + sread.attrib['name'] + "' init due to missing element")

        #         name_dict['JointWriter'] = name_JWriter
        #         name_dict['SkinReader'] = name_SReader

        #         return True, name_dict
        #     else:
        #         print("Failed to read XML-file")
        #         return False, name_dict
        # else:
        #     print("Not a valid XML-Filepath given!")
        #     return False, name_dict
