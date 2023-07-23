from typing import Any, NoReturn
from numpy import ndarray
from .iCub_Interface import ANNiCub_wrapper


class PyKinematicWriter:
    """ """
    @classmethod
    def __init__(cls, *args, **kwargs) -> None: ...

    def close(self, iCub: ANNiCub_wrapper) -> NoReturn:
        """Close the module.

        Parameters
        ----------
        iCub : ANNiCub_wrapper
            main interface wrapper

        Returns
        -------

        """
        ...

    def get_DOF(self) -> int:
        """Return the DOF of the kinematic chain.

        Parameters
        ----------

        Returns
        -------
        type
            int: DOF of the kinematic chain
        """
        ...

    def init(self, iCub: ANNiCub_wrapper, name: str, part: str, version: float, ini_path: str = ...) -> bool:
        """Initialize the Kinematic Writer with given parameters.

        Parameters
        ----------
        iCub : ANNiCub_wrapper
            main interface wrapper
        name : str
            individual name for the kinematic reader
        part : str
            string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso}
        version : float
            version of the robot hardware
        ini_path : str
            path to the interface ini-file. (Default value = "../data/")

        Returns
        -------
        bool
            return True/False, indicating success/failure
        """
        ...

    def init_grpc(self, iCub: ANNiCub_wrapper, name: str, part: str, version: float, ini_path: str = ..., ip_address: str = ..., port: int = ...) -> bool:
        """Initialize the Kinematic Writer with given parameters, including the gRPC based connection.

        Parameters
        ----------
        iCub : ANNiCub_wrapper
            main interface wrapper
        name : str
            individual name for the kinematic reader
        part : str
            string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso}
        version : float
            version of the robot hardware
        ini_path : str
            path to the interface ini-file. (Default value = "../data/")
        ip_address : str
            gRPC server ip address. (Default value = "0.0.0.0")
        port : unsigned int
            gRPC server port. (Default value = 50025)

        Returns
        -------
        bool
            return True/False, indicating success/failure
        """
        ...

    def solve_InvKin(self, position, blocked_links) -> ndarray:
        """Compute the joint configuration for a given 3D End-Effector position (Inverse Kinematics).

        Parameters
        ----------
        position : list
            target cartesian position for the end-effector/hand
        blocked_links : list
            links of the kinematic chain, which should be blocked for inverse kinematic

        Returns
        -------
        NDarray
            active joint positions (in radians)
        """
        ...
