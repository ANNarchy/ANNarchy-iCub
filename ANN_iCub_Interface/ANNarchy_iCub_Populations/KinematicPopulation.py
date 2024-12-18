"""
   Copyright (C) 2021-2022 Torsten Fietzek; Helge Ülo Dinkelbach

   KinematicPopulation.py is part of the ANNarchy iCub interface

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


class KinematicForward(SpecificPopulation):
    """
        ANNarchy population class to connect with the iCub forward kinematics.
        Readout the angles from the iCub, compute the forward kinematics and set it as population activation.
    """

    def __init__(self, geometry=(3,), ip_address="0.0.0.0", port=50020, copied=False, name=None):
        """Init the KinematicForward Population.

        Args:
            geometry (tuple, optional): ANNarchy population geometry. Defaults to (3,).
            ip_address (str, optional): ip-address of the gRPC connection. Need to fit with the respective kinematic reader module. Defaults to "0.0.0.0".
            port (int, optional): port of the gRPC connection. Need to fit with the respective kinematic reader module. Defaults to 50020.
            copied (bool, optional): ANNarchy specific parameter. Defaults to False.
            name (str, optional): individiual name for the population. Defaults to None.
        """
        SpecificPopulation.__init__(self, geometry=geometry, neuron=Neuron(equations="r = 0.0"), copied=copied, name=name)

        self._ip_address = ip_address
        self._port = port

    def _init_attributes(self):
        SpecificPopulation._init_attributes(self)

        self.cyInstance.set_ip_address(self._ip_address)
        self.cyInstance.set_port(self._port)

    def _copy(self):
        return KinematicForward(geometry=self.geometry, ip_address=self._ip_address, port=self._port, copied=True, name=self.name)

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
#include "ANN_iCub_Interface/grpc/ProvideInputClient.h"
"""
        self._specific_template['declare_additional'] = """
    std::string ip_address;
    unsigned int port;
    ClientInstance* kinematic_source=nullptr;
        """
        self._specific_template['access_additional'] = """
    // Kinematic Source ip address
    void set_ip_address(std::string value) {
        ip_address = value;
    }
    std::string get_ip_address() {
        return ip_address;
    }

    // Kinematic Source port
    void set_port(unsigned int value) {
        port = value;
    }
    unsigned int get_port() {
        return port;
    }

    void connect() {
        if (kinematic_source == nullptr) {
            kinematic_source = new ClientInstance(ip_address, port);
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

        self._specific_template['update_variables'] = """
        r = kinematic_source->retrieve_kinematic_hand();
        """

    def _instantiate(self, cython_module):
        # initializes cython wrapper
        SpecificPopulation._instantiate(self, cython_module)

    def connect(self):
        """Connect the population to the gRPC socket. Need to be called once after compile."""
        # create socket and connect
        if self.initialized:
            self.cyInstance.connect()
