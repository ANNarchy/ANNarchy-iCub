"""
Created on Thu Jul 9 20:05:53 CEST 2020

@author: tofo

auxilary methods for interface testing
"""

import numpy as np

# Test support files
from .joint_limits import joint_limits as j_lim


#################### auxilary methods ###################
def normal_pdf(value, mean, sigma):
    """
        Return the function value of a normal distribution for a given value.

        params:
            value           -- value to calculate normal distribution at
            mean            -- mean of the normal distribution
            sigma           -- sigma of the normal distribution

        return:
                            -- function value for the normal distribution
    """
    inv_sqrt_2pi = 1.0 / (sigma * np.sqrt(2 * np.pi))
    a = (value - mean) / sigma

    return inv_sqrt_2pi * np.exp(-0.5 * a * a)

def encode(part, joint, pop_size, joint_angle, sigma, resolution=0.0, relative=False):
    """
        Encode a joint angle as double value in a population code.

        params:
            part            -- robot part
            joint           -- joint number
            pop_size        -- size of the population
            joint_angle     -- joint angle read from the robot
            sigma           -- sigma for population coding gaussian
            resolution      -- if non-zero fixed resolution for all joints instead of fixed population size

        return:
                            -- population encoded joint angle
    """

    joint_min = j_lim[part]['joint_' + str(joint) + '_min']
    joint_max = j_lim[part]['joint_' + str(joint) + '_max']
    joint_range = joint_max - joint_min + 1

    if relative:
        joint_range = joint_range * 2. - 1
        min_val = -joint_range
    else:
        min_val = joint_min

    if resolution == 0:
        joint_deg_res = joint_range / pop_size
    else:
        joint_deg_res = resolution
        pop_size = int(np.floor(joint_range / resolution))

    neuron_deg = np.zeros((pop_size,))
    pos_pop = np.zeros((pop_size,))

    for j in range(pop_size):
        neuron_deg[j] = min_val + j * joint_deg_res
        pos_pop[j] = round(normal_pdf(neuron_deg[j], joint_angle, sigma), 3)

    # pos_pop = pos_pop/np.amax(pos_pop)

    return pos_pop
