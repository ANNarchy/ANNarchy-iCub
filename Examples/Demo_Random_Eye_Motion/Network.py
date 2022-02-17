"""
 *  Copyright (C) 2021 Torsten Fietzek
 *
 *  Network.py is part of the ANNarchy iCub interface
 *
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  The ANNarchy iCub interface is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this headers. If not, see <http://www.gnu.org/licenses/>.
"""

import os

import ANNarchy as ann
import ANN_iCub_Interface.ANNarchy_iCub_Populations as iCub_pop

ann.setup(dt=10)

## Interface Populations
# Visual input populations
vis_pop_right = iCub_pop.VisionPopulation(geometry=(240, 320), port=50000, name="vis_right")
vis_pop_left = iCub_pop.VisionPopulation(geometry=(240, 320), port=50001, name="vis_left")

joint_ctrl_neuron = ann.Neuron(
    parameters="""
        y0_min_p = 0.
        y0_max_p = 0.
        m_min_p = 0.
        m_max_p = 0.
        y0_min_m = 0.
        y0_max_m = 0.
        m_min_m = 0.
        m_max_m = 0.
        """,
    equations="""
        min_value = ite((sum(inh) < 0), (y0_min_m + m_min_m * sum(inh)), (y0_min_p + m_min_p * sum(inh)))
        max_value = ite((sum(inh) < 0), (y0_max_m + m_max_m * sum(inh)), (y0_max_p + m_max_p * sum(inh)))
        r = sum(exc): min=min_value, max=max_value
    """)


# Proprioception of joint angles
joints = (3, 4)
joint_read = iCub_pop.JointReadout(geometry=(2,), joints=joints, name="head_read")

# Joint control command population
joint_write = iCub_pop.JointControl(geometry=(2,), neuron=joint_ctrl_neuron, name="head_ctrl")

## Normal ANNarchy
# ANNarchy neurons
rand_neuron = ann.Neuron(
    parameters="""
        min_val = 0.
        max_val = 0.
        """,
    equations="""r = min_val + (max_val - min_val) * Uniform(0.0, 1.0)""")
sum_neuron = ann.Neuron(
    parameters="""
        min_val = 0.
        max_val = 0.
        """,
    equations="r = sum(joint) + sum(rand_num): min=min_val, max=max_val")

# ANNarchy populations
rand_population = ann.Population(geometry=(2,), neuron=rand_neuron, name="rand")
sum_population = ann.Population(geometry=(2,), neuron=sum_neuron, name="sum")

# projections
rand_sum = ann.Projection(rand_population, sum_population, "rand_num")
rand_sum.connect_one_to_one(weights=1.0)

joint_sum = ann.Projection(joint_read, sum_population, "joint")
joint_sum.connect_one_to_one(weights=1.0)

sum_ctrl = ann.Projection(sum_population, joint_write, "exc")
sum_ctrl.connect_one_to_one(weights=1.0)


sum_ctrl1 = ann.Projection(sum_population[0], joint_write[1], "inh")
sum_ctrl1.connect_one_to_one(weights=1.0)

sum_ctrl2 = ann.Projection(sum_population[1], joint_write[0], "inh")
sum_ctrl2.connect_one_to_one(weights=1.0)


# monitors
m_right_eye = ann.Monitor(vis_pop_right, 'r')
m_left_eye = ann.Monitor(vis_pop_left, 'r')

m_joint_read = ann.Monitor(joint_read, 'r')
m_joint_ctrl = ann.Monitor(joint_write, ['r'] )
# m_rand = ann.Monitor(sum_population, 'r')
# m_sum = ann.Monitor(rand_population, 'r')


# Compile ANNarchy network
net = ann.Network(everything=True)
