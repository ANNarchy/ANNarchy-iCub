"""
 *  Copyright (C) 2022 Torsten Fietzek
 *
 *  retrieve_scene_img.py is part of the ANNarchy iCub interface
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

import numpy as np
import yarp


def visual_input_yarp():
    ######################################################################
    ######################### Init YARP network ##########################
    scene_cam = {}

    # network initialization and check
    yarp.Network.init()
    if not yarp.Network.checkNetwork():
        print('[ERROR] Please try running yarp server')

    # Initialization of all needed ports
    # Port for scene image
    scene_cam['port'] = yarp.Port()
    if not scene_cam['port'].open("/demo/scene"):
        print("[ERROR] Could not open scene camera port")
    if not yarp.Network.connect("/icubSim/cam", "/demo/scene"):
        print("[ERROR] Could not connect input_port_scene")


    ######################################################################
    ############### Initialization of imgae data structures ##############

    scene_cam['np_img'] = np.ones((240, 320, 3), np.uint8)
    scene_cam['y_img'] = yarp.ImageRgb()
    scene_cam['y_img'].resize(320, 240)

    scene_cam['y_img'].setExternal(scene_cam['np_img'].data, scene_cam['np_img'].shape[1], scene_cam['np_img'].shape[0])

    return scene_cam

def read_image(scene_cam):

    scene_cam['port'].read(scene_cam['y_img'])
    scene_cam['port'].read(scene_cam['y_img'])

    if scene_cam['y_img'].getRawImage().__int__() != scene_cam['np_img'].__array_interface__['data'][0]:
        print("read() reallocated my scene_cam['y_img']!")

    return scene_cam['np_img'].copy()