from typing import Any, NoReturn
from numpy import ndarray
from .iCub_Interface import ANNiCub_wrapper


class PyKinematicWriter:
    """ """
    @classmethod
    def __init__(cls, *args, **kwargs) -> None: ...

    def block_links(self, blocked_joints) -> Any:
        """Block specific set of joints in the kinematic chain.

        Parameters
        ----------
        blocked_joints : list
            joints that should be blocked

        Returns
        -------

        """
        ...

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

    def get_DOF_links(self) -> ndarray:
        """Get joints being part of active kinematic chain.

        Parameters
        ----------

        Returns
        -------
        NDarray
            vector with the active joints
        """
        ...

    def get_blocked_links(self) -> ndarray:
        """Get blocked links.

        Parameters
        ----------

        Returns
        -------
        NDarray
            vector containing the blocked links
        """
        ...

    def get_jointangles(self) -> ndarray:
        """Get current joint angles of active kinematic chain -> radians.

        Parameters
        ----------

        Returns
        -------
        NDarray
            joint angles in radians
        """
        ...

    def init(self, iCub: ANNiCub_wrapper, name: str, part: str, version: float, ini_path: str = ..., offline_mode=...) -> bool:
        """Initialize the Kinematic Writer with given parameters.

        Parameters
        ----------
        iCub : ANNiCub_wrapper
            main interface wrapper
        name : str
            individual name for the kinematic writer
        part : str
            string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso}
        version : float
            version of the robot hardware
        ini_path : str
            path to the interface ini-file. (Default value = "../data/")
        offline_mode : bool
            flag, if iCub network is offline. (Default value = False)

        Returns
        -------
        bool
            return True/False, indicating success/failure
        """
        ...

    def init_grpc(self, iCub: ANNiCub_wrapper, name: str, part: str, version: float, ini_path: str = ..., ip_address: str = ..., port: int = ..., offline_mode=...) -> bool:
        """Initialize the Kinematic Writer with given parameters, including the gRPC based connection.

        Parameters
        ----------
        iCub : ANNiCub_wrapper
            main interface wrapper
        name : str
            individual name for the kinematic writer
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
        offline_mode : bool
            flag, if iCub network is offline. (Default value = False)

        Returns
        -------
        bool
            return True/False, indicating success/failure
        """
        ...

    def release_links(self, release_joints) -> Any:
        """Release links of kinematic chain

        Parameters
        ----------
        release_joints : list
            joints that should be released

        Returns
        -------

        """
        ...

    def set_jointangles(self, joint_angles) -> ndarray:
        """Set joint angles for inverse kinematic in offline mode.

        Parameters
        ----------
        joint_angles : list/NDarray
            joint angles

        Returns
        -------
        NDarray
            actual set joint angles in radians -> evaluted constraints
        """
        ...

    def solve_InvKin(self, position, blocked_links=...) -> ndarray:
        """Compute the joint configuration for a given 3D End-Effector position (Inverse Kinematics).

        Parameters
        ----------
        position : list
            target cartesian position for the end-effector/hand
        blocked_links : list
            links of the kinematic chain, which should be blocked for inverse kinematic in online mode (Default value = [])
            IGNORED in offline mode -> use setter for block links and joint angles

        Returns
        -------
        NDarray
            active joint positions (in radians)
        """
        ...
