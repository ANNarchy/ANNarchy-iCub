"""
 *  Copyright (C) 2022 Torsten Fietzek
 *
 *  plot_results.py is part of the iCub ANNarchy interface
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
import sys
from pathlib import Path

import matplotlib.pylab as plt
import matplotlib.image as plt_img
import numpy as np

# folder = "/home/toto/Schreibtisch/iCub_General_Repos/Interface_ANNarchy_iCub/Examples/Demo_Paper_Interface/results/disparity/"
# folder = "/home/toto/Schreibtisch/iCub_General_Repos/Interface_ANNarchy_iCub/Examples/Demo_Paper_Interface/results/2022-02-16_14-10/"
# folder = "/home/toto/Schreibtisch/iCub_General_Repos/Interface_ANNarchy_iCub/Examples/Demo_Paper_Interface/results/2022-02-16_17-05/"
folder = "/home/toto/Schreibtisch/iCub_General_Repos/Interface_ANNarchy_iCub/Examples/Demo_Paper_Interface/results/2022-02-16_17-08/"


# folder_prefix = "/Run1/"
# folder_prefix = "/Run2/"
folder_prefix = ""

trials = 1

save_folder = folder + "/plot_data/" + folder_prefix
Path(save_folder).mkdir(parents=True, exist_ok=True)

for i in range(trials):
    folder_trial = folder + folder_prefix + "trial_" + str(i) + "/"
    save_folder_scene = save_folder + "/scene_" + str(i) + "/"
    Path(save_folder_scene).mkdir(parents=True, exist_ok=True)

    # load data
    skin_data = np.load(folder_trial + "/skin_data.npy")
    compute_data = np.load(folder_trial + "/compute_data.npy")
    prop_data = np.load(folder_trial + "/prop_data.npy")
    scene = np.load(folder_trial + "/scene_imgs.npy")

    with open(folder_trial + "/detect.txt", 'r') as f:
        detect_str = f.read()
    if len(detect_str) == 0:
        detect = -1
    else:
        detect = int(detect_str)

    # plot data
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

    plt.savefig(save_folder + "/fig_data_trial" + str(i) + ".png")
    # plt.show()

    for j in range(scene.shape[0]):
        plt_img.imsave(save_folder_scene + "/scene_" + str(j) + ".png", scene[j])