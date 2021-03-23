from ANNarchy.core.Population import Population
from ANNarchy.core.Neuron import Neuron
from .iCubInterface import iCubInputInterface

class SkinPopulation(Population):

    def __init__(self, geometry=None, ip_address="0.0.0.0", port="50000", copied=False):

        Population.__init__(self, geometry=geometry, neuron = Neuron(parameters="r = 0.0"), copied=copied )

        self._iCub = iCubInputInterface(ip_address=ip_address, port=port)

    def _copy(self):
        
        return SkinPopulation(geometry=self.geometry, ip_address=self._iCub._ip_address, port=self._iCub._port, copied=True)

    def _generate(self):
        """
        TODO: read out code for iCub through gRPC
        """
        self._specific_template['update_variables'] = ""

    def _instantiate(self, cython_module):

        # initializes cython wrapper
        Population._instantiate(self, cython_module)

        # create socket and connect
        self._iCub.create_and_connect()
