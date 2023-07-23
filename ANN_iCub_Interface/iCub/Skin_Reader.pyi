from typing import NoReturn
from numpy import ndarray
from .iCub_Interface import ANNiCub_wrapper


class PySkinReader:
    """ """
    @classmethod
    def __init__(cls, *args, **kwargs) -> None: ...

    def close(self, iCub: ANNiCub_wrapper) -> NoReturn:
        """Close and clean skin reader.

        Parameters
        ----------
        iCub : ANNiCub_wrapper
            main interface wrapper

        Returns
        -------

        """
        ...

    def get_tactile_arm(self) -> ndarray:
        """Return tactile data for the upper arm skin.

        Parameters
        ----------

        Returns
        -------
        type
            NDarray (vector[vector[double]]): tactile data of the arm part of the skin, values: non-normalized: 0..255 ; normalized: 0..1.0
        """
        ...

    def get_tactile_arm_size(self) -> int:
        """Return size of tactile data for the upper arm skin.

        Parameters
        ----------

        Returns
        -------
        type
            unsigned int: size of sensor data vector -> upper arm section
        """
        ...

    def get_tactile_forearm(self) -> ndarray:
        """Return tactile data for the forearm skin.

        Parameters
        ----------

        Returns
        -------
        type
            NDarray (vector[vector[double]]): tactile data of the forearm part of the skin, values: non-normalized: 0..255 ; normalized: 0..1.0
        """
        ...

    def get_tactile_forearm_size(self) -> int:
        """Return size of tactile data for the forearm skin

        Parameters
        ----------

        Returns
        -------
        type
            unsigned int: size of sensor data vector -> forearm section
        """
        ...

    def get_tactile_hand(self) -> ndarray:
        """Return tactile data for the hand skin.

        Parameters
        ----------

        Returns
        -------
        type
            NDarray (vector[vector[double]]): tactile data of the hand part of the skin, values: non-normalized: 0..255 ; normalized: 0..1.0
        """
        ...

    def get_tactile_hand_size(self) -> int:
        """Return size of tactile data for the hand skin.

        Parameters
        ----------

        Returns
        -------
        type
            unsigned int: size of sensor data vector -> hand section
        """
        ...

    def get_taxel_pos(self, skin_part: str) -> ndarray:
        """Return the taxel positions given by the ini files from the icub-main repo.

        Parameters
        ----------
        skin_part: str :
            skin part to load the data for ("arm", "forearm", "hand")

        Returns
        -------
        type
            NDarray (vector[vector[double]]): Vector containing taxel positions -> reference frame depending on skin part
        """
        ...

    def init(self, iCub: ANNiCub_wrapper, name: str, arm: str, norm=..., ini_path: str = ...) -> bool:
        """Initialize skin reader with given parameters.

        Parameters
        ----------
        iCub : ANNiCub_wrapper
            main interface wrapper
        name : str
            individual name for the skin reader module
        arm : str
            character to choose the arm side (r/R for right; l/L for left)
        norm : bool
            if true, the sensor data are returned normalized (iCub [0..255]; normalized [0..1]). (Default value = True)
        ini_path : str
            Path to the "interface_param.ini"-file. (Default value = "../data/")

        Returns
        -------
        bool
            return True/False, indicating success/failure
        """
        ...

    def init_grpc(self, iCub: ANNiCub_wrapper, name: str, arm: str, norm=..., ini_path: str = ..., ip_address: str = ..., port: int = ...) -> bool:
        """Initialize the skin reader with given parameters, including the gRPC based connection.

        Parameters
        ----------
        iCub : ANNiCub_wrapper
            main interface wrapper
        name : str
            individual name for the skin reader module
        arm : str
            character to choose the arm side (r/R for right; l/L for left)
        norm : bool
            if true, the sensor data are returned normalized (iCub [0..255]; normalized [0..1]). (Default value = True)
        ini_path : str
            Path to the "interface_param.ini"-file. (Default value = "../data/")
        ip_address : str
            gRPC server ip address. (Default value = "0.0.0.0")
        port : unsigned int
            gRPC server port. (Default value = 50015)
        iCub: ANNiCub_wrapper :

        Returns
        -------
        bool
            return True/False, indicating success/failure
        """
        ...

    def read_skin_arm(self) -> ndarray:
        """Read tactile data for upper arm skin.

        Parameters
        ----------

        Returns
        -------
        NDarray : vector[double]
            tactile data of the arm part of the skin, values: non-normalized: 0..255 ; normalized: 0..1.0
        """
        ...

    def read_skin_forearm(self) -> ndarray:
        """Read tactile data for forearm skin.

        Parameters
        ----------

        Returns
        -------
        NDarray : vector[double]
            tactile data of the forearm part of the skin, values: non-normalized: 0..255 ; normalized: 0..1.0
        """
        ...

    def read_skin_hand(self) -> ndarray:
        """Read tactile data for hand skin.

        Parameters
        ----------

        Returns
        -------
        NDarray : vector[double]
            tactile data of the hand part of the skin, values: non-normalized: 0..255 ; normalized: 0..1.0
        """
        ...

    def read_tactile(self) -> bool:
        """Read sensor data for one step

        Parameters
        ----------

        Returns
        -------
        bool
            return True/False, indicating success/failure
        """
        ...
