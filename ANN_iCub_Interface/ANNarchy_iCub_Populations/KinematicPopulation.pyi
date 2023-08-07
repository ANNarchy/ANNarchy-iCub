from ANNarchy.core.SpecificPopulation import SpecificPopulation
from typing import Tuple


class KinematicForward(SpecificPopulation):
    """
        ANNarchy population class to connect with the iCub forward kinematics.
        Readout the angles from the iCub, compute the forward kinematics and set it as population activation.
    """
    def __init__(self, geometry: Tuple =..., ip_address: str = ..., port: int = ..., copied: bool = ..., name: str | None = ...) -> None:
        '''Init the KinematicForward Population.

        Args:
            geometry (tuple, optional): ANNarchy population geometry. Defaults to (3,).
            ip_address (str, optional): ip-address of the gRPC connection. Need to fit with the respective kinematic reader module. Defaults to "0.0.0.0".
            port (int, optional): port of the gRPC connection. Need to fit with the respective kinematic reader module. Defaults to 50020.
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
