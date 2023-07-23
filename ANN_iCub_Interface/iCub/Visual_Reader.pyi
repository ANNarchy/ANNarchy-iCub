from typing import NoReturn
from numpy import ndarray
from .iCub_Interface import ANNiCub_wrapper


class PyVisualReader:
    """ """
    @classmethod
    def __init__(cls, *args, **kwargs) -> None: ...

    def close(self, iCub: ANNiCub_wrapper) -> NoReturn:
        """Close the visual reader module

        Parameters
        ----------
        iCub : ANNiCub_wrapper
            main interface wrapper

        Returns
        -------

        """
        ...

    def init(self, iCub: ANNiCub_wrapper, name: str, eye: str, fov_width: float = ..., fov_height: float = ...,
             img_width: int = ..., img_height: int = ..., fast_filter=..., ini_path: str = ...) -> bool:
        """Initialize Visual reader with given parameters.

        Parameters
        ----------
        iCub : ANNiCub_wrapper
            main interface wrapper
        name : str
            name for the visual reader module
        eye : str
            character representing the selected eye (l/L; r/R; b/B)
        fov_width : double
            output field of view width in degree [0, 60] (input fov width: 60°). (Default value = 60)
        fov_height : double
            output field of view height in degree [0, 48] (input fov height: 48°). (Default value = 48)
        img_width : int
            output image width in pixel (input width: 320px). (Default value = 320)
        img_height : int
            output image height in pixel (input height: 240px). (Default value = 240)
        fast_filter : bool
            flag to select the filter for image upscaling; True for a faster filter. (Default value = True)
        ini_path : str
            Path to the "interface_param.ini"-file. (Default value = "../data/")

        Returns
        -------
        bool
            return True/False, indicating success/failure
        """
        ...

    def init_grpc(self, iCub: ANNiCub_wrapper, name: str, eye: str, fov_width: float = ..., fov_height: float = ..., img_width: int = ...,
                  img_height: int = ..., fast_filter=..., ini_path: str = ..., ip_address: str = ..., port: int = ...) -> bool:
        """Initialize the visual reader with given parameters, including the gRPC based connection.

        Parameters
        ----------
        ANNiCub_wrapperiCub : _type_
            main interface wrapper
        name : str
            name for the visual reader module
        eye : str
            character representing the selected eye (l/L; r/R; b/B)
        fov_width : double
            output field of view width in degree [0, 60] (input fov width: 60°). (Default value = 60)
        fov_height : double
            output field of view height in degree [0, 48] (input fov height: 48°). (Default value = 48)
        img_width : int
            output image width in pixel (input width: 320px). (Default value = 320)
        img_height : int
            output image height in pixel (input height: 240px). (Default value = 240)
        fast_filter : bool
            flag to select the filter for image upscaling; True for a faster filter. (Default value = True)
        ini_path : str
            Path to the "interface_param.ini"-file. (Default value = "../data/")
        strip_address : str
            gRPC server ip address. (Default value = "0.0.0.0")
        unsignedintport : int
            gRPC server port. (Default value = 50000)

        Returns
        -------
        bool
            return True/False, indicating success/failure
        """
        ...

    def read_robot_eyes(self) -> ndarray:
        """Return image_s from the iCub camera_s. The return type depends on the selected precision (float/double).

        Parameters
        ----------

        Returns
        -------
        type
            NDarray (vector[vector[precision]]): image_s from the camera_s in the form vector of image_s and as flattened image
        """
        ...

    def retrieve_robot_eye(self) -> ndarray:
        """Return RGB-image from one of the iCub cameras. Does not work in 'B' mode.

        Parameters
        ----------

        Returns
        -------
        type
            NDarrray (vector[int]): RGB-camera image flattened
        """
        ...
