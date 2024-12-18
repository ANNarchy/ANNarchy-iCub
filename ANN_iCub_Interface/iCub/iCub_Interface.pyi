from typing import NoReturn, Tuple

from .Kinematic_Writer import PyKinematicWriter
from .Kinematic_Reader import PyKinematicReader
from .Visual_Reader import PyVisualReader
from .Skin_Reader import PySkinReader
from .Joint_Writer import PyJointWriter
from .Joint_Reader import PyJointReader


class ANNiCub_wrapper:
    """ """
    @classmethod
    def __init__(cls, *args, **kwargs) -> None: ...

    def clear(self) -> NoReturn:
        """Clean-up all initialized interface instances"""
        ...

    def get_jreader_by_name(self, name: str) -> PyJointReader:
        """Returns the Joint Reader instance with the given name.

        Parameters
        ----------
        name : str
            Name of the Joint Reader instance.

        Returns
        -------
        PyJointReader
            Joint Reader instance
        """
        ...

    def get_jreader_by_part(self, part: str) -> PyJointReader:
        """Returns the Joint Reader instance with the given part.

        Parameters
        ----------
        part : str
            The robot part which is controlled by the Joint Reader.

        Returns
        -------
        PyJointReader
            Joint Reader instance
        """
        ...

    def get_jwriter_by_name(self, name: str) -> PyJointWriter:
        """Returns the Joint Writer instance with the given name.

        Parameters
        ----------
        name : str
            Name of the Joint Writer instance.

        Returns
        -------
        PyJointWriter
            Joint Writer instance
        """
        ...

    def get_jwriter_by_part(self, part: str) -> PyJointWriter:
        """Returns the Joint Writer instance with the given part.

        Parameters
        ----------
        part : str
            The robot part which is controlled by the Joint Writer.

        Returns
        -------
        PyJointWriter
            Joint Writer instance
        """
        ...

    def get_skinreader_by_name(self, name: str) -> PySkinReader:
        """Returns the Skin Reader instance with the given name.

        Parameters
        ----------
        name : str
            Name of the Skin Reader instance.

        Returns
        -------
        PySkinReader
            Skin Reader instance
        """
        ...

    def get_vis_reader_by_name(self, name: str) -> PyVisualReader:
        """Returns the Visual Reader instance with the given name.

        Parameters
        ----------
        name : str
            Name of the Visual Reader instance.

        Returns
        -------
        PyVisualReader
            Visual Reader instance
        """
        ...

    def get_kin_reader_by_name(self, name: str) -> PyKinematicReader:
        """Returns the Kinematic Reader instance with the given name.

        Parameters
        ----------
        name : str
            Name of the Kinematic Reader instance.

        Returns
        -------
        PyKinematicReader
            Kinematic Reader instance
        """
        ...

    def get_kin_writer_by_name(self, name: str) -> PyKinematicWriter:
        """Returns the Kinematic Writer instance with the given name.

        Parameters
        ----------
        name : str
            Name of the Kinematic Writer instance.

        Returns
        -------
        PyKinematicWriter
            Kinematic Writer instance
        """
        ...


    def init_robot_from_file(self, xml_file: str) -> Tuple[bool, str]:
        """Init iCub interface with the modules given in the xml-file

        Parameters
        ----------
        xml_file : str
            filename of the xml-config-file

        Returns
        -------
        Tuple[bool, str]
            Returns a bool value representing the success of the init and a dicionary containing the module names for each module type
        """
        ...

    def save_robot_to_file(self, xml_file: str, description: str = ...) -> NoReturn:
        """Save robot configuration to xml-config file

        Parameters
        ----------
        xml_file : str
            filename for the xml-config-file
        description : str
            optional description added as comment in the robot section. Defaults to "".

        Returns
        -------

        """
        ...
