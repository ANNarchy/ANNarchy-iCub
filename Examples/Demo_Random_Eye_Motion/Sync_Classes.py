"""
 *  Copyright (C) 2021 Torsten Fietzek
 *
 *  Sync_Classes.py is part of the iCub ANNarchy interface
 *
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  The iCub ANNarchy interface is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this headers. If not, see <http://www.gnu.org/licenses/>.
"""

import sys
import time

import matplotlib.pylab as plt
import numpy as np
from iCub_ANN_Interface.Sync import Master_Clock

master = Master_Clock.MasterClock()

# Implementation of ClockInterface class for iCub interface
class iCubClock(Master_Clock.ClockInterface):
    def __init__(self, iCubInterface):
        self.input = True
        self.iCub = iCubInterface

    def sync_input(self):
        self.iCub.get_jwriter_by_part("head").retrieve_ANNarchy_input_multi()


    def update(self, T):
        self.iCub.get_jwriter_by_part("head").write_ANNarchy_input_multi()

# Implementation of ClockInterface class for ANNarchy network
class ANNarchyClock(Master_Clock.ClockInterface):
    def __init__(self, ANNnet):
        self.input = True
        self.net = ANNnet

    def sync_input(self):
        pass

    def update(self, T):
        self.net.simulate(T)
