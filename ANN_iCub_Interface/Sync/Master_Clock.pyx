# distutils: language = c++
# cython: language_level = 3

"""
   Copyright (C) 2020-2022 Torsten Fietzek; Helge Ülo Dinkelbach

   Master_Clock.pyx is part of the ANNarchy iCub interface

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   The ANNarchy iCub interface is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this headers. If not, see <http://www.gnu.org/licenses/>.
"""

import threading as mp


class MasterClock(object):
    """
        Main Class for synchronisation, needs to be instantiated only once.
    """
    def __init__(self):
        self.instances = []

    def add(self, instance):
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
        if isinstance(instance, ClockInterface):
            self.instances.append(instance)
        else:
            raise TypeError

    def update(self, T):
        """
        Perform an update for each registered instance in parallel. Contains an input retrieval step and the actual update.

        Parameters
        ----------
        T : int
            number of timesteps for the update -> e.g. simulation time for ANNarchy
        """
        input_proc = []
        for i, inst in enumerate(self.instances):
            if inst.input:
                input_proc.append(mp.Thread(name="inp_instance_"+str(i), target=inst.sync_input))
                input_proc[-1].start()

        for proc in input_proc:
            proc.join()

        processes = []
        for i, inst in enumerate(self.instances):
            processes.append(mp.Thread(name="instance_"+str(i), target=inst.update, args=(T,)))
            processes[-1].start()

        for proc in processes:
            proc.join()


class ClockInterface(object):
    """
        Base-Class for synchronisation parts. A subclass need to be implemented for each part (e.g. iCub interaction; ANNarchy simulation)
    """
    def __init__(self):
        self.input = True

    def sync_input(self):
        """
        Need to be implemented. Should contain necessary input retrieval.

        Raises
        ------
        NotImplementedError
            Raises NotImplementedError as default. Need to be overwritten in the actual implementation.
        """
        print("For each Sync-class the 'sync_input' method has to be implemented or input has to be set to 'False'!")
        raise NotImplementedError

    def update(self, T):
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
        print("For each Sync-class the 'update' method has to be implemented!")
        raise NotImplementedError
