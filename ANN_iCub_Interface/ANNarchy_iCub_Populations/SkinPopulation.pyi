from ANNarchy.core.SpecificPopulation import SpecificPopulation
from _typeshed import Incomplete


class SkinPopulation(SpecificPopulation):
    """
        ANNarchy population class to connect with the iCub skin.
        Readout the skin sensor data and set it as population activation.
    """
    name: Incomplete
    def __init__(self, geometry: Incomplete | None = ..., skin_section: str = ..., ip_address: str = ..., port: int = ..., copied: bool = ..., name: Incomplete | None = ...) -> None:
        '''Init the SkinPopulation.

        Args:
            geometry (tuple, optional): ANNarchy population geometry. Defaults to None.
            skin_section (str, optional): Specify the respective skin section of the used arm. Defaults to "".
            ip_address (str, optional): ip-address of the gRPC connection. Need to fit with the respective kinematic reader module. Defaults to "0.0.0.0".
            port (int, optional): port of the gRPC connection. Need to fit with the respective kinematic reader module. Defaults to 50015.
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
