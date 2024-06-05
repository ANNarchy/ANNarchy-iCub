from typing import NoReturn, Tuple
from iCub.iCub_Interface import ANNiCub_wrapper


def create_robot_interface_file(filename_config: str, filename_interface: str = ...) -> NoReturn:
    """Create file with interface init code.

    Parameters
    ----------
    filename_config :
        filename of XML config file
    filename_interface :
        filename of created interface file (Default value = "./robot_interface.py")

    Returns
    -------

    """

def init_robot_from_file(iCub: ANNiCub_wrapper, xml_file: str) -> Tuple[bool, str]:
    """Init iCub interface with the modules given in the xml-file

    Parameters
    ----------
    iCub : ANNiCub_wrapper
        main interface wrapper
    xml_file : str
        filename of the xml-config-file

    Returns
    -------
    Tuple[bool, str]
        Returns a bool value representing the success of the init and a dicionary containing the module names for each module type
    """
    ...

def save_robot_to_file(iCub: ANNiCub_wrapper, xml_file: str, description: str = ...) -> NoReturn:
    """Save robot configuration to xml-config file

    Parameters
    ----------
    iCub : ANNiCub_wrapper
        main interface wrapper
    xml_file : str
        filename for the xml-config-file
    description : str
        optional description added as comment in the robot section. Defaults to "".

    Returns
    -------

    """
    ...
