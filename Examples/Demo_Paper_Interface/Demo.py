"""
 *  Copyright (C) 2021 Torsten Fietzek
 *
 *  Demo.py is part of the iCub ANNarchy interface
 *
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  The iCub ANNarchy interface is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this headers. If not, see <http://www.gnu.org/licenses/>.
"""

from datetime import datetime
import os
import random
import sys
import time
from pathlib import Path

import ANNarchy as ann
import matplotlib.pylab as plt
import numpy as np
from iCub_ANN_Interface import __root_path__ as ann_interface_root
from iCub_ANN_Interface.iCub import (Joint_Reader, Joint_Writer,
                                     Kinematic_Reader, Skin_Reader,
                                     iCub_Interface, Kinematic_Writer)

import retrieve_scene_img as scene_cam
from Network import (monitors, pop_compute, pop_joint_read, pop_joint_write,
                     pop_sread_forearm)

Lib_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + "/Testfiles"
sys.path.append(Lib_PATH)
import iCub_Python_Lib.iCubSim_world_controller as Sim_world

# object position in world ref frame
obj_pos0 = np.array([-0.13, 0.64, 0.19])
obj_pos1 = np.array([-0.225, 0.7, 0.175])
obj_pos2 = np.array([-0.26, 0.74, 0.175])
obj_rest_pos = np.array([0, 0.3, -0.3])
obj_diff = obj_pos2-obj_pos0

# hand positions in robot ref frame
hand_start_pos = [-0.3, 0.0, 0.05 ]
hand_target_pos = [-0.3, 0.3, 0.15 ]
blocked_links = [0, 1, 2, 7, 8, 9]
# blocked_links = [0, 1, 2]
rarm_select = [0, 1, 2, 3]

params = {}
params['steps'] = 100
params['p_obj_threshold'] = 0.3
params['jr_rarm'] = (len(rarm_select),)
params['jw_rarm'] = (len(rarm_select),)
params['tr_rarm'] = (240,)

plot_on = False

folder = datetime.now().strftime("./results/%Y-%m-%d_%H:%M/")
Path(folder).mkdir(parents=True, exist_ok=True)

wc = Sim_world.WorldController()
sphere = wc.create_object("ssph", [0.025], obj_rest_pos, [1,1,1])

# Init iCub interface
iCub = iCub_Interface.iCubANN_wrapper()
ret_val, robot_dict = iCub.init_robot_from_file("./data/demo_robot.xml") # init robot by file
rarm_kinread = Kinematic_Reader.PyKinematicReader() # individual module initialization
rarm_kinwrite = Kinematic_Writer.PyKinematicWriter() # individual module initialization

ret_val = ret_val & rarm_kinread.init(iCub, "kinr_rA", "right_arm", 2, "./data")
ret_val = ret_val & rarm_kinwrite.init(iCub, "kinw_rA", "right_arm", 2, "./data")
if not ret_val:
    print("Interface initialization failed!")
    sys.exit(0)

scenecam = scene_cam.visual_input_yarp()

rarm_jw = iCub.get_jwriter_by_part("right_arm")
rarm_jr = iCub.get_jreader_by_part("right_arm")
rarm_tr = iCub.get_skinreader_by_name("TR_right_arm")

rarm_home_pos = rarm_jr.read_double_all()
rarm_start_pos = np.round(np.rad2deg(rarm_kinwrite.solve_InvKin(hand_start_pos, blocked_links)),2)
rarm_target_pos = np.round(np.rad2deg(rarm_kinwrite.solve_InvKin(hand_target_pos, blocked_links)),2)

stepwidth = np.round((rarm_target_pos - rarm_start_pos)/params['steps'],2)

upper = np.zeros_like(rarm_target_pos)
lower = np.zeros_like(rarm_start_pos)

for i in range(rarm_start_pos.shape[0]):
    if rarm_start_pos[i] > rarm_target_pos[i]:
        upper[i] = rarm_start_pos[i]
        lower[i] = rarm_target_pos[i]
    else:
        lower[i] = rarm_start_pos[i]
        upper[i] = rarm_target_pos[i]

pop_compute.lower = lower
pop_compute.upper = upper
pop_compute.start = rarm_start_pos

pop_compute.step = stepwidth

print("start:", rarm_start_pos)
print("target:", rarm_target_pos)
print("step:", stepwidth)

# Joint_Writer.PyJointWriter().retrieve_ANNarchy_input_multi()
# Joint_Reader.PyJointReader().

rarm_jw.write_double_multiple(rarm_start_pos, rarm_select, "abs", True)
ann.simulate(2)
out = True
trial = 0
while(out):
    if trial%5 == 0:
        print("Trial:", trial)
    folder_trial = folder + "/trial_" + str(trial) + "/"
    Path(folder_trial).mkdir(parents=True, exist_ok=True)

    rarm_jw.write_double_multiple(rarm_start_pos, rarm_select, "abs", True)
    pop_compute.r = rarm_start_pos
    for mon in monitors:
        monitors[mon].start()
    target_dir = True
    simulate = True
    switches = 0
    p_place_obj = random.uniform(0, 1)
    obj_pos = random.uniform(0, 1) * obj_diff + obj_pos0
    if p_place_obj > params['p_obj_threshold']:
        print("Object placed")
        wc.move_object(sphere, obj_pos)

    step = 0
    no_hit = True
    scene = []
    detect = -1
    while(simulate):
        if step%5 == 0:
            print("Step:", step)
            scene.append(scene_cam.read_image(scenecam))

        ann.simulate(1)

        if np.allclose(pop_joint_read.r, rarm_target_pos, atol=0.05) and target_dir:
            pop_compute.step = pop_compute.step*-1
            target_dir = False
            switches += 1

        if np.allclose(pop_joint_read.r, rarm_start_pos, atol=0.05) and not target_dir:
            pop_compute.step = pop_compute.step*-1
            target_dir = True
            switches += 1

        if np.amax(pop_sread_forearm.r) > 0. and no_hit:
            jp = pop_joint_read.r
            print("Hit object at: \n    J1: {: 5.2f} deg \n    J2: {: 5.2f} deg \n    J3: {: 5.2f} deg \n    J4: {: 5.2f} deg".format(jp[0], jp[1], jp[2], jp[3]))
            # simulate = False
            switches += 1
            no_hit = False
            detect = step
            pop_compute.step = pop_compute.step*-1
            target_dir = not target_dir
        else:
            rarm_jw.retrieve_ANNarchy_input_multi()
            rarm_jw.write_ANNarchy_input_multi()

        if switches > 1:
            simulate = False

        step += 1

    # retrieve recorded data
    skin_raw_data = monitors['m_skin'].get()['r']
    timesteps = skin_raw_data.shape[0]
    skin_data = np.zeros((timesteps,))
    for i in range(timesteps):
        skin_data[i] = np.amax(skin_raw_data[i])
    compute_data = monitors['m_compute'].get()['r']
    prop_data = monitors['m_prop'].get()['r']

    # save data
    np.save(folder_trial + "/skin_data.npy", skin_data)
    np.save(folder_trial + "/compute_data.npy", compute_data)
    np.save(folder_trial + "/prop_data.npy", prop_data)
    np.save(folder_trial + "/scene_imgs.npy", scene)
    with open(folder_trial + "/detect.txt", 'w') as f:
        f.write(str(detect))

    # plot data
    if plot_on:
        fig = plt.figure(layout="constrained", figsize=(12, 8))
        subfigs = fig.subfigures(2, 1, hspace=0.125, height_ratios=[3,2])

        axes = subfigs[0].subplots(1, 4, gridspec_kw={"wspace":0.075}) #, sharey=True
        subfigs[0].suptitle("Joint angles from iCub arm joints 0-3")
        # per joint subplots
        for j in range(4):
            ax = axes[j]
            ax.set_title("Joint " + str(j))
            if detect >=0:
                line_obs = ax.axvline(x=detect, color='darkgray', linestyle='--', label='time of obstacle detection by skin sensors')
            line_prop, = ax.plot(prop_data[:, j], color='tab:blue', label="joint angle (proprioception)")
            line_comp, = ax.plot(compute_data[:, j], color='tab:orange', label="target joint angle (internally computed)")
            if j == 0:
                ax.set(xlabel='simulation time [ms]', ylabel='joint angle [deg]')
            else:
                ax.set(xlabel='simulation time [ms]')

        # one legend for all subplots
        if detect >=0:
            subfigs[0].legend(handles=[line_obs, line_prop, line_comp], bbox_to_anchor=(0., -.08, 1., 0.), loc=8, ncol=3, borderaxespad=0.)
        else:
            subfigs[0].legend(handles=[line_prop, line_comp], bbox_to_anchor=(0., -.08, 1., 0.), loc=8, ncol=2, borderaxespad=0.)

        # skin data plot
        subfigs[1].suptitle("iCub skin sensor values from right forearm patch")
        ax_fig1 = subfigs[1].subplots()
        if detect >=0:
            ax_fig1.axvline(x=detect, color='darkgray', linestyle='--', label='time of obstacle detection by skin sensors')
        ax_fig1.plot(skin_data, color="tab:green")
        ax_fig1.set(xlabel='simulation time [ms]', ylabel='maximum skin sensor value []')

        plt.savefig(folder_trial + "/fig_data.png")
        plt.show()

    r = input()
    if r == "exit":
        out = False

    # reset to start conditions
    wc.move_object(sphere, obj_rest_pos)
    rarm_jw.write_double_multiple(rarm_start_pos, rarm_select, "abs", True)
    pop_compute.r = rarm_start_pos
    trial += 1

rarm_jw.write_double_all(rarm_home_pos, "abs", True)

iCub.clear()
