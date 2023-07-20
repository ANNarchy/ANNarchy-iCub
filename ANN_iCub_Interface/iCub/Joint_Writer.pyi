from typing import NoReturn
from numpy import ndarray
from .iCub_Interface import ANNiCub_wrapper


class PyJointWriter:
    @classmethod
    def __init__(cls, *args, **kwargs) -> None: ...

    def close(self, iCub: ANNiCub_wrapper) -> NoReturn:
        """Close joint writer with cleanup

        Args:
            iCub (ANNiCub_wrapper): main interface wrapper
        """
        ...

    def get_joint_count(self) -> int:
        """Return number of controlled joints

        Returns:
            int: return number of joints being controlled by the joint writer
        """
        ...

    def get_joint_limits(self) -> ndarray:
        """Return the limits of joint angles in degree

        Returns:
            NDarray (vector[vector[double]]): return array, containing the limits of joint angles in degree (joint, (max, min))
        """
        ...

    def get_joint_limits_max(self) -> ndarray:
        """Return the upper limits of joint angles in degree

        Returns:
            NDarray (vector[double]): return vector, containing the upper limits of joint angles in degree (joint, max)
        """
        ...

    def get_joint_limits_min(self) -> ndarray:
        """Return the lower limits of joint angles in degree

        Returns:
            NDarray (vector[double]): return vector, containing the lower limits of joint angles in degree (joint, min)
        """
        ...

    def get_joints_deg_res(self) -> ndarray:
        """Return the resolution in degree of the populations encoding the joint angles

        Returns:
            NDarray (vetor[double]): return vector, containing the resolution for every joints population codimg in degree
        """
        ...

    def get_neurons_per_joint(self) -> ndarray:
        """Return the size of the populations encoding the joint angles

        Returns:
            NDarray (vector[int]): return vector, containing the population size for every joint
        """
        ...

    def init(self, iCub: ANNiCub_wrapper, name: str, part: str, n_pop: int, degr_per_neuron: float = ..., speed: float = ..., ini_path: str = ...) -> bool:
        """Initialize the joint writer with given parameters.

        Args:
            iCub (ANNiCub_wrapper): main interface wrapper
            name (str): name for the joint writer module
            part (str): string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso}
            n_pop (unsigned int): number of neurons per population, encoding each one joint angle;
                                  only works if parameter "deg_per_neuron" is not set
            degr_per_neuron (double, optional): degree per neuron in the populationencoding the joints angles;
                                                if set: population size depends on joint working range. Defaults to 0.0.
            speed (double, optional): velocity for the joint movements. Defaults to 10.0.
            ini_path (str, optional): Path to the "interface_param.ini"-file. Defaults to "../data/".

        Returns:
            bool: return True/False, indicating success/failure
        """
        ...

    def init_grpc(self, iCub: ANNiCub_wrapper, name: str, part: str, n_pop: int, joints, mode: str, blocking=..., degr_per_neuron: float = ..., speed: float = ..., 
                  ini_path: str = ..., ip_address: str = ..., port: int = ...) -> bool:
        """Initialize the joint writer with given parameters, including the gRPC based connection.

        Args:
            iCub (ANNiCub_wrapper): main interface wrapper
            name (str): name for the joint writer module
            part (str): string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso}
            n_pop (unsigned int): number of neurons per population, encoding each one joint angle;
                                  only works if parameter "deg_per_neuron" is not set
            joints (list (vector[int])): joint selection for grpc -> empty vector for all joints
            mode (str): mode for writing joints:
                            - 'abs' for absolute joint angle positions
                            - 'rel' for relative joint angles
                            - 'vel' for velocity values -> DO NOT USE "VEL" AS BLOCKING MOTION!!!
            blocking (bool, optional): if True, complete motion before continuation. Defaults to True.
            degr_per_neuron (double, optional): degree per neuron in the populationencoding the joints angles;
                                                if set: population size depends on joint working range. Defaults to 0.0.
            speed (double, optional): velocity for the joint movements. Defaults to 10.0.
            ini_path (str, optional): Path to the "interface_param.ini"-file. Defaults to "../data/".
            ip_address (str, optional): gRPC server ip address. Defaults to "0.0.0.0".
            port (unsigned int, optional): gRPC server port. Defaults to 50010.

        Returns:
            bool: return True/False, indicating success/failure
        """
        ...

    def retrieve_ANNarchy_input_all(self) -> NoReturn:
        """Retrieve all joint angles from specialized gRPC-connected ANNarchy-JointControl-Population."""
        ...

    def retrieve_ANNarchy_input_all_enc(self) -> NoReturn:
        """Retrieve all population encoded joint angles from specialized gRPC-connected ANNarchy-JointControl-Population."""
        ...

    def retrieve_ANNarchy_input_multi(self) -> NoReturn:
        """Retrieve multiple joint angles from specialized gRPC-connected ANNarchy-JointControl-Population."""
        ...

    def retrieve_ANNarchy_input_multi_enc(self) -> NoReturn:
        """Retrieve multiple population encoded joint angles from specialized gRPC-connected ANNarchy-JointControl-Population."""
        ...

    def retrieve_ANNarchy_input_single(self) -> NoReturn:
        """Retrieve single joint angle from specialized gRPC-connected ANNarchy-JointControl-Population."""
        ...

    def retrieve_ANNarchy_input_single_enc(self) -> NoReturn:
        """Retrieve single population encoded joint angle from specialized gRPC-connected ANNarchy-JointControl-Population."""
        ...

    def set_joint_acceleration(self, acc: float, joint: int = ...) -> bool:
        """Set joint acceleration.

        Args:
            acc (double): acceleration value to be set
            joint (int, optional): joint number of the robot part or -1 for all joints. Defaults to -1.

        Returns:
            bool: return True/False, indicating success/failure
        """
        ...

    def set_joint_controlmode(self, control_mode: str, joint: int = ...) -> bool:
        """Set joint control mode

        Args:
            control_mode (str): control mode for the joint. currently implemented are: "velocity" and "position"
            joint (int, optional): joint number of the robot part or -1 for all joints. Defaults to -1.

        Returns:
            bool: return True/False, indicating success/failure
        """
        ...

    def set_joint_velocity(self, speed: float, joint: int = ...) -> bool:
        """Set joint velocity.

        Args:
            speed (double): velocity value to be set
            joint (int, optional): joint number of the robot part or -1 for all joints. Defaults to -1.

        Returns:
            bool: return True/False, indicating success/failure
        """
        ...

    def write_ANNarchy_input_all(self) -> NoReturn:
        """Write all joints with retrieved joint angles."""
        ...

    def write_ANNarchy_input_all_enc(self) -> NoReturn:
        """Write all joints with retrieved population encoded joint angles."""
        ...

    def write_ANNarchy_input_multi(self) -> NoReturn:
        """Write multiple joints with retrieved joint angles."""
        ...

    def write_ANNarchy_input_multi_enc(self) -> NoReturn:
        """Write multiple joints with retrieved population encoded joint angles."""
        ...

    def write_ANNarchy_input_single(self) -> NoReturn:
        """Write single joint with retrieved joint angle."""
        ...

    def write_ANNarchy_input_single_enc(self) -> NoReturn:
        """Write single joint with retrieved population encoded joint angle."""
        ...

    def write_double_all(self, position, mode: str, blocking=...) -> bool:
        """Move all joints to the given positiion (joint angles/velocities).

        Args:
            position (list/NDarray (vector[double])): joint angles/velocities to write to the robot joints
            mode (str): string to select the motion mode: 'abs' for absolute joint angle positions; 'rel' for relative joint angles; 'vel' for velocity values: DO NOT USE "VEL" AS BLOCKING MOTION!!!
            blocking (bool, optional): if True, complete motion before continuation. Defaults to True.

        Returns:
            bool: return True/False, indicating success/failure
        """
        ...

    def write_double_multiple(self, position, joints, mode: str, blocking=...) -> bool:
        """Move multiple joints to the given positiion (joint angles/velocities).

        Args:
            position (list/NDarray (vector[double])): joint angles/velocities to write to the robot joints
            joints (list/NDarray (vector[int])): joint indizes of the joints, which should be moved (e.g. head: [3, 4, 5] -> all eye movements)
            mode (str): string to select the motion mode: 'abs' for absolute joint angle positions; 'rel' for relative joint angles; 'vel' for velocity values: DO NOT USE "VEL" AS BLOCKING MOTION!!!
            blocking (bool, optional): if True, complete motion before continuation. Defaults to True.

        Returns:
            bool: return True/False, indicating success/failure
        """
        ...

    def write_double_one(self, position: float, joint: int, mode: str, blocking=...) -> bool:
        """Move single joint to the given positiion (joint angle/velocity).

        Args:
            position (double): joint angle/velocity to write to the robot joint
            joint (int): joint number of the robot part
            mode (str): string to select the motion mode: 'abs' for absolute joint angle positions; 'rel' for relative joint angles; 'vel' for velocity values: DO NOT USE "VEL" AS BLOCKING MOTION!!!
            blocking (bool, optional): if True, complete motion before continuation. Defaults to True.

        Returns:
            bool: return True/False, indicating success/failure
        """
        ...

    def write_pop_all(self, position_pops, mode: str, blocking=...) -> bool:
        """Move all joints to the joint angles/velocities encoded in the given vector of populations.

        Args:
            position_pops (NDarray (vector[vector[double]])): vector of populations, each encoding the angle/velocity for a single joint
            mode (str): string to select the motion mode: 'abs' for absolute joint angle positions; 'rel' for relative joint angles; 'vel' for velocity values: DO NOT USE "VEL" AS BLOCKING MOTION!!!
            blocking (bool, optional): if True, complete motion before continuation. Defaults to True.

        Returns:
            bool: return True/False, indicating success/failure
        """
        ...

    def write_pop_multiple(self, position_pops, joints, mode: str, blocking=...) -> bool:
        """Move multiple joints to the joint angles/velocities encoded in the given vector of populations.

        Args:
            position_pops (NDarray (vector[vector[double]])): vector of populations, each encoding the angle/velocity for a single joint
            joints (list/NDarray (vector[int])): Joint indizes of the joints, which should be moved (head: [3, 4, 5] -> all eye movements)
            mode (str): string to select the motion mode: 'abs' for absolute joint angle positions; 'rel' for relative joint angles; 'vel' for velocity values: DO NOT USE "VEL" AS BLOCKING MOTION!!!
            blocking (bool, optional): if True, complete motion before continuation. Defaults to True.

        Returns:
            bool: return True/False, indicating success/failure
        """
        ...

    def write_pop_one(self, position_pop, joint: int, mode: str, blocking=...) -> bool:
        """Move a single joint to the joint angle/velocity encoded in the given population.

        Args:
            position_pop (NDarray (vector[double])): population encoding the joint angle/velocity
            joint (int): joint number of the robot part
            mode (str): string to select the motion mode: 'abs' for absolute joint angle positions; 'rel' for relative joint angles; 'vel' for velocity values: DO NOT USE "VEL" AS BLOCKING MOTION!!!
            blocking (bool, optional): if True, complete motion before continuation. Defaults to True.

        Returns:
            bool: return True/False, indicating success/failure
        """
        ...
