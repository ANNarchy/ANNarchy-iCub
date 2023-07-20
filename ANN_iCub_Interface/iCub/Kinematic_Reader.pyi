from typing import Any, NoReturn
from numpy import ndarray
from .iCub_Interface import ANNiCub_wrapper


class PyKinematicReader:
    @classmethod
    def __init__(cls, *args, **kwargs) -> None: ...

    def block_links(self, blocked_joints) -> Any:
        """Block specific set of joints in the kinematic chain.

        Args:
            blocked_joints (list): joints that should be blocked
        """
        ...

    def close(self, iCub: ANNiCub_wrapper) -> NoReturn:
        """Close the module

        Args:
            iCub (ANNiCub_wrapper): main interface wrapper
        """
        ...

    def get_DOF(self) -> int:
        """Return the DOF of the kinematic chain

        Returns:
            int: degree of freedom (DOF) of the kinematic chain
        """
        ...

    def get_DOF_links(self) -> ndarray:
        """Get joints being part of active kinematic chain.

        Returns:
            NDarray: vector with the active joints
        """
        ...

    def get_blocked_links(self) -> ndarray:
        """Get blocked links.

        Returns:
            NDarray: vector containing the blocked links
        """
        ...

    def get_handposition(self) -> ndarray:
        """Get End-Effector cartesian position.

        Returns:
            NDarray: Cartesian position of the end-effector in robot reference frame
        """
        ...

    def get_jointangles(self) -> ndarray:
        """Get current joint angles of active kinematic chain -> radians.

        Returns:
            NDarray: joint angles in radians
        """
        ...

    def get_jointposition(self, joint: int) -> ndarray:
        """Get cartesian position for the given joint.

        Args:
            joint (unsigned int): joint number of the robot part

        Returns:
            NDarray: Cartesian position of the joint in robot reference frame
        """
        ...

    def init(self, iCub: ANNiCub_wrapper, name: str, part: str, version: float, ini_path: str = ..., offline_mode=...) -> bool:
        """Initialize the Kinematic Reader with given parameters

        Args:
            iCub (ANNiCub_wrapper): main interface wrapper
            name (str): individual name for the kinematic reader
            part (str): string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso}
            version (float): version of the robot hardware
            ini_path (str, optional): path to the interface ini-file. Defaults to "../data/".
            offline_mode (bool, optional): flag, if iCub network is offline. Defaults to False.

        Returns:
            bool: return True/False, indicating success/failure
        """
        ...

    def init_grpc(self, iCub: ANNiCub_wrapper, name: str, part: str, version: float, ini_path: str = ...,
                  ip_address: str = ..., port: int = ..., offline_mode=...) -> bool:
        """Initialize the Kinematic Reader with given parameters, including the gRPC based connection.

        Args:
            iCub (ANNiCub_wrapper): main interface wrapper
            name (str): individual name for the kinematic reader
            part (str): string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso}
            version (float): version of the robot hardware
            ini_path (str, optional): path to the interface ini-file. Defaults to "../data/".
            ip_address (str, optional): gRPC server ip address. Defaults to "0.0.0.0".
            port (unsigned int, optional): gRPC server port. Defaults to 50000.
            offline_mode (bool, optional): flag, if iCub network is offline. Defaults to False.

        Returns:
            bool: return True/False, indicating success/failure
        """
        ...

    def release_links(self, release_joints) -> Any:
        """Release links of kinematic chain

        Args:
            release_joints (list): joints that should be released
        """
        ...

    def set_jointangles(self, joint_angles) -> Any:
        """Set joint angles for forward kinematic in offline mode.

        Args:
            joint_angles (list/NDarray): joint angles
        """
        ...
