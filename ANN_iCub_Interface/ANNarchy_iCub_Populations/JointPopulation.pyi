from typing import Tuple, List
try:
    from ANNarchy.intern.SpecificPopulation import SpecificPopulation

except:
    from ANNarchy.core.SpecificPopulation import SpecificPopulation


class JointControl(SpecificPopulation):
    """
        ANNarchy population class to connect with the iCub joint control, e. g. arm or head.
        Readout the angles from the ANNarchy Population and send it to the iCub.
    """
    def __init__(self, geometry: Tuple | None = ..., neuron=..., ip_address: str = ..., port: int = ..., copied: bool = ..., name: str | None = ...) -> None:
        '''Init the JointControl population.

        Args:
            geometry (tuple, optional): ANNarchy population geometry. Defaults to None.
            neuron (Neuron, optional): ANNarchy Neuron, being used in the population. Defaults to Neuron(equations="r = 0.0").
            ip_address (str, optional): ip-address of the gRPC connection. Need to fit with the respective joint writer module. Defaults to "0.0.0.0".
            port (int, optional): port of the gRPC connection. Need to fit with the respective joint reader module. Defaults to 50010.
            copied (bool, optional): ANNarchy specific parameter. Defaults to False.
            name (str, optional): individiual name for the population. Defaults to None.
        '''
    @property
    def ip_address(self): ...
    @ip_address.setter
    def ip_address(self, value) -> None: ...
    @property
    def port(self): ...
    @port.setter
    def port(self, value) -> None: ...
    def connect(self) -> None:
        """Connect the population to the gRPC socket. Need to be called once after compile."""


class JointReadout(SpecificPopulation):
    """
        ANNarchy population class to connect with the iCub joint readout, e. g. arm or head.
        Readout the angles from the iCub and set it as population activation.
    """
    def __init__(self, geometry: Tuple | None = ..., joints: List | None = ..., encoded: bool = ..., ip_address: str = ..., port: int = ..., copied: bool = ..., name: str | None = ...) -> None:
        '''Init the JointReadout population.

        Args:
            geometry (tuple, optional): ANNarchy population geometry. Defaults to None.
            joints (list, optional): Specify the joints, which should be accessed. Defaults to None.
            encoded (bool, optional): Specify if the joint angles should be encoded with a population coding. Defaults to False.
            ip_address (str, optional): ip-address of the gRPC connection. Need to fit with the respective joint reader module. Defaults to "0.0.0.0".
            port (int, optional): port of the gRPC connection. Need to fit with the respective joint reader module. Defaults to 50005.
            copied (bool, optional): ANNarchy specific parameter. Defaults to False.
            name (str, optional): individiual name for the population. Defaults to None.
        '''
    @property
    def ip_address(self): ...
    @ip_address.setter
    def ip_address(self, value) -> None: ...
    @property
    def port(self): ...
    @port.setter
    def port(self, value) -> None: ...
    @property
    def joints(self): ...
    @joints.setter
    def joints(self, value) -> None: ...
    @property
    def encoded(self): ...
    @encoded.setter
    def encoded(self, value) -> None: ...
    def connect(self) -> None:
        """Connect the population to the gRPC socket. Need to be called once after compile."""
