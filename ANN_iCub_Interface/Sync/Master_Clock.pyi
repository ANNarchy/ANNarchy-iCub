from typing import NoReturn, Any


class ClockInterface:
    """
        Base-Class for synchronisation parts. A subclass need to be implemented for each part (e.g. iCub interaction; ANNarchy simulation)
    """
    def __init__(self, *args, **kwargs) -> None: ...

    def sync_input(self, *args, **kwargs) -> NoReturn:
        """
        Need to be implemented. Should contain necessary input retrieval.

        Raises
        ------
        NotImplementedError
            Raises NotImplementedError as default. Need to be overwritten in the actual implementation.
        """
        ...

    def update(self, *args, **kwargs) -> NoReturn:
        """
        Need to be implemented. Should contain necessary update steps -> e.g. ANNarchy simulation.

        Parameters
        ----------
        T : int
            number of timesteps for the update -> e.g. simulation time for ANNarchy

        Raises
        ------
        NotImplementedError
            Raises NotImplementedError as default. Need to be overwritten in the actual implementation.
        """
        ...


class MasterClock:
    """
        Main Class for synchronisation, needs to be instantiated only once.
    """
    def __init__(self, *args, **kwargs) -> None: ...

    def add(self, *args, **kwargs) -> Any:
        """
        Add instance of class inherited from "ClockInterface" for synchronisation.

        Parameters
        ----------
        instance : sublass of ClockInterface
            Class instance which is derived from ClockInterface (need to be implemented serperately).

        Raises
        ------
        TypeError
            Raises TypeError, if instances is not a sublass of ClockInterface.
        """
        ...

    def update(self, *args, **kwargs) -> NoReturn:
        """
        Perform an update for each registered instance in parallel. Contains an input retrieval step and the actual update.

        Parameters
        ----------
        T : int
            number of timesteps for the update -> e.g. simulation time for ANNarchy
        """
        ...
