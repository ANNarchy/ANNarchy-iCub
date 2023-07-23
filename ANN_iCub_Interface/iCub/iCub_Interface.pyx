# distutils: language = c++
# cython: language_level = 3
# cython: binding=True
# cython: embedsignature=True
# cython: embedsignature.format=python

"""
   Copyright (C) 2019-2023 Torsten Fietzek; Helge Ülo Dinkelbach

   iCubCPP.pyx is part of the ANNarchy iCub interface

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   The ANNarchy iCub interface is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this headers. If not, see [http://www.gnu.org/licenses/].
 """

import os
import xml.etree.ElementTree as ET
from typing import Tuple
from xml.dom import minidom

from cython.operator cimport dereference as deref

from .Kinematic_Writer cimport PyKinematicWriter
from .Kinematic_Reader cimport PyKinematicReader
from .Visual_Reader cimport PyVisualReader
from .Skin_Reader cimport PySkinReader
from .Joint_Writer cimport PyJointWriter
from .Joint_Reader cimport PyJointReader


def _textToList(liststring):
    l_x = liststring.strip('[]').replace('\'', '').replace(' ', '')
    if len(l_x) == 0:
        return list(l_x)
    else:
        return [int(x) for x in l_x.split(",")]


cdef class ANNiCub_wrapper:
    """Main wrapper class"""

    # interface constructor
    def __cinit__(self):
        print("Initialize iCub Interface.")

        self._joint_reader = {}
        self._joint_reader_parts = {}
        self._joint_writer = {}
        self._joint_writer_parts = {}
        self._skin_reader = {}
        self._visual_reader = {}
        self._kinematic_reader = {}
        self._kinematic_writer = {}

    # interface destructor
    def __dealloc__(self):
        print("Close iCub Interface.")
        if self._joint_reader is not None:
            self._joint_reader.clear()
        if self._joint_writer is not None:
            self._joint_writer.clear()
        if self._skin_reader is not None:
            self._skin_reader.clear()
        if self._visual_reader is not None:
            self._visual_reader.clear()
        if self._kinematic_reader is not None:
            self._kinematic_reader.clear()
        if self._kinematic_writer is not None:
            self._kinematic_writer.clear()

    '''
    # Manage the reader/writer modules
    # Handling of the Reader and Writer modules in the main Interface
    '''

    # close all interface modules
    def clear(self):
        """Clean-up all initialized interface instances"""
        print("Clear iCub interface")
        size = len(self._joint_reader)
        while size > 0:
            self._joint_reader[list(self._joint_reader.keys())[0]].close(self)
            size = len(self._joint_reader)

        size = len(self._joint_reader)
        while size > 0:
            self._joint_writer[list(self._joint_writer.keys())[0]].close(self)
            size = len(self._joint_writer)

        size = len(self._skin_reader)
        while size > 0:
            self._skin_reader[list(self._skin_reader.keys())[0]].close(self)
            size = len(self._skin_reader)

        size = len(self._visual_reader)
        while size > 0:
            self._visual_reader[list(self._visual_reader.keys())[0]].close(self)
            size = len(self._visual_reader)

        size = len(self._kinematic_reader)
        while size > 0:
            self._kinematic_reader[list(self._kinematic_reader.keys())[0]].close(self)
            size = len(self._kinematic_reader)

        size = len(self._kinematic_writer)
        while size > 0:
            self._kinematic_writer[list(self._kinematic_writer.keys())[0]].close(self)
            size = len(self._kinematic_writer)

        self._joint_reader.clear()
        self._joint_writer.clear()
        self._skin_reader.clear()
        self._visual_reader.clear()
        self._kinematic_reader.clear()
        self._kinematic_writer.clear()

    # register joint reader module
    def register_jreader(self, name: str, module: PyJointReader):
        """Register Joint Reader module at the main wrapper.
            -> For internal use only.

        Parameters
        ----------
        name : str
            name given to the Joint Reader
        module : PyJointReader
            Joint Reader instance

        Returns
        -------
        bool
            True/False on Success/Failure
        """
        if deref(module._cpp_joint_reader).getRegister():
            print("[Interface iCub] Joint Reader module is already registered!")
            return False
        else:
            if name in self._joint_reader:
                print("[Interface iCub] Joint Reader module name is already used!")
                return False
            else:
                if module._part in self._joint_reader_parts:
                    print("[Interface iCub] Joint Reader module part is already used!")
                    return False
                else:
                    self._joint_reader[name] = module
                    module._name = name
                    self._joint_reader_parts[module._part] = name
                    deref(module._cpp_joint_reader).setRegister(1)
                    return True

    # unregister joint reader  module
    def unregister_jreader(self, module: PyJointReader):
        """Unregister Joint Reader module at the main wrapper.
            -> For internal use only.

        Parameters
        ----------
        module : PyJointReader
            Joint Reader instance

        Returns
        -------
        bool
            True/False on Success/Failure
        """
        if deref(module._cpp_joint_reader).getRegister():
            deref(module._cpp_joint_reader).setRegister(0)
            self._joint_reader.pop(module._name, None)
            self._joint_reader_parts.pop(module._part, None)
            module._name = ""
            return True
        else:
            print("[Interface iCub] Joint Reader module is not yet registered!")
            return False

    # register joint writer  module
    def register_jwriter(self, name: str, module: PyJointWriter):
        """Register Joint Writer module at the main wrapper.
            -> For internal use only.

        Parameters
        ----------
        name : str
            name given to the Joint Writer
        module : PyJointWriter
            Joint Writer instance

        Returns
        -------
        bool
            True/False on Success/Failure
        """
        if deref(module._cpp_joint_writer).getRegister():
            print("[Interface iCub] Joint Writer module is already registered!")
            return False
        else:
            if name in self._joint_writer:
                print("[Interface iCub] Joint Writer module name is already used!")
                return False
            else:
                if module._part in self._joint_writer_parts:
                    print("[Interface iCub] Joint Writer module part is already used!")
                    return False
                else:
                    self._joint_writer[name] = module
                    module._name = name
                    self._joint_writer_parts[module._part] = name
                    deref(module._cpp_joint_writer).setRegister(1)
                    return True

    # unregister joint writer module
    def unregister_jwriter(self, module: PyJointWriter):
        """Unregister Joint Writer module at the main wrapper.
            -> For internal use only.

        Parameters
        ----------
        module : PyJointWriter
            Joint Writer instance

        Returns
        -------
        bool
            True/False on Success/Failure
        """
        if deref(module._cpp_joint_writer).getRegister():
            deref(module._cpp_joint_writer).setRegister(0)
            self._joint_writer.pop(module._name, None)
            self._joint_writer_parts.pop(module._part, None)
            module._name = ""
            return True
        else:
            print("[Interface iCub] Joint Writer module is not yet registered!")
            return False

    # register skin reader module
    def register_skin_reader(self, name: str, module: PySkinReader):
        """Register Skin Reader module at the main wrapper.
            -> For internal use only.

        Parameters
        ----------
        name : str
            name given to the Skin Reader
        module : PySkinReader
            Skin Reader instance

        Returns
        -------
        bool
            True/False on Success/Failure
        """
        if deref(module._cpp_skin_reader).getRegister():
            print("[Interface iCub] Skin Reader module is already registered!")
            return False
        else:
            if name in self._skin_reader:
                print("[Interface iCub] Skin Reader module name is already used!")
                return False
            else:
                self._skin_reader[name] = module
                module._name = name
                deref(module._cpp_skin_reader).setRegister(1)
                return True

    # unregister skin reader module
    def unregister_skin_reader(self, module: PySkinReader):
        """Unregister Skin Reader module at the main wrapper.
            -> For internal use only.

        Parameters
        ----------
        module : PySkinReader
            Skin Reader instance

        Returns
        -------
        bool
            True/False on Success/Failure
        """
        if deref(module._cpp_skin_reader).getRegister():
            deref(module._cpp_skin_reader).setRegister(0)
            self._skin_reader.pop(module._name, None)
            module._name = ""
            return True
        else:
            print("[Interface iCub] Skin Reader module is not yet registered!")
            return False

    # register visual reader module
    def register_vis_reader(self, name: str, module: PyVisualReader):
        """Register Visual Reader module at the main wrapper.
            -> For internal use only.

        Parameters
        ----------
        name : str
            name given to the Visual Reader
        module : PyVisualReader
            Visual Reader instance

        Returns
        -------
        bool
            True/False on Success/Failure
        """
        if deref(module._cpp_visual_reader).getRegister():
            print("[Interface iCub] Visual Reader module is already registered!")
            return False
        else:
            if name in self._visual_reader:
                print("[Interface iCub] Visual Reader module name is already used!")
                return False
            self._visual_reader[name] = module
            module._name = name
            deref(module._cpp_visual_reader).setRegister(1)
            return True

    # unregister visual reader module
    def unregister_vis_reader(self, module: PyVisualReader):
        """Unregister Visual Reader module at the main wrapper.
            -> For internal use only.

        Parameters
        ----------
        module : PyVisualReader
            Visual Reader instance

        Returns
        -------
        bool
            True/False on Success/Failure
        """
        if deref(module._cpp_visual_reader).getRegister():
            deref(module._cpp_visual_reader).setRegister(0)
            self._visual_reader.pop(module._name, None)
            module._name = ""
            return True
        else:
            print("[Interface iCub] Visual Reader module is not yet registered!")
            return False

    # register kinematic reader module
    def register_kin_reader(self, name: str, module: PyKinematicReader):
        """Register Kinematic Reader module at the main wrapper.
            -> For internal use only.

        Parameters
        ----------
        name : str
            name given to the Kinematic Reader
        module : PyKinematicReader
            Kinematic Reader instance

        Returns
        -------
        bool
            True/False on Success/Failure
        """
        if deref(module._cpp_kin_reader).getRegister():
            print("[Interface iCub] Kinematic Reader module is already registered!")
            return False
        else:
            if name in self._kinematic_reader:
                print("[Interface iCub] Kinematic Reader module name is already used!")
                return False
            self._kinematic_reader[name] = module
            module._name = name
            deref(module._cpp_kin_reader).setRegister(1)
            return True

    # unregister kinematic reader module
    def unregister_kin_reader(self, module: PyKinematicReader):
        """Unregister Kinematic Reader module at the main wrapper.
            -> For internal use only.

        Parameters
        ----------
        module : PyKinematicReader
            Kinematic Reader instance

        Returns
        -------
        bool
            True/False on Success/Failure
        """
        if deref(module._cpp_kin_reader).getRegister():
            deref(module._cpp_kin_reader).setRegister(0)
            self._kinematic_reader.pop(module._name, None)
            module._name = ""
            return True
        else:
            print("[Interface iCub] Kinematic Reader module is not yet registered!")
            return False

    # register kinematic writer module
    def register_kin_writer(self, name: str, module: PyKinematicWriter):
        """Register Kinematic Writer module at the main wrapper.
            -> For internal use only.

        Parameters
        ----------
        name : str
            name given to the Kinematic Writer
        module : PyKinematicWriter
            Kinematic Writer instance

        Returns
        -------
        bool
            True/False on Success/Failure
        """
        if deref(module._cpp_kin_writer).getRegister():
            print("[Interface iCub] Kinematic Writer module is already registered!")
            return False
        else:
            if name in self._kinematic_writer:
                print("[Interface iCub] Kinematic Writer module name is already used!")
                return False
            self._kinematic_writer[name] = module
            module._name = name
            deref(module._cpp_kin_writer).setRegister(1)
            return True

    # unregister kinematic writer module
    def unregister_kin_writer(self, module: PyKinematicWriter):
        """Unregister Kinematic Writer module at the main wrapper.
            -> For internal use only.

        Parameters
        ----------
        module : PyKinematicWriter
            Kinematic Writer instance

        Returns
        -------
        bool
            True/False on Success/Failure
        """
        if deref(module._cpp_kin_writer).getRegister():
            deref(module._cpp_kin_writer).setRegister(0)
            self._kinematic_writer.pop(module._name, None)
            module._name = ""
            return True
        else:
            print("[Interface iCub] Kinematic Writer module is not yet registered!")
            return False

    '''
    # Access to interface instances via main warpper
    # TODO: Add getter for kinematic modules
    '''

    # get joint reader module by name
    def get_jreader_by_name(self, name: str) -> PyJointReader:
        """Returns the Joint Reader instance with the given name.

        Parameters
        ----------
        name : str
            Name of the Joint Reader instance.

        Returns
        -------
        PyJointReader
            Joint Reader instance
        """
        if (name in self._joint_reader):
            return self._joint_reader[name]
        else:
            print("[Interface iCub] No Joint Reader module with the given name is registered!")
            return None

    # get joint reader module by part
    def get_jreader_by_part(self, part: str) -> PyJointReader:
        """Returns the Joint Reader instance with the given part.

        Parameters
        ----------
        part : str
            The robot part which is controlled by the Joint Reader.

        Returns
        -------
        PyJointReader
            Joint Reader instance
        """
        if (part in self._joint_reader_parts):
            return self._joint_reader[self._joint_reader_parts[part]]
        else:
            print("[Interface iCub] No Joint Reader module with the given part is registered!")
            return None

    # get joint writer module by name
    def get_jwriter_by_name(self, name: str) -> PyJointWriter:
        """Returns the Joint Writer instance with the given name.

        Parameters
        ----------
        name : str
            Name of the Joint Writer instance.

        Returns
        -------
        PyJointWriter
            Joint Writer instance
        """
        if (name in self._joint_writer):
            return self._joint_writer[name]
        else:
            print("[Interface iCub] No Joint Writer module with the given name is registered!")
            return None

    # get joint writer module by part
    def get_jwriter_by_part(self, part: str) -> PyJointWriter:
        """Returns the Joint Writer instance with the given part.

        Parameters
        ----------
        part : str
            The robot part which is controlled by the Joint Writer.

        Returns
        -------
        PyJointWriter
            Joint Writer instance
        """
        if (part in self._joint_writer_parts):
            return self._joint_writer[self._joint_writer_parts[part]]
        else:
            print("[Interface iCub] No Joint Writer module with the given part is registered!")
            return None

    # get skin reader module by name
    def get_skinreader_by_name(self, name: str) -> PySkinReader:
        """Returns the Skin Reader instance with the given name.

        Parameters
        ----------
        name : str
            Name of the Skin Reader instance.

        Returns
        -------
        PySkinReader
            Skin Reader instance
        """
        if (name in self._skin_reader):
            return self._skin_reader[name]
        else:
            print("[Interface iCub] No Skin Reader module with the given name is registered!")
            return None

    # get visual reader module by name
    def get_vis_reader_by_name(self, name: str) -> PyVisualReader:
        """Returns the Visual Reader instance with the given name.

        Parameters
        ----------
        name : str
            Name of the Visual Reader instance.

        Returns
        -------
        PyVisualReader
            Visual Reader instance
        """
        if (name in self._visual_reader):
            return self._visual_reader[name]
        else:
            print("[Interface iCub] No Visual Reader module with the given name is registered!")
            return None

    '''
    # Global loading/ saving methods for whole interface configuration
    # TODO: extend for kinematic modules
    '''

    # initialize interface for a robot configuration defined in a XML-file
    def init_robot_from_file(self, xml_file: str) -> Tuple[bool, str]:
        """Init iCub interface with the modules given in the xml-file

        Parameters
        ----------
        xml_file : str
            filename of the xml-config-file

        Returns
        -------
        Tuple[bool, str]
            Returns a bool value representing the success of the init and a dicionary containing the module names for each module type
        """
        name_dict = {}
        if os.path.isfile(xml_file):
            tree = ET.parse(xml_file)
            robot = tree.getroot()

            if robot is not None:
                # init joint reader
                for jread in robot.iter('JReader'):
                    args = {'name': jread.attrib['name']}
                    grpc = False
                    no_error_jread = True
                    if (jread.find('part') is None):
                        print("Element part is missing")
                        no_error_jread = False
                    else:
                        args['part'] = jread.find('part').text
                    if (jread.find('sigma') is None):
                        print("Element sigma is missing")
                        no_error_jread = False
                    else:
                        args['sigma'] = float(jread.find('sigma').text)
                    if (jread.find('popsize') is None):
                        if (jread.find('n_pop') is None):
                            print("Element popsize is missing")
                            no_error_jread = False
                        else:
                            args['n_pop'] = int(jread.find('n_pop').text)
                    else:
                        args['n_pop'] = int(jread.find('popsize').text)
                    if (jread.find('ini_path') is None):
                        print("Element ini_path is missing")
                        no_error_jread = False
                    else:
                        args['ini_path'] = jread.find('ini_path').text
                    if (jread.find('ip_address') is not None):
                        args['ip_address'] = jread.find('ip_address').text
                        if (jread.find('port') is not None):
                            args['port'] = int(jread.find('port').text)
                            grpc = True
                    if (jread.find('deg_per_neuron') is not None):
                        deg_per_neuron = float(jread.find('deg_per_neuron').text)

                    if (no_error_jread):
                        reader = PyJointReader()
                        if grpc:
                            if not reader.init_grpc(self, **args):
                                print("Init Joint Reader '" + jread.attrib['name'] + "' failed!")
                        else:
                            if not reader.init(self, **args):
                                print("Init Joint Reader '" + jread.attrib['name'] + "' failed!")
                    else:
                        print("Skipped Joint Reader '" + jread.attrib['name'] + "' init due to missing element")

                # init joint writer
                for jwrite in robot.iter('JWriter'):
                    args = {}
                    grpc = False
                    no_error_jwrite = True
                    if (jwrite.find('part') is None):
                        print("Element part is missing")
                        no_error_jwrite = False
                    else:
                        args['part'] = jwrite.find('part').text
                    if (jwrite.find('popsize') is None):
                        if (jwrite.find('n_pop') is None):
                            print("Element popsize is missing")
                            no_error_jwrite = False
                        else:
                            args['n_pop'] = int(jwrite.find('n_pop').text)
                    else:
                        args['n_pop'] = int(jwrite.find('popsize').text)
                    if (jwrite.find('speed') is None):
                        print("Element speed is missing")
                        no_error_jwrite = False
                    else:
                        args['speed'] = float(jwrite.find('speed').text)
                    if (jwrite.find('ini_path') is None):
                        print("Element ini_path is missing")
                        no_error_jwrite = False
                    else:
                        args['ini_path'] = jwrite.find('ini_path').text
                    if (jwrite.find('ip_address') is not None):
                        args['ip_address'] = jwrite.find('ip_address').text
                        if (jwrite.find('port') is not None):
                            args['port'] = int(jwrite.find('port').text)
                            if (jwrite.find('mode') is not None):
                                args['mode'] = jwrite.find('mode').text
                                if (jwrite.find('blocking') is not None):
                                    args['blocking'] = eval(jwrite.find('blocking').text.capitalize())
                                    if (jwrite.find('joint_select') is not None):
                                        args['joints'] = _textToList(jwrite.find('joint_select').text)
                                        grpc = True
                                    elif (jwrite.find('joints') is not None):
                                        args['joints'] = _textToList(jwrite.find('joints').text)
                                        grpc = True
                    if (jwrite.find('deg_per_neuron') is not None):
                        deg_per_neuron = float(jwrite.find('deg_per_neuron').text)

                    if (no_error_jwrite):
                        writer = PyJointWriter()
                        if grpc:
                            if not writer.init_grpc(self, jwrite.attrib['name'], **args):
                                print("Init Joint Writer '" + jwrite.attrib['name'] + "' failed!")
                        else:
                            if not writer.init(self, jwrite.attrib['name'], **args):
                                print("Init Joint Writer '" + jwrite.attrib['name'] + "' failed!")
                    else:
                        print("Skipped Joint Writer '" + jwrite.attrib['name'] + "' init due to missing element")

                # init visual reader
                for vread in robot.iter('VisReader'):
                    args = {}
                    grpc = False
                    no_error_vread = True
                    if (vread.find('eye') is None):
                        print("Element eye is missing")
                        no_error_vread = False
                    else:
                        args['eye'] = vread.find('eye').text
                    if (vread.find('fov_width') is None or vread.find('fov_height') is None):
                        print("Element fov_width or fov_height is missing")
                        no_error_vread = False
                    else:
                        args['fov_width'] = float(vread.find('fov_width').text)
                        args['fov_height'] = float(vread.find('fov_height').text)
                    if (vread.find('img_width') is None or vread.find('img_height') is None):
                        print("Element img_width or img_height is missing")
                        no_error_vread = False
                    else:
                        args['img_width'] = float(vread.find('img_width').text)
                        args['img_height'] = float(vread.find('img_height').text)
                    if (vread.find('fast_filter') is None):
                        print("Element fast_filter is missing")
                        no_error_vread = False
                    else:
                        args['fast_filter'] = eval(vread.find('fast_filter').text.capitalize())
                    if (vread.find('ini_path') is None):
                        print("Element ini_path is missing")
                        no_error_vread = False
                    else:
                        args['ini_path'] = vread.find('ini_path').text
                    if (vread.find('ip_address') is not None):
                        args['ip_address'] = vread.find('ip_address').text
                        if (vread.find('port') is not None):
                            args['port'] = int(vread.find('port').text)
                            grpc = True
                    if (no_error_vread):
                        vreader = PyVisualReader()
                        if grpc:
                            if not vreader.init_grpc(self, vread.attrib['name'], args['eye'], args['fov_width'], args['fov_height'], args['img_width'], args['img_height'],
                                                     args['fast_filter'], ini_path=args['ini_path'], ip_address=args['ip_address'], port=args['port']):
                                print("Init Visual Reader '" + vread.attrib['name'] + "' failed!")
                        else:
                            if not vreader.init(self, vread.attrib['name'], args['eye'], args['fov_width'], args['fov_height'], args['img_width'], args['img_height'],
                                                args['fast_filter'], ini_path=args['ini_path']):
                                print("Init Visual Reader '" + vread.attrib['name'] + "' failed!")
                    else:
                        print("Skipped Visual Reader init due to missing element")

                # init tactile reader
                for sread in robot.iter('TacReader'):
                    args = {}
                    grpc = False
                    no_error_sread = True
                    if (sread.find('arm') is None):
                        print("Element arm is missing")
                        no_error_sread = False
                    else:
                        args['arm'] = sread.find('arm').text
                    if (sread.find('normalize') is None):
                        print("Element norm is missing")
                        no_error_sread = False
                    else:
                        args['norm'] = eval(sread.find('normalize').text.capitalize())
                    if (sread.find('ini_path') is None):
                        print("Element ini_path is missing")
                        no_error_sread = False
                    else:
                        args['ini_path'] = sread.find('ini_path').text
                    if (sread.find('ip_address') is not None):
                        args['ip_address'] = sread.find('ip_address').text
                        if (sread.find('port') is not None):
                            args['port'] = int(sread.find('port').text)
                            grpc = True
                    if (no_error_sread):
                        sreader = PySkinReader()
                        if grpc:
                            if not sreader.init_grpc(self, sread.attrib['name'], args['arm'], args['norm'], args['ini_path'], ip_address=args['ip_address'], port=args['port']):
                                print("Init Skin Reader '" + sread.attrib['name'] + "' failed!")
                        else:
                            if not sreader.init(self, sread.attrib['name'], args['arm'], args['norm'], args['ini_path']):
                                print("Init Skin Reader '" + sread.attrib['name'] + "' failed!")
                    else:
                        print("Skipped Skin Reader '" + sread.attrib['name'] + "' init due to missing element")

                name_dict["Joint_Reader"] = self._joint_reader.keys()
                name_dict["Joint_Writer"] = self._joint_writer.keys()
                name_dict["Skin_Reader"] = self._skin_reader.keys()
                name_dict["Visual_Reader"] = self._visual_reader.keys()

                return True, name_dict
            else:
                print("Failed to read XML-file")
                return False, name_dict
        else:
            print("Not a valid XML-Filepath given!")
            return False, name_dict

    # save robot robot configuration as XML-file
    def save_robot_to_file(self, xml_file: str, description: str = ""):
        """Save robot configuration to xml-config file

        Parameters
        ----------
        xml_file : str
            filename for the xml-config-file
        description : str
            optional description added as comment in the robot section. Defaults to "".

        Returns
        -------

        """
        root = ET.Element("robot")
        root.append(ET.Comment(description))

        for name, module in self._joint_reader.items():
            JReader = ET.SubElement(root, "JReader", attrib={"name": name})
            jread_cast = <PyJointReader> module
            jread_param = deref(jread_cast._cpp_joint_reader).getParameter()
            for key, value in (<dict> jread_param).items():
                ET.SubElement(JReader, key.decode('utf-8')).text = value.decode('utf-8')

        for name, module in self._joint_writer.items():
            JWriter = ET.SubElement(root, "JWriter", attrib={"name": name})
            jwrite_cast = <PyJointWriter> module
            jwrite_param = deref(jwrite_cast._cpp_joint_writer).getParameter()
            for key, value in (<dict> jwrite_param).items():
                ET.SubElement(JWriter, key.decode('utf-8')).text = value.decode('utf-8')

        for name, module in self._visual_reader.items():
            VReader = ET.SubElement(root, "VisReader", attrib={"name": name})
            vread_cast = <PyVisualReader> module
            vread_param = deref(vread_cast._cpp_visual_reader).getParameter()
            for key, value in (<dict> vread_param).items():
                ET.SubElement(VReader, key.decode('utf-8')).text = value.decode('utf-8')

        for name, module in self._skin_reader.items():
            SReader = ET.SubElement(root, "TacReader", attrib={"name": name})
            sread_cast = <PySkinReader> module
            sread_param = deref(sread_cast._cpp_skin_reader).getParameter()
            for key, value in (<dict> sread_param).items():
                ET.SubElement(SReader, key.decode('utf-8')).text = value.decode('utf-8')

        XML_file_string = minidom.parseString(ET.tostring(root, 'utf-8')).toprettyxml(indent="    ")
        with open(xml_file, "w") as files:
            files.write(XML_file_string)
