"""
Created on Sun Mar 01 18:19:17 2020

@author: tofo

parameterfile for testing the interface
"""


import numpy as np

#########################################################
################### general parameter ###################
# select the used simulator
gazebo = True


#########################################################
################### performance test ####################
# general
test_count = 5
position_path = "./Testfiles/test_positions/"

# jreader
n_pop_jr = 100         # population size
sigma_jr = 1.5         # sigma for population coding gaussian
neuron_res_jr = 0.0    # population resolution
parts = ["right_arm", "head"]   # tested iCub parts

# jwriter
n_pop_jw = 100         # population size
sigma_jw = 1.5         # sigma for population coding gaussian
neuron_res_jw = 0.0    # population resolution

# vreader
save_path_vr = "./Testfiles/Vision/"

# vis_move
n_pop_vm = 50
speed_arm_vm = 15
speed_head_vm = 15
save_path_vm = "./Testfiles/Vis_movement/"


#########################################################
####################### auto test #######################
# positioning
n_pop_pos = 100
sigma_pos = 1.5
neuron_res_pos = 0.0
path_pos = './Testfiles/Movement/'
position_path_pos = "./Testfiles/test_positions/"

# number of images for visual reader test
img_count = 10

# location of the sphere and the box in the simulator
loc_sph = [0.2, 1.0, 0.7]
loc_box = [-0.15, 0.8, 0.6]

if(gazebo):
    loc_sph = [loc_sph[2], loc_sph[0], loc_sph[1]]
    loc_box = [loc_box[2], loc_box[0], loc_box[1]]

