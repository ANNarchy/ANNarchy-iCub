from typing import Tuple
try:
    from ANNarchy.intern.SpecificPopulation import SpecificPopulation

except:
    from ANNarchy.core.SpecificPopulation import SpecificPopulation


class VisionPopulation(SpecificPopulation):
    """
        ANNarchy population class to connect with the iCub cameras.
        Read the camera images from the iCub, preprocess the images and set it as activation for the ANNarchy population.
    """
    def __init__(self, geometry: Tuple =..., ip_address: str = ..., port: int = ..., copied: bool = ..., name: str | None = ...) -> None:
        '''Init the VisionPopulation.

        Args:
            geometry (tuple, optional): ANNarchy population geometry. Defaults to (320,240).
            ip_address (str, optional): ip-address of the gRPC connection. Need to fit with the respective visual reader module. Defaults to "0.0.0.0".
            port (int, optional): port of the gRPC connection. Need to fit with the respective visual reader module. Defaults to 50000.
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
    def period(self): ...
    @period.setter
    def period(self, value) -> None: ...
    @property
    def offset(self): ...
    @offset.setter
    def offset(self, value) -> None: ...
    def connect(self) -> None:
        """Connect the population to the gRPC socket. Need to be called once after compile."""
