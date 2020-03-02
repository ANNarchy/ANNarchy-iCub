"""
Created on Sun Mar 01 18:19:17 2020

@author: tofo

parameterfile for the testing the interface
"""
import numpy as np

#########################################################
################### general parameter ###################
# select the used simulator
gazebo = False

#########################################################
####################### auto test #######################
# numver of images for visual reader test
img_count = 10
# location of the sphere and the box in the simulator
loc_sph = [0.2, 1.0, 0.7]
loc_box = [-0.15, 0.8, 0.6]
if(gazebo):
    loc_sph = [loc_sph[2], loc_sph[0], loc_sph[1]]
    loc_box = [loc_box[2], loc_box[0], loc_box[1]]
