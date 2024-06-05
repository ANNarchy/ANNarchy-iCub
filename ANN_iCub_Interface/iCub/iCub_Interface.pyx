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

from .Module_Base_Class cimport PyModuleBase
from ..Special_Features import init_robot_from_file as sp_init_robot_from_file, save_robot_to_file as sp_save_robot_to_file


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

        size = len(self._joint_writer)
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


    '''
    # Access to interface instances via main warpper
    '''

    # get joint reader module by name
    def get_jreader_by_name(self, name: str):
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
    def get_jreader_by_part(self, part: str):
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
    def get_jwriter_by_name(self, name: str):
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
    def get_jwriter_by_part(self, part: str):
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
    def get_skinreader_by_name(self, name: str):
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
    def get_vis_reader_by_name(self, name: str):
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

    # get kinematic reader module by name
    def get_kin_reader_by_name(self, name: str):
        """Returns the Kinematic Reader instance with the given name.

        Parameters
        ----------
        name : str
            Name of the Kinematic Reader instance.

        Returns
        -------
        PyKinematicReader
            Kinematic Reader instance
        """
        if (name in self._kinematic_reader):
            return self._kinematic_reader[name]
        else:
            print("[Interface iCub] No Kinematic Reader module with the given name is registered!")
            return None

    # get kinematic reader module by name
    def get_kin_writer_by_name(self, name: str):
        """Returns the Kinematic Writer instance with the given name.

        Parameters
        ----------
        name : str
            Name of the Kinematic Writer instance.

        Returns
        -------
        PyKinematicWriter
            Kinematic Writer instance
        """
        if (name in self._kinematic_writer):
            return self._kinematic_writer[name]
        else:
            print("[Interface iCub] No Kinematic Writer module with the given name is registered!")
            return None


    def _get_jreader_dict(self):
        return self._joint_reader

    def _get_jwriter_dict(self):
        return self._joint_writer

    def _get_kreader_dict(self):
        return self._kinematic_reader

    def _get_kwriter_dict(self):
        return self._kinematic_writer

    def _get_sreader_dict(self):
        return self._skin_reader
    
    def _get_vreader_dict(self):
        return self._visual_reader

    def init_robot_from_file(self, xml_file: str):
        print("Function deprecated; Please use ANN_iCub_Interface.init_robot_from_file-method instead!")
        return sp_init_robot_from_file(self, xml_file)

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
        print("Function deprecated; Please use ANN_iCub_Interface.save_robot_to_file-method instead!")
        return sp_save_robot_to_file(self, xml_file, description)
