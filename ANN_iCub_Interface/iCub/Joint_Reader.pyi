from typing import NoReturn
from numpy import ndarray
from .iCub_Interface import ANNiCub_wrapper


class PyJointReader:
    """ """
    @classmethod
    def __init__(cls, *args, **kwargs) -> None: ...

    def close(self, iCub: ANNiCub_wrapper) -> NoReturn:
        """Close joint reader with cleanup

        Parameters
        ----------
        iCub : ANNiCub_wrapper
            main interface wrapper

        Returns
        -------

        """
        ...

    def get_joint_count(self) -> int:
        """Return the number of controlled joints

        Parameters
        ----------

        Returns
        -------
        type
            int: return number of joints, being controlled by the reader
        """
        ...

    def get_joints_deg_res(self) -> ndarray:
        """Return the resolution in degree of the populations encoding the joint angles

        Parameters
        ----------

        Returns
        -------
        type
            NDarray (vector[double]): return vector, containing the resolution for every joints population coding in degree
        """
        ...

    def get_neurons_per_joint(self) -> ndarray:
        """Return the size of the populations encoding the joint angles

        Parameters
        ----------

        Returns
        -------
        type
            NDarray (vector[int]): return vector, containing the population size for every joint
        """
        ...

    def init(self, iCub: ANNiCub_wrapper, name: str, part: str, sigma: float,
             n_pop: int, degr_per_neuron: float = ..., ini_path: str = ...) -> bool:
        """Initialize the joint reader with given parameters.

        Parameters
        ----------
        iCub : ANNiCub_wrapper
            main interface wrapper
        name : str
            name for the joint reader module
        part : str
            string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso}
        sigma : double
            sigma for the joints angles populations coding
        n_pop : unsigned int
            number of neurons per population, encoding each one joint angle only works if parameter "deg_per_neuron" is not set
        degr_per_neuron : double
            degree per neuron in the populations, encoding the joints angles
            if set: population size depends on joint working range. (Default value = 0.0)
        ini_path : str
            Path to the "interface_param.ini"-file. (Default value = "../data/")

        Returns
        -------
        bool
            return True, if successful

        """
        ...

    def init_grpc(self, iCub: ANNiCub_wrapper, name: str, part: str, sigma: float, n_pop: int,
                  degr_per_neuron: float = ..., ini_path: str = ..., ip_address: str = ..., port: int = ...) -> bool:
        """Initialize the joint reader with given parameters, including the gRPC based connection.

        Parameters
        ----------
        iCub : ANNiCub_wrapper
            main interface wrapper
        name : str
            name for the joint reader module
        part : str
            string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso}
        sigma : double
            sigma for the joints angles populations coding
        n_pop : unsigned int
            number of neurons per population, encoding each one joint angle only works if parameter "deg_per_neuron" is not set
        degr_per_neuron : double
            degree per neuron in the populations, encoding the joints angles
            if set: population size depends on joint working range. (Default value = 0.0)
        ini_path : str
            Path to the "interface_param.ini"-file. (Default value = "../data/")
        ip_address : str
            gRPC server ip address. (Default value = "0.0.0.0")
        port : unsigned int
            gRPC server port. (Default value = 50005)

        Returns
        -------
        bool
            return True, if successful

        """
        ...

    def read_double_all(self) -> ndarray:
        """Read all joints and return joint angles directly as double values

        Parameters
        ----------

        Returns
        -------
        NDarray : vector[double]
            joint angles read from the robot; empty vector at error
        """
        ...

    def read_double_multiple(self, joints) -> ndarray:
        """Read multiple joints and return joint angles directly as double value.

        Parameters
        ----------
        joints : list (vector[int]
            joint numbers of the robot part

        Returns
        -------
        NDarray : vector[double]
            joint angle read from the robot; empty vector at error
        """
        ...

    def read_double_one(self, joint: int) -> ndarray:
        """Read one joint and return joint angle directly as double value.

        Parameters
        ----------
        joint : int
            joint number of the robot part

        Returns
        -------
        double
            joint angle read from the robot; NAN at error
        """
        ...

    def read_pop_all(self) -> ndarray:
        """Read all joints and return the joint angles encoded in vectors (population coding)

        Parameters
        ----------

        Returns
        -------
        NDarray : vector[vector[double]]
            population vectors encoding every joint angle from associated robot part
        """
        ...

    def read_pop_multiple(self, joints) -> ndarray:
        """Read multiple joints and return the joint angles encoded in vectors (population coding).

        Parameters
        ----------
        joints : list (vector[int]
            joint numbers of the robot part

        Returns
        -------
        NDarray : vector[vector[double]]
            population vectors encoding selected joint angles from associated robot part
        """
        ...

    def read_pop_one(self, joint: int) -> ndarray:
        """Read one joint and return the joint angle encoded in a vector (population coding).

        Parameters
        ----------
        joint : int
            joint number of the robot part

        Returns
        -------
        NDarray : vector[double]
            population vector encoding the joint angle
        """
        ...
