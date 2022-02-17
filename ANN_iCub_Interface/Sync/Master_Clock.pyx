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
import time

class MasterClock(object):
    def __init__(self):
        self.instances = []

    def add(self, instance):
        self.instances.append(instance)

    def update(self, T):
        start = time.time()

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
    def __init__(self):
        self.input = True

    def sync_input(self):
        print("For each Sync-class the 'sync_input' method has to be implemented or input has to be set to 'False'!")
        raise NotImplementedError

    def update(self, T):
        print("For each Sync-class the 'update' method has to be implemented!")
        raise NotImplementedError


if __name__ == '__main__':
    ## user has to implement these classes
    class ANNInterface(ClockInterface):
        def __init__(self, network):
            self.net = network
            pass
        def update(self, T):
            # simulate
            print(self.net, T)
            pass

    class iCubInterface(ClockInterface):
        def __init__(self, interface):
            self.iCub = interface
            pass
        def update(self, T):
            # start action -> small enough for timestep
            print(self.iCub, T)
            pass

    mc = MasterClock()
    ANNnet = "TEST ANNarchy"
    ann_clock = ANNInterface(ANNnet)
    iCub = "TEST iCub"
    icub_clock = iCubInterface(iCub)
    mc.add(ann_clock)
    mc.add(icub_clock)
    for i in range(20):
        print("read sensors")
        mc.update(i) #(bearbeitet)
        print("post sync")
