# cython: language_level = 3
"""
######  Dec   CEST 2020

@author: Torsten Fietzek


"""
import multiprocessing as mp
import time

class MasterClock(object):
    def __init__(self):
        self.instances = []
        mp.set_start_method('spawn')

    def add(self, instance):
        self.instances.append(instance)
    def update(self, T):
        start = time.time()
        processes = []
        for inst in self.instances:
            processes.append(mp.Process(target=inst.update, args=(T)))
            processes[-1].start()
        
        for proc in processes:
            proc.join()

        print("Duration:", (time.time()-start))

class ClockInterface(object):
    def __init__(self):
        pass

    def update(self, T):
        print("For each class the 'update' method has to be implemented!")
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
