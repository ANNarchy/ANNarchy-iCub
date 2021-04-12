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

from .Joint_Reader cimport JointReader
from .Joint_Reader cimport PyJointReader

from .Joint_Writer cimport JointWriter
from .Joint_Writer cimport PyJointWriter

from .Skin_Reader cimport SkinReader
from .Skin_Reader cimport PySkinReader

from .Visual_Reader cimport VisualReader
from .Visual_Reader cimport PyVisualReader

import xml.etree.ElementTree as ET
import os


cdef class iCubANN_wrapper:

    def __cinit__(self):
        print("Initialize iCub Interface.")
        #my_interface.init() - we need a special init?

        self.joint_reader = {}
        self.joint_reader_parts = {}

        self.joint_writer = {}
        self.joint_writer_parts = {}

        self.skin_reader = {}
        
        self.visual_reader = {}

    def __dealloc__(self):
        print("Close iCub Interface.")
        self.joint_reader.clear()
        self.joint_writer.clear()
        self.skin_reader.clear()
        self.visual_reader.clear()


    def clear(self):
        print("Clear iCub interface")
        size = len(self.joint_reader)
        while size > 0:
            self.joint_reader[list(self.joint_reader.keys())[0]].close(self)
            size = len(self.joint_reader)

        size = len(self.joint_reader)
        while size > 0:
            self.joint_writer[list(self.joint_writer.keys())[0]].close(self)
            size = len(self.joint_writer)

        size = len(self.skin_reader)
        while size > 0:
            self.skin_reader[list(self.skin_reader.keys())[0]].close(self)
            size = len(self.skin_reader)

        size = len(self.visual_reader)
        while size > 0:
            self.visual_reader[list(self.visual_reader.keys())[0]].close(self)
            size = len(self.visual_reader)

        self.joint_reader.clear()
        self.joint_writer.clear()
        self.skin_reader.clear()
        self.visual_reader.clear()


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
                self.skin_reader[name] = module
                module.name = name
                deref(module.cpp_skin_reader).setRegister(1)
                return True

    # unregister skin reader module
    def unregister_skin_reader(self, PySkinReader module):
        if deref(module.cpp_skin_reader).getRegister():
            deref(module.cpp_skin_reader).setRegister(0)
            self.skin_reader.pop(module.name, None)
            module.name = ""
            return True
        else:
            print("[Interface iCub] Skin Reader module is not yet registered!")
            return False

    # register visual reader module
    def register_vis_reader(self, str name, PyVisualReader module):
        if deref(module.cpp_visual_reader).getRegister():
            print("[Interface iCub] Visual Reader module is already registered!")
            return False
        else:
            if name in self.visual_reader:
                print("[Interface iCub] Visual Reader module name is already used!")
                return False
            self.visual_reader[name] = module
            module.name = name
            deref(module.cpp_visual_reader).setRegister(1)
            return True


    # unregister visual reader module
    def unregister_vis_reader(self, PyVisualReader module):
        if deref(module.cpp_visual_reader).getRegister():
            deref(module.cpp_visual_reader).setRegister(0)
            self.visual_reader.pop(module.name, None)
            module.name = ""
            return True
        else:
            print("[Interface iCub] Visual Reader module is not yet registered!")
            return False

    # get joint reader module by name
    def get_jreader_by_name(self, str name):
        if (name in self.joint_reader):
            return self.joint_reader[name]
        else:
            print("[Interface iCub] No Joint Reader module with the given name is registered!")
            return None

    # get joint reader module by part
    def get_jreader_by_part(self, str part):
        if (part in self.joint_reader_parts):
            return self.joint_reader[self.joint_reader_parts[part]]
        else:
            print("[Interface iCub] No Joint Reader module with the given part is registered!")
            return None

    # get joint writer module by name
    def get_jwriter_by_name(self, str name):
        if (name in self.joint_writer):
            return self.joint_writer[name]
        else:
            print("[Interface iCub] No Joint Writer module with the given name is registered!")
            return None

    # get joint writer module by part
    def get_jwriter_by_part(self, str part):
        if (part in self.joint_writer_parts):
            return self.joint_writer[self.joint_writer_parts[part]]
        else:
            print("[Interface iCub] No Joint Writer module with the given part is registered!")
            return None

    # get skin reader module by name
    def get_skinreader_by_name(self, str name):
        if (name in self.skin_reader):
            return self.skin_reader[name]
        else:
            print("[Interface iCub] No Skin Reader module with the given name is registered!")
            return None

    # get visual reader module by name
    def get_vis_reader_by_name(self, str name):
        if (name in self.visual_reader):
            return self.visual_reader[name]
        else:
            print("[Interface iCub] No Visual Reader module with the given name is registered!")
            return None

    # initialize interface for a robot configuration defined in a XML-file
    def init_robot_from_file(self, xml_file):
        name_dict = {}
        if os.path.isfile(xml_file):
            tree = ET.parse(xml_file)
            robot = tree.getroot()

            if not robot == None:
                # init joint reader
                for jread in robot.iter('JReader'):
                    args = {}
                    grpc = False
                    no_error_jread = True
                    if(jread.find('part') == None):
                        print("Element part is missing")
                        no_error_jread = False
                    else:
                        args['part'] = jread.find('part').text
                    if(jread.find('sigma') == None):
                        print("Element sigma is missing")
                        no_error_jread = False
                    else:
                        args['sigma'] = float(jread.find('sigma').text)
                    if(jread.find('popsize') == None):
                        print("Element popsize is missing")
                        no_error_jread = False
                    else:
                        args['popsize'] = int(jread.find('popsize').text)
                    if(jread.find('ini_path') == None):
                        print("Element ini_path is missing")
                        no_error_jread = False
                    else:
                        args['ini_path'] = jread.find('ini_path').text
                    if(not (jread.find('ip_address') == None)):
                        args['ip_address'] = jread.find('ip_address').text
                        if(not (jread.find('port') == None)):
                            args['port'] = int(jread.find('port').text)
                            grpc=True
                    if(jread.find('deg_per_neuron') == None):
                        if(no_error_jread):
                            reader = PyJointReader()
                            if grpc:
                                if not reader.init_grpc(self, jread.attrib['name'], args['part'], args['sigma'], args['popsize'], ini_path=args['ini_path'], ip_address=args['ip_address'] , port=args['port']):
                                    print("Init Joint Reader '" + jread.attrib['name'] + "' failed!")
                            else:
                                if not reader.init(self, jread.attrib['name'], args['part'], args['sigma'], args['popsize'], ini_path=args['ini_path']):
                                    print("Init Joint Reader '" + jread.attrib['name'] + "' failed!")
                        else:
                            print("Skipped Joint Reader '" + jread.attrib['name'] + "' init due to missing element")
                    else:
                        deg_per_neuron = float(jread.find('deg_per_neuron').text)
                        if(no_error_jread):
                            reader = PyJointReader()
                            if grpc:
                                if not reader.init_grpc(self, jread.attrib['name'], args['part'], args['sigma'], args['popsize'], deg_per_neuron=deg_per_neuron, ini_path=args['ini_path'], ip_address=args['ip_address'] , port=args['port']):
                                    print("Init Joint Reader '" + jread.attrib['name'] + "' failed!")
                            else:
                                if not reader.init(self, jread.attrib['name'], args['part'], args['sigma'], args['popsize'], deg_per_neuron=deg_per_neuron, ini_path=args['ini_path']):
                                    print("Init Joint Reader '" + jread.attrib['name'] + "' failed!")
                        else:
                            print("Skipped Joint Reader '" + jread.attrib['name'] + "' init due to missing element")

                # init joint writer
                for jwrite in robot.iter('JWriter'):
                    args = {}
                    grpc = False
                    no_error_jwrite = True
                    if(jwrite.find('part') == None):
                        print("Element part is missing")
                        no_error_jwrite = False
                    else:
                        args['part'] = jwrite.find('part').text
                    if(jwrite.find('popsize') == None):
                        print("Element popsize is missing")
                        no_error_jwrite = False
                    else:
                        args['popsize'] = int(jwrite.find('popsize').text)
                    if(jwrite.find('speed') == None):
                        print("Element speed is missing")
                        no_error_jwrite = False
                    else:
                        args['speed'] = float(jwrite.find('speed').text)
                    if(jwrite.find('ini_path') == None):
                        print("Element ini_path is missing")
                        no_error_jwrite = False
                    else:
                        args['ini_path'] = jwrite.find('ini_path').text
                    if(not (jwrite.find('ip_address') == None)):
                        args['ip_address'] = jwrite.find('ip_address').text
                        if(not (jwrite.find('port') == None)):
                            args['port'] = int(jwrite.find('port').text)
                            if(not (jwrite.find('joint_select') == None)):
                                args['joint_select'] = [int(x) for x in jwrite.find('joint_select').text.split(",")]
                                if(not (jwrite.find('mode') == None)):
                                    args['mode'] = jwrite.find('mode').text
                                    if(not (jwrite.find('blocking') == None)):
                                        args['blocking'] = bool(jwrite.find('blocking').text)
                                        grpc=True
                    if(jwrite.find('deg_per_neuron') == None):
                        if(no_error_jwrite):
                            writer = PyJointWriter()
                            if grpc:
                                if not writer.init_grpc(self, jwrite.attrib['name'], args['part'], args['popsize'], args['joint_select'], args['mode'], blocking=args['blocking'], speed=args['speed'], ini_path=args['ini_path'], ip_address=args['ip_address'] , port=args['port']):
                                    print("Init Joint Writer '" + jwrite.attrib['name'] + "' failed!")
                            else:
                                if not writer.init(self, jwrite.attrib['name'], args['part'], args['popsize'], args['speed'], ini_path=args['ini_path']):
                                    print("Init Joint Writer '" + jwrite.attrib['name'] + "' failed!")
                        else:
                            print("Skipped Joint Writer '" + jwrite.attrib['name'] + "' init due to missing element")
                    else:
                        deg_per_neuron = float(jwrite.find('deg_per_neuron').text)
                        if(no_error_jwrite):
                            writer = PyJointWriter()
                            if grpc:
                                if not writer.init_grpc(self, jwrite.attrib['name'], args['part'], args['popsize'], args['joint_select'], args['mode'], blocking=args['blocking'], speed=args['speed'], deg_per_neuron=deg_per_neuron, ini_path=args['ini_path'], ip_address=args['ip_address'] , port=args['port']):
                                    print("Init Joint Writer '" + jwrite.attrib['name'] + "' failed!")
                            else:
                                if not writer.init(self, jwrite.attrib['name'], args['part'], args['sigma'], args['popsize'], deg_per_neuron=deg_per_neuron, ini_path=args['ini_path']):
                                    print("Init Joint Writer '" + jwrite.attrib['name'] + "' failed!")
                        else:
                            print("Skipped Joint Writer '" + jwrite.attrib['name'] + "' init due to missing element")

                # init visual reader
                for vread in robot.iter('VisReader'):
                    args = {}
                    grpc = False
                    no_error_vread = True
                    if(vread.find('eye') == None):
                        print("Element eye is missing")
                        no_error_vread = False
                    else:
                        args['eye'] = vread.find('eye').text
                    if(vread.find('fov_width') == None or vread.find('fov_height') == None):
                        print("Element fov_width or fov_height is missing")
                        no_error_vread = False
                    else:
                        args['fov_width'] = float(vread.find('fov_width').text)
                        args['fov_height'] = float(vread.find('fov_height').text)
                    if(vread.find('img_width') == None or vread.find('img_height') == None):
                        print("Element img_width or img_height is missing")
                        no_error_vread = False
                    else:
                        args['img_width'] = float(vread.find('img_width').text)
                        args['img_height'] = float(vread.find('img_height').text)
                    if(vread.find('max_buffer_size') == None):
                        print("Element max_buffer_size is missing")
                        no_error_vread = False
                    else:
                        args['max_buffer_size'] = int(vread.find('max_buffer_size').text)
                    if(vread.find('fast_filter') == None):
                        print("Element fast_filter is missing")
                        no_error_vread = False
                    else:
                        args['fast_filter'] = bool(vread.find('fast_filter').text)
                    if(vread.find('ini_path') == None):
                        print("Element ini_path is missing")
                        no_error_vread = False
                    else:
                        args['ini_path'] = vread.find('ini_path').text
                    if(not (vread.find('ip_address') == None)):
                        args['ip_address'] = vread.find('ip_address').text
                        if(not (vread.find('port') == None)):
                            args['port'] = int(vread.find('port').text)
                            grpc=True
                    if(no_error_vread):
                        vreader = PyVisualReader()
                        if grpc:
                            if not vreader.init_grpc(self, vread.attrib['name'], args['eye'], args['fov_width'], args['fov_height'], args['img_width'], args['img_height'], args['max_buffer_size'], args['fast_filter'], ini_path=args['ini_path'], ip_address=args['ip_address'] , port=args['port']):
                                print("Init Visual Reader '" + vread.attrib['name'] + "' failed!")
                        else:
                            if not vreader.init(self, vread.attrib['name'], args['eye'], args['fov_width'], args['fov_height'], args['img_width'], args['img_height'], args['max_buffer_size'], args['fast_filter'], ini_path=args['ini_path']):
                                print("Init Visual Reader '" + vread.attrib['name'] + "' failed!")
                    else:
                        print("Skipped Visual Reader init due to missing element")

                # init tactile reader
                for sread in robot.iter('TacReader'):
                    args = {}
                    grpc = False
                    no_error_sread = True
                    if(sread.find('arm') == None):
                        print("Element arm is missing")
                        no_error_sread = False
                    else:
                        args['arm'] = sread.find('arm').text
                    if(sread.find('normalize') == None):
                        print("Element norm is missing")
                        no_error_sread = False
                    else:
                        args['norm'] = bool(sread.find('normalize').text)
                    if(sread.find('ini_path') == None):
                        print("Element ini_path is missing")
                        no_error_sread = False
                    else:
                        args['ini_path'] = sread.find('ini_path').text
                    if(not (sread.find('ip_address') == None)):
                        args['ip_address'] = sread.find('ip_address').text
                        if(not (sread.find('port') == None)):
                            args['port'] = int(sread.find('port').text)
                            grpc=True
                    if(no_error_sread):
                        sreader = PySkinReader()
                        if grpc:
                            if not sreader.init_grpc(self, sread.attrib['name'], args['arm'], args['norm'], args['ini_path'], ip_address=args['ip_address'] , port=args['port']):
                                print("Init Skin Reader '" + sread.attrib['name'] + "' failed!")
                        else:
                            if not sreader.init(self, sread.attrib['name'], args['arm'], args['norm'], args['ini_path']):
                                print("Init Skin Reader '" + sread.attrib['name'] + "' failed!")
                    else:
                        print("Skipped Skin Reader '" + sread.attrib['name'] + "' init due to missing element")

                name_dict["Joint_Reader"] = self.joint_reader.keys()
                name_dict["Joint_Writer"] = self.joint_writer.keys()
                name_dict["Skin_Reader"] = self.skin_reader.keys()
                name_dict["Visual_Reader"] = self.visual_reader.keys()

                return True, name_dict
            else:
                print("Failed to read XML-file")
                return False, name_dict
        else:
            print("Not a valid XML-Filepath given!")
            return False, name_dict
