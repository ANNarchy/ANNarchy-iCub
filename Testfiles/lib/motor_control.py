"""
Created on Thu Apr 13 15:16:32 2018

@author: tofo

library for functions related to the motor control
"""

import numpy as np
import yarp
import time

######################################################################
######################### init motor control #########################

def motor_init(part):
    '''
    initialize motor control for the given part 

    params: part    -- part of the iCub to be controlled (string: head, left_arm, right_arm, ...)
    return: iPos    -- Position Controller for the given iCub part
            iEnc    -- Encoder for the controlled joints
            jnts    -- number of controlled joints
    '''
    # prepare a property object
    props = yarp.Property()
    props.put("device","remote_controlboard")
    props.put("local","/client/" + part)
    props.put("remote","/icubSim/"+ part)

    # create remote driver
    DeadDriver = yarp.PolyDriver(props)

    #query motor control interfaces
    iPos = DeadDriver.viewIPositionControl()
    iEnc = DeadDriver.viewIEncoders()
    
    #retrieve number of joints
    jnts=iPos.getAxes()

    print('----- Controlling', jnts, 'joints -----')
    return iPos, iEnc, jnts, DeadDriver


######################################################################
###################### go to head zero position ######################
def goto_zero_head_pos(iPos_head, iEnc_head, jnts_head):
    '''
    go to the all joints at 0 degree position

    params: iPos_head   -- Position Controller for the iCub head
            iEnc_head   -- Encoder for the head joints
            jnts_head   -- number of head joints
    '''
    zero_pos = yarp.Vector(jnts_head)
    set_pos_vec(zero_pos, 0.0, jnts_head)
    iPos_head.positionMove(zero_pos.data()) 
    motion = False
    while not motion:
        act_pos = get_joint_position(iEnc_head, jnts_head)
        motion = iPos_head.checkMotionDone() and (abs(act_pos[4]) < (abs(zero_pos[4]) + 0.2))


######################################################################
##################### move eyes to new position ######################
def move_eyes(eye_pos, iPos_h, jnts_h, offset_h=0):
    '''
    move the iCub eyes to a new position

    params: eye_pos     -- target eye position [ gaze_y, gaze_x, vergence_angle ]
            iPos_h      -- Position Controller for the iCub head
            jnts_h      -- number of head joints
    '''
    targ_pos = yarp.Vector(jnts_h)
    set_pos_vec(targ_pos, 0.0, jnts_h)
    targ_pos.set(2, offset_h)
    targ_pos.set(3, eye_pos[0])
    targ_pos.set(4, (eye_pos[1] + offset_h))
    targ_pos.set(5, eye_pos[2])

    iPos_h.positionMove(targ_pos.data())
    motion = False
    while not motion:
        time.sleep(0.01)
        motion = iPos_h.checkMotionDone()
    time.sleep(0.4)


######################################################################
###################### get the joints positions ######################
def get_joint_position(iEnc, jnts):
    '''
    get position of controlled joints

    params: iEnc    -- Encoder for the controlled joints
            jnts    -- number of joints

    return: encs    -- Vector containing the joint positions
    '''
    # read encoders
    encs = yarp.Vector(jnts)
    iEnc.getEncoders(encs.data())
    return encs


######################################################################
############### set position vector with given values ################
def set_pos_vector(pos_vec, a, b, c, d, e, f):
    '''
    set position vector with given values for each joints (6 joints like iCub head)

    params: pos_vec     -- position vector
            a           -- value joint 0
            b           -- value joint 1
            c           -- value joint 2
            d           -- value joint 3
            e           -- value joint 4
            f           -- value joint 5
    '''
    pos_vec.set(0, a)
    pos_vec.set(1, b)
    pos_vec.set(2, c)
    pos_vec.set(3, d)
    pos_vec.set(4, e)
    pos_vec.set(5, f)


def set_pos_vec(pos_vec, a, jnts):
    '''
    set position vector with one value for all joints

    params: pos_vec     -- position vector
            a           -- value for all joints
            jnts        -- number of joints
    '''
    for x in range(0, jnts):
        pos_vec.set(x, a)


######################################################################
############ Convert between yarp vector and numpy array #############
def npvec_2_yarpvec(array):
    '''
    convert a 1D numpy array into a YARP vector

    params: array       -- 1D Numpy array

    return: yarp_vec    -- YARP vector, result of conversion
    '''
    vector = np.array(array)
    yarp_vec = yarp.Vector(vector.shape[0])

    for i in range(vector.shape[0]):
        yarp_vec.set(i, float(vector[i]))
    
    return yarp_vec

def yarpvec_2_npvec(yarp_vec):
    '''
    convert a YARP vector into a 1D numpy array 

    params: yarp_vec    -- YARP vector

    return: vector      -- 1D Numpy array, result of conversion 
    '''
    vector = np.zeros(yarp_vec.length())

    for i in range(yarp_vec.length()):
        vector[i] = float(yarp_vec[i])
    
    return vector
