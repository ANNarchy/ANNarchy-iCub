from typing import Any, NoReturn
from numpy import ndarray
from .iCub_Interface import ANNiCub_wrapper


class PyKinematicWriter:
    @classmethod
    def __init__(cls, *args, **kwargs) -> None: ...

    def close(self, iCub: ANNiCub_wrapper) -> NoReturn:
        """Close the module.

        Args:
            iCub (ANNiCub_wrapper): main interface wrapper
        """
        ...

    def get_DOF(self) -> int:
        """Return the DOF of the kinematic chain.

        Returns:
            int: DOF of the kinematic chain
        """
        ...

    def init(self, iCub: ANNiCub_wrapper, name: str, part: str, version: float, ini_path: str = ...) -> bool:
        """Initialize the Kinematic Writer with given parameters.

        Args:
            iCub (ANNiCub_wrapper): main interface wrapper
            name (str): individual name for the kinematic reader
            part (str): string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso}
            version (float): version of the robot hardware
            ini_path (str, optional): path to the interface ini-file. Defaults to "../data/".

        Returns:
            bool: return True/False, indicating success/failure
        """
        ...

    def init_grpc(self, iCub: ANNiCub_wrapper, name: str, part: str, version: float, ini_path: str = ..., ip_address: str = ..., port: int = ...) -> bool:
        """Initialize the Kinematic Writer with given parameters, including the gRPC based connection.

        Args:
            iCub (ANNiCub_wrapper): main interface wrapper
            name (str): individual name for the kinematic reader
            part (str): string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso}
            version (float): version of the robot hardware
            ini_path (str, optional): path to the interface ini-file. Defaults to "../data/".
            ip_address (str, optional): gRPC server ip address. Defaults to "0.0.0.0".
            port (unsigned int, optional): gRPC server port. Defaults to 50000.

        Returns:
            bool: return True/False, indicating success/failure
        """
        ...

    def solve_InvKin(self, position, blocked_links) -> ndarray:
        """Compute the joint configuration for a given 3D End-Effector position (Inverse Kinematics).

        Args:
            position (list): target cartesian position for the end-effector/hand
            blocked_links (list): links of the kinematic chain, which should be blocked for inverse kinematic

        Returns:
            NDarray: active joint positions (in radians)
        """
        ...
