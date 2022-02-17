"""
 *  Copyright (C) 2021 Torsten Fietzek
 *
 *  Demo.py is part of the ANNarchy iCub interface
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

import sys
import time

import ANNarchy as ann
import matplotlib.pylab as plt
import numpy as np
from ANN_iCub_Interface import __root_path__ as ann_interface_root
from ANN_iCub_Interface.iCub import iCub_Interface

from Network import (m_joint_ctrl, m_joint_read, m_left_eye,  # , m_rand, m_sum
                     m_right_eye, net)
from retrieve_scene_img import visual_input_yarp
from Sync_Classes import ANNarchyClock, iCubClock, master

# Compile network
compiler_flags = "-march=native -O2" + " -I"+ann_interface_root+" -Wl,-rpath,"+ann_interface_root+"/ANN_iCub_Interface/grpc/"
extra_libs = "-lprotobuf -lgrpc++ -lgrpc++_reflection -L"+ann_interface_root+"/ANN_iCub_Interface/grpc/ -liCub_ANN_grpc"
net.compile(directory='annarchy_iCub_demo', clean=False, compiler_flags=compiler_flags, extra_libs=extra_libs)

# Connect input populations to gRPC service
for pop in net.get_populations():
    try:
        pop.connect()
    except:
        pass

net.get_population("head_ctrl").y0_min_p = [-25., -25.]
net.get_population("head_ctrl").y0_max_p = [15., 25.]
net.get_population("head_ctrl").m_min_p = [0.8, 0.]
net.get_population("head_ctrl").m_max_p = [-0.4, 0.]
net.get_population("head_ctrl").y0_min_m = [-25., -25.]
net.get_population("head_ctrl").y0_max_m = [15., 25.]
net.get_population("head_ctrl").m_min_m = [-0.8, 0.]
net.get_population("head_ctrl").m_max_m = [0.4, 0.]

net.get_population("sum").min_val = [-25., -25.]
net.get_population("sum").max_val = [15., 25.]

net.get_population("rand").min_val = [-12.5, -15.]
net.get_population("rand").max_val = [10., 15.]

# Init iCub interface
iCub = iCub_Interface.iCubANN_wrapper()
ret_val, robot_dict = iCub.init_robot_from_file("./data/demo_robot.xml")
if not ret_val:
    print("Interface initialization failed!")
    sys.exit(0)
head_jw = iCub.get_jwriter_by_part("head")
head_jr = iCub.get_jreader_by_part("head")

head_jw.write_double_all([0., 0., 0., 0., 0., 0.], "abs")

time.sleep(1.5)

icub_clock = iCubClock(iCub)
ann_clock = ANNarchyClock(net)

master.add(icub_clock)
master.add(ann_clock)

# scene video
input_port_scene, scene_yarp_image, scene_img_array = visual_input_yarp()
scene_images = []

for i in range(200):
    if i%5==0:
        print("step:", i)

    master.update(50.)

    input_port_scene.read(scene_yarp_image)
    input_port_scene.read(scene_yarp_image)

    if scene_yarp_image.getRawImage().__int__() != scene_img_array.__array_interface__['data'][0]:
        print("read() reallocated my scene_yarp_image!")
    scene_images.append(scene_img_array.copy())

print("save data")
np.save("left_eye_imgs", net.get(m_left_eye).get('r'))
np.save("right_eye_imgs", net.get(m_right_eye).get('r'))
# np.save("random", net.get(m_rand).get('r'))
# np.save("summe", net.get(m_sum).get('r'))
np.save("show_angles", np.round(net.get(m_joint_read).get('r').transpose(), 4))
np.save("ctrl_r", np.round(net.get(m_joint_ctrl).get('r').transpose(), 4))

np.save("scene_images", scene_images)
