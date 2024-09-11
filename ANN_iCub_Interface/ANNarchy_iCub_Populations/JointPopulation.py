"""
   Copyright (C) 2021-2022 Torsten Fietzek; Helge Ülo Dinkelbach

   JointPopulation.py is part of the ANNarchy iCub interface

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

import ANN_iCub_Interface
from ANNarchy.core.Neuron import Neuron
try:
    from ANNarchy.intern.SpecificPopulation import SpecificPopulation
    from ANNarchy.intern.Messages import _error

except:
    from ANNarchy.core.SpecificPopulation import SpecificPopulation
    from ANNarchy.core.Global import _error


class JointControl(SpecificPopulation):
    """
        ANNarchy population class to connect with the iCub joint control, e. g. arm or head.
        Readout the angles from the ANNarchy Population and send it to the iCub.
    """

    def __init__(self, geometry=None, neuron=Neuron(equations="r = 0.0"), ip_address="0.0.0.0", port=50010, copied=False, name=None):
        """Init the JointControl population.

        Args:
            geometry (tuple, optional): ANNarchy population geometry. Defaults to None.
            neuron (Neuron, optional): ANNarchy Neuron, being used in the population. Defaults to Neuron(equations="r = 0.0").
            ip_address (str, optional): ip-address of the gRPC connection. Need to fit with the respective joint writer module. Defaults to "0.0.0.0".
            port (int, optional): port of the gRPC connection. Need to fit with the respective joint reader module. Defaults to 50010.
            copied (bool, optional): ANNarchy specific parameter. Defaults to False.
            name (str, optional): individiual name for the population. Defaults to None.
        """
        SpecificPopulation.__init__(self, geometry=geometry, neuron=neuron, copied=copied, name=name)

        self._ip_address = ip_address
        self._port = port

    def _init_attributes(self):

        SpecificPopulation._init_attributes(self)

        self.cyInstance.set_ip_address(self._ip_address)
        self.cyInstance.set_port(self._port)

    def _copy(self):

        return JointControl(geometry=self.geometry, neuron=self.neuron_type, ip_address=self._ip_address, port=self._port, copied=True, name=self.name)

    @property
    def ip_address(self):
        if self.initialized:
            return self.cyInstance.get_ip_address()
        else:
            _error("Read-out IP address is only valid after compile().")

    @ip_address.setter
    def ip_address(self, value):
        if self.initialized:
            self.cyInstance.set_ip_address(value)
        else:
            _error("Changing IP address is only valid after compile() or constructor.")

    @property
    def port(self):
        if self.initialized:
            return self.cyInstance.get_port()
        else:
            _error("Read-out port is only valid after compile().")

    @port.setter
    def port(self, value):
        if self.initialized:
            self.cyInstance.set_port(value)
        else:
            _error("Changing port is only valid after compile() or constructor.")

    def _generate(self):
        """
            read out code for iCub through gRPC
        """
        include_paths = ANN_iCub_Interface.__path__[0]+"/grpc/"

        self._specific_template['include_additional'] = """// grpc stuff
#include "ANN_iCub_Interface/grpc/WriteOutputServer.h"
"""

        self._specific_template['declare_additional'] = """
    std::string ip_address;
    unsigned int port;
    WriteOutputServerInstance<PopStruct%(id)s>* joint_server=nullptr;
    std::thread server_thread;

    ~PopStruct%(id)s() {
        if (joint_server != nullptr) {
            joint_server->shutdown();
            server_thread.join();
        }
    }
    """ % {'id': self.id}
        self._specific_template['access_additional'] = """
    // Joint Source ip address
    void set_ip_address(std::string value) {
        ip_address = value;
    }
    std::string get_ip_address() {
        return ip_address;
    }

    // Joint Source port
    void set_port(unsigned int value) {
        port = value;
    }
    unsigned int get_port() {
        return port;
    }

    void connect() {
        if (joint_server == nullptr) {
            joint_server = new WriteOutputServerInstance<PopStruct%(id)s>(ip_address, port, new WriteOutputServiceImpl<PopStruct%(id)s>(this) );
            this->server_thread = std::thread(&WriteOutputServerInstance<PopStruct%(id)s>::wait, this->joint_server);
        } else {
            std::cerr << "Population %(name)s already connected" << std::endl;
        }
    }
    """ % {'id': self.id, 'name': self.name}
        self._specific_template['export_additional'] = """
        # IP Address and port
        void set_ip_address(string)
        string get_ip_address()
        void set_port(unsigned int)
        unsigned int get_port()
        void connect()
"""
        self._specific_template['wrapper_access_additional'] = """
    # IP Address and port
    def set_ip_address(self, value):
        pop%(id)s.set_ip_address(value.encode('utf-8'))
    def get_ip_address(self):
        return pop%(id)s.get_ip_address()
    def set_port(self, value):
        pop%(id)s.set_port(value)
    def get_port(self):
        return pop%(id)s.get_port()
    def connect(self):
        pop%(id)s.connect()
""" %{'id': self.id}

    def _instantiate(self, cython_module):
        # initializes cython wrapper
        SpecificPopulation._instantiate(self, cython_module)

    def connect(self):
        """Connect the population to the gRPC socket. Need to be called once after compile."""
        # create socket and connect
        if self.initialized:
            self.cyInstance.connect()


class JointReadout(SpecificPopulation):
    """
        ANNarchy population class to connect with the iCub joint readout, e. g. arm or head.
        Readout the angles from the iCub and set it as population activation.
    """

    def __init__(self, geometry=None, joints=None, encoded=False, ip_address="0.0.0.0", port=50005, copied=False, name=None):
        """Init the JointReadout population.

        Args:
            geometry (tuple, optional): ANNarchy population geometry. Defaults to None.
            joints (list, optional): Specify the joints, which should be accessed. Defaults to None.
            encoded (bool, optional): Specify if the joint angles should be encoded with a population coding. Defaults to False.
            ip_address (str, optional): ip-address of the gRPC connection. Need to fit with the respective joint reader module. Defaults to "0.0.0.0".
            port (int, optional): port of the gRPC connection. Need to fit with the respective joint reader module. Defaults to 50005.
            copied (bool, optional): ANNarchy specific parameter. Defaults to False.
            name (str, optional): individiual name for the population. Defaults to None.
        """
        SpecificPopulation.__init__(self, geometry=geometry, neuron=Neuron(equations="r = 0.0"), copied=copied, name=name)

        self._ip_address = ip_address
        self._port = port
        self._joints = joints
        self._encoded = encoded

    def _init_attributes(self):
        SpecificPopulation._init_attributes(self)

        self.cyInstance.set_joints(self._joints)
        self.cyInstance.set_encoded(self._encoded)
        self.cyInstance.set_ip_address(self._ip_address)
        self.cyInstance.set_port(self._port)

    def _copy(self):
        return JointReadout(geometry=self.geometry, joints=self._joints, encoded=self._encoded, ip_address=self._ip_address, port=self._port, copied=True, name=self.name)

    @property
    def ip_address(self):
        if self.initialized:
            return self.cyInstance.get_ip_address()
        else:
            _error("Read-out IP address is only valid after compile().")

    @ip_address.setter
    def ip_address(self, value):
        if self.initialized:
            self.cyInstance.set_ip_address(value)
        else:
            _error("Changing IP address is only valid after compile() or constructor.")

    @property
    def port(self):
        if self.initialized:
            return self.cyInstance.get_port()
        else:
            _error("Read-out port is only valid after compile().")

    @port.setter
    def port(self, value):
        if self.initialized:
            self.cyInstance.set_port(value)
        else:
            _error("Changing port is only valid after compile() or constructor.")

    @property
    def joints(self):
        if self.initialized:
            return self.cyInstance.get_joints()
        else:
            _error("Read-out joints is only valid after compile().")

    @joints.setter
    def joints(self, value):
        if self.initialized:
            self.cyInstance.set_joints(value)
        else:
            _error("Changing joints is only valid after compile() or constructor.")

    @property
    def encoded(self):
        if self.initialized:
            return self.cyInstance.get_encoded()
        else:
            _error("Read-out encoded is only valid after compile().")

    @encoded.setter
    def encoded(self, value):
        if self.initialized:
            self.cyInstance.set_encoded(value)
        else:
            _error("Changing encoded is only valid after compile() or constructor.")

    def _generate(self):
        """
            read out code for iCub through gRPC
        """
        include_paths = ANN_iCub_Interface.__path__[0]+"/grpc/"

        self._specific_template['include_additional'] = """// grpc stuff
#include "ANN_iCub_Interface/grpc/ProvideInputClient.h"
"""
        self._specific_template['declare_additional'] = """
    std::string ip_address;
    unsigned int port;
    ClientInstance* joint_source=nullptr;
    std::vector<int> joints;
    bool encoded;
        """
        self._specific_template['access_additional'] = """
    // Joint Source ip address
    void set_ip_address(std::string value) {
        ip_address = value;
    }
    std::string get_ip_address() {
        return ip_address;
    }

    // Joint Source port
    void set_port(unsigned int value) {
        port = value;
    }
    unsigned int get_port() {
        return port;
    }

    // Joint Source joint selection
    void set_joints(std::vector<int> value) {
        joints = value;
    }
    std::vector<int> get_joints() {
        return joints;
    }

    // Joint Source joint encoding
    void set_encoded(bool value) {
        encoded = value;
    }
    bool get_encoded() {
        return encoded;
    }

    void connect() {
        if (joint_source == nullptr) {
            joint_source = new ClientInstance(ip_address, port);
        } else {
            std::cerr << "Population %(name)s already connected" << std::endl;
        }
    }
    """ % {'name': self.name}
        self._specific_template['export_additional'] = """
        # IP Address and port
        void set_ip_address(string)
        string get_ip_address()
        void set_port(unsigned int)
        unsigned int get_port()
        void set_joints(vector[int])
        vector[int] get_joints()
        void set_encoded(bool)
        bool get_encoded()
        void connect()
"""
        self._specific_template['wrapper_access_additional'] = """
    # IP Address and port
    def set_ip_address(self, value):
        pop%(id)s.set_ip_address(value.encode('utf-8'))
    def get_ip_address(self):
        return pop%(id)s.get_ip_address()
    def set_port(self, value):
        pop%(id)s.set_port(value)
    def get_port(self):
        return pop%(id)s.get_port()
    def set_joints(self, value):
        pop%(id)s.set_joints(value)
    def get_joints(self):
        return pop%(id)s.get_joints()
    def set_encoded(self, value):
        pop%(id)s.set_encoded(value)
    def get_encoded(self):
        return pop%(id)s.get_encoded()
    def connect(self):
        pop%(id)s.connect()
""" %{'id': self.id}

        if len(self._joints) == 0:
            self._specific_template['update_variables'] = """
        #pragma omp single
        {
        r  = joint_source->retrieve_alljoints(encoded);
        }
        """
        elif len(self._joints) == 1:
            self._specific_template['update_variables'] = """
        #pragma omp single
        {
        r  = joint_source->retrieve_singlejoint(joints[0], encoded);
        }
        """
        else:
            self._specific_template['update_variables'] = """
        #pragma omp single
        {
        r  = joint_source->retrieve_multijoints(joints, encoded);
        }
        """

    def _instantiate(self, cython_module):
        # initializes cython wrapper
        SpecificPopulation._instantiate(self, cython_module)

    def connect(self):
        """Connect the population to the gRPC socket. Need to be called once after compile."""
        # create socket and connect
        if self.initialized:
            self.cyInstance.connect()
