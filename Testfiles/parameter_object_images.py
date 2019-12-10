"""
Created on Tue May 14 15:30:17 2019

@author: tofo

parameterfile for object/model image creation and iCub hand image creation
"""
import numpy as np


######################################################################
######################## Genereal parameters #########################

bog2deg = 180.0 / np.pi         # factor for radiant to degree conversion
eye_distance = 0.07             # distance between left and right eye
eye_loc = [0.0, 0.9375, 0.055]  # location of the center point between both eyes
eye_y_position = eye_loc[1]     # y-position of the eyes


######################################################################
###################### Parameter object/models #######################
with_arm = True
####################### Object/model positions #######################
position_param = {}
position_param['obj_x'] = [ -0.1, 0.00, 0.10 ]  # object x position in m
position_param['obj_y'] = [ 0.84, 0.94, 1.04 ]  # object y position in m
position_param['obj_z'] = [ 0.65, 0.75, 0.85 ]  # object z position in m


######################################################################
################## Parameter arm cartesian control ###################

############### Initial hand position and orientation ################
pos_hand_world_coord   = np.array([ -0.22, 0.7, 0.23, 1.0 ])             # in world coordinate system (hand pos)
# pos_hand_world_coord   = np.array([ -0.28, 0.97, 0.0, 1.0 ])             # in world coordinate system (hand up)

# pos_hand_world_coord   = np.array([ -0.15, 0.8, 0.2, 1.0 ])             # in world coordinate system
# pos_hand_world_coord   = np.array([ -0.45, 0.75, 0.0, 1.0 ])             # in world coordinate system

orientation_robot_hand = np.array([ 0.1113, -0.9845, 0.1357, 3.0023 ])  # in robot coordinate system
# orientation_robot_hand = np.array([ 0.0022, -0.993, -0.1178, 2.0423 ])  # in robot coordinate system

###################### Transformation matrices: ######################
######## robot coordinate system <-> world coordinate system #########
Transfermat_robot2world = np.array([[  0., -1., 0.,  0.0000 ],
                                    [  0.,  0., 1.,  0.5976 ],
                                    [ -1.,  0., 0., -0.0260 ],
                                    [  0.,  0., 0.,  1.0000 ]])
Transfermat_world2robot = np.linalg.inv(Transfermat_robot2world)

################ Hand positions in world coordinates #################
arm_pos_w = {}

arm_pos_w['x'] = [ -0.05, -0.07, -0.09 ]
arm_pos_w['y'] = [  0.89,  0.91,  0.93 ]
arm_pos_w['z'] = [  0.23,  0.25,  0.27 ]

#################### Initial finger joint angles #####################
finger = {}

finger['7']  = 58.8
finger['8']  = 20.0
finger['9']  = 19.8
finger['10'] = 19.8
finger['11'] = 9.9
finger['12'] = 10.8
finger['13'] = 9.9
finger['14'] = 10.8
finger['15'] = 10.8
