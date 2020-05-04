"""
Created on Sun Mar 02 18:19:17 2020

@author: tofo

save positions for interface testing
"""

import numpy as np
import yarp


import iCub_Python_Lib.YARP_motor_control as mot


yarp.Network.init()
if yarp.Network.checkNetwork() != True:
    print("[error] Please try running yarp server")
    quit()

# prepare a property object
props = yarp.Property()
part = "right_arm"
props.put("device","remote_controlboard")
props.put("remote","/icubSim/" + part)
props.put("local","/client/" + part)

# create remote driver
driver = yarp.PolyDriver(props)

# query motor control interfaces
iCtrl = driver.viewIControlMode()
iPos = driver.viewIPositionControl()
iEnc = driver.viewIEncoders()

# retrieve number of joints
jnts=iPos.getAxes()

for i in range(jnts):
    iCtrl.setControlMode(i, yarp.VOCAB_CM_POSITION)

# save the arm joint positions
# iPos, iEnc, jnts, driver = mot.motor_init('right_arm')
# test_pos0 = mot.get_joint_position(iEnc, jnts)
pos = yarp.Vector(jnts)

iEnc.getEncoders(pos.data())

print(pos)
for i in range(jnts):
    print(pos[i])
    pos[i] = round(pos[i], 2)
position = mot.yarpvec_2_npvec(pos)
print(position)
np.save("test_pos0.npy", position)
driver.close()