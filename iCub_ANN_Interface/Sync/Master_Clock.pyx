# distutils: language = c++
# cython: language_level = 3

"""
######  Dec   CEST 2020

@author: Torsten Fietzek; Helge Ülo Dinkelbach

   Master_Clock.pyx is part of the iCub ANNarchy interface

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   The iCub ANNarchy interface is distributed in the hope that it will be useful,
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
        # mp.set_start_method('fork')

    def add(self, instance):
        self.instances.append(instance)

    def update(self, T):
        start = time.time()
        processes = []
        for i, inst in enumerate(self.instances):
            processes.append(mp.Thread(name="instance_"+str(i), target=inst.update, args=(T,)))
            processes[-1].start()

        for proc in processes:
            proc.join()

        print("Duration:", (time.time()-start))

class ClockInterface(object):
    def __init__(self):
        pass

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
        def updated(self, T):
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
