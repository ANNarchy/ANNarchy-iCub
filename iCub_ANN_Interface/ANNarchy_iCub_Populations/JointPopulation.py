#===============================================================================
#
#     Copyright (C) 2021  Helge Uelo Dinkelbach, Torsten Fietzek
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     ANNarchy is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#===============================================================================
import iCub_ANN_Interface

from ANNarchy.core.Population import Population
from ANNarchy.core.Neuron import Neuron
from ANNarchy.core.Global import _error

from .iCubInterface import iCubInputInterface, iCubOutputInterface

class JointControl(Population):
    """
    Set the position/orientation of joints, e. g. elbow or finger.
    """
    def __init__(self, geometry=None, ip_address="0.0.0.0", port=50000, copied=False):

        Population.__init__(self, geometry=geometry, neuron = Neuron(parameters="r = 0.0"), copied=copied )

        self._iCub = iCubOutputInterface(ip_address=ip_address, port=port)

    def _init_attributes(self):

        Population._init_attributes(self)

        self.cyInstance.set_ip_address(self._iCub._ip_address)
        self.cyInstance.set_port(self._iCub._port)

    def _copy(self):

        return JointControl(geometry=self.geometry, ip_address=self._iCub._ip_address, port=self._iCub._port, copied=True)

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
        TODO: read out code for iCub through gRPC
        """
        include_paths = iCub_ANN_Interface.__path__[0]+"/grpc/"

        self._specific_template['include_additional'] = """// grpc stuff
#include "iCub_ANN_Interface/grpc/WriteOutputServer.h"
"""        

        self._specific_template['declare_additional'] = """
    std::string ip_address;
    unsigned int port;
    WriteOutputServerInstance<PopStruct%(id)s>* joint_server;
    std::thread server_thread;

    ~PopStruct%(id)s() {
        joint_server->shutdown();
        server_thread.join();
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
        joint_server = new WriteOutputServerInstance<PopStruct%(id)s>(ip_address, port, new WriteOutputServiceImpl<PopStruct%(id)s>(this) );
        this->server_thread = std::thread(&WriteOutputServerInstance<PopStruct%(id)s>::wait, this->joint_server);
    }
    """ % {'id': self.id}
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
        Population._instantiate(self, cython_module)

    def connect(self):
        # create socket and connect
        self._iCub.create_and_connect()

        if self.initialized:
            self.cyInstance.connect()

class JointReadout(Population):
    """
    Get the position/orientation of joints, e. g. elbow or finger.
    """
    def __init__(self, geometry=None, joints = None, encoded=False, ip_address="0.0.0.0", port=50005, copied=False):

        Population.__init__(self, geometry=geometry, neuron = Neuron(parameters="r = 0.0"), copied=copied )

        self._iCub = iCubInputInterface(ip_address=ip_address, port=port)
        self._joints = joints
        self._encoded = encoded


    def _init_attributes(self):

        Population._init_attributes(self)

        self.cyInstance.set_joints(self._joints)
        self.cyInstance.set_encoded(self._encoded)
        self.cyInstance.set_ip_address(self._iCub._ip_address)
        self.cyInstance.set_port(self._iCub._port)

    def _copy(self):

        return JointReadout(geometry=self.geometry, ip_address=self._iCub._ip_address, port=self._iCub._port, copied=True)

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
        TODO: read out code for iCub through gRPC
        """
        include_paths = iCub_ANN_Interface.__path__[0]+"/grpc/"

        self._specific_template['include_additional'] = """// grpc stuff
#include "iCub_ANN_Interface/grpc/ProvideInputClient.h"
"""
        self._specific_template['declare_additional'] = """
    std::string ip_address;
    unsigned int port;
    ClientInstance* joint_source;
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
        joint_source = new ClientInstance(ip_address, port);
    }
    """
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
        r  = joint_source->retrieve_alljoints(encoded);
        """
        elif len(self._joints) == 1:
            self._specific_template['update_variables'] = """
        r  = joint_source->retrieve_singlejoint(joints[0], encoded);
        """
        else:
            self._specific_template['update_variables'] = """
        r  = joint_source->retrieve_multijoints(joints, encoded);
        """

    def _instantiate(self, cython_module):

        # initializes cython wrapper
        Population._instantiate(self, cython_module)

    def connect(self):
        # create socket and connect
        self._iCub.create_and_connect()

        if self.initialized:
            self.cyInstance.connect()