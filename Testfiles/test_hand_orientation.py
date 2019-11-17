
import numpy as np
import time
import yarp
import cv2
import os
import sys

# import lib.auxilaries as aux
# import lib.image_processing as img
import lib.motor_control as mot

from parameter_object_images import Transfermat_robot2world, Transfermat_world2robot, orientation_robot_hand, pos_hand_world_coord, arm_pos_w, finger



###################### print position/orientation #######################

def print_hand_pos(world_pos, orient_giv, hand_pos_r, orient_r, Mat_rw):

    pos_akt = np.ones((4,1))
    for i in range(3):
        pos_akt[i] = hand_pos_r[i]
    pos_akt_w = np.dot(Mat_rw, pos_akt)
    delta = []

    for i in range(3):
        d = round(float(world_pos[i]), 4) - round(float(pos_akt_w[i]), 4)
        if abs(d) > 0.01:
            print('ACHTUNG')
        delta.append(d)
    print('Delta  position:', delta)

    delta_o = []
    for i in range(4):
        d = round(float(orient_giv[i]), 4) - round(float(orient_r[i]), 4)
        if abs(d) > 0.3:
            print('ACHTUNG')
        delta_o.append(d)
    print('Delta  orientation:', delta_o)

    print('Hand position', round(pos_akt_w[0, 0], 4), round(pos_akt_w[1, 0], 4), round(pos_akt_w[2, 0], 4))
    print('Hand orientation', round(orient_r[0], 4), round(orient_r[1], 4), round(orient_r[2], 4), round(orient_r[3], 4))



######################################################################
############## init cartesian controller for right arm ###############
yarp.Network.init()
if yarp.Network.checkNetwork() != True:
    print("[error] Please try running yarp server")
    quit()
T_r2w = Transfermat_robot2world
T_w2r = Transfermat_world2robot

orient_hand = mot.npvec_2_yarpvec(orientation_robot_hand)

pos     = yarp.Vector(3)
orient  = yarp.Vector(4)
    
# prepare a property object
props = yarp.Property()
props.put("device","cartesiancontrollerclient")
props.put("remote","/icubSim/cartesianController/right_arm")
props.put("local","/client/right_arm")

# create remote driver
DeadDriver_rarm = yarp.PolyDriver(props)

# query motor control interfaces
iCart = DeadDriver_rarm.viewICartesianControl()
iCart.setPosePriority("position")
######################################################################

welt_pos = pos_hand_world_coord
iCart.getPose(pos, orient)
print_hand_pos(welt_pos, orient_hand, pos, orient, T_r2w)
time.sleep(1)
print(welt_pos)
rob_pos = np.dot(T_w2r,  welt_pos.reshape((4,1)))
pos_rob = mot.npvec_2_yarpvec(rob_pos[0:3])
iCart.goToPoseSync(pos_rob, orient_hand)
iCart.waitMotionDone(period=5.0)
iCart.getPose(pos, orient)
print_hand_pos(welt_pos, orient_hand, pos, orient, T_r2w)
time.sleep(1)

iCart.getPose(pos, orient)
print_hand_pos(welt_pos, orient_hand, pos, orient, T_r2w)

iCart.stopControl()
DeadDriver_rarm.close()

# # save the arm joint positions
# iPos, iEnc, jnts, driver = mot.motor_init('right_arm')
# test_pos0 = mot.get_joint_position(iEnc, jnts)
# print(test_pos0)
# for i in range(jnts):
#     print(test_pos0[i])
# position = mot.yarpvec_2_npvec(test_pos0)
# print(position)
# np.save("test_pos0.npy", position)
# driver.close()