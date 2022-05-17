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


def generate_data_figure(data, parameter, save_folder, save_postfix=""):
    # plot data
    fig = plt.figure(layout="constrained", figsize=(12, 8))
    subfigs = fig.subfigures(2, 1, hspace=0.125, height_ratios=[3,2])

    axes = subfigs[0].subplots(1, 4, gridspec_kw={"wspace":0.075}, sharey=True) #, sharey=True
    subfigs[0].suptitle("Joint angles from iCub arm joints 0-3", fontsize=parameter['suptitlesize'])
    # per joint subplots
    for j in range(4):
        ax = axes[j]
        ax.tick_params(labelsize=parameter['ticksize'])
        ax.set_ylim(parameter['y_lim_joints'])
        ax.set_xlim(parameter['x_lim'])

        ax.set_title("Joint " + str(j), fontsize=parameter['titlesize'])
        if data['detect'] >=0:
            line_obs = ax.axvline(x=data['detect'], color='darkgray', linestyle='--', label='obstacle detected by skin')
        line_prop, = ax.plot(data['prop_data'][:, j], color='tab:blue', label="joint angle (proprioception)")
        line_comp, = ax.plot(data['compute_data'][:, j], color='tab:orange', label="target joint angle (internally computed)")
        if j == 0:
            ax.set(xlabel='simulation time [ms]', ylabel='joint angle [deg]')
        else:
            ax.set(xlabel='simulation time [ms]')
        ax.xaxis.label.set_size(parameter['labelsize'])
        ax.yaxis.label.set_size(parameter['labelsize'])

    # one legend for all subplots
    if data['detect'] >=0:
        subfigs[0].legend(handles=[line_obs, line_prop, line_comp], bbox_to_anchor=(0., -.08, 1., 0.), loc=8, ncol=3, borderaxespad=0., fontsize=parameter['legendsize'])
    else:
        subfigs[0].legend(handles=[line_prop, line_comp], bbox_to_anchor=(0., -.08, 1., 0.), loc=8, ncol=2, borderaxespad=0., fontsize=parameter['legendsize'])

    # skin data plot
    subfigs[1].suptitle("iCub skin sensor values from right forearm patch", fontsize=parameter['suptitlesize'])
    ax_fig1 = subfigs[1].subplots()
    ax_fig1.tick_params(labelsize=parameter['ticksize'])
    ax_fig1.set_ylim(parameter['y_lim_skin'])
    ax_fig1.set_xlim(parameter['x_lim'])

    if data['detect'] >=0:
        ax_fig1.axvline(x=data['detect'], color='darkgray', linestyle='--', label='obstacle detected by skin')
    ax_fig1.plot(data['skin_data'], color="tab:green")
    ax_fig1.set(xlabel='simulation time [ms]', ylabel='max. skin sensor value []')
    ax_fig1.xaxis.label.set_size(parameter['labelsize'])
    ax_fig1.yaxis.label.set_size(parameter['labelsize'])

    plt.savefig(save_folder + "/fig_data_trial" + save_postfix + ".png")
    # plt.show()
    plt.close(fig=fig)



# folder = "/home/toto/Schreibtisch/iCub_General_Repos/Interface_ANNarchy_iCub/Examples/Demo_Paper_Interface/results/disparity/"
# folder = "/home/toto/Schreibtisch/iCub_General_Repos/Interface_ANNarchy_iCub/Examples/Demo_Paper_Interface/results/2022-02-16_14-10/"
# folder = "/home/toto/Schreibtisch/iCub_General_Repos/Interface_ANNarchy_iCub/Examples/Demo_Paper_Interface/results/2022-02-16_17-05/"
folder = "/home/toto/Schreibtisch/iCub_General_Repos/Interface_ANNarchy_iCub/Examples/Demo_Paper_Interface/results/2022-02-16_17-08/"


# folder_prefix = "/Run1/"
# folder_prefix = "/Run2/"
folder_prefix = ""

parameter = {}
parameter['ticksize'] = 13
parameter['legendsize'] = 14
parameter['suptitlesize'] = 18
parameter['titlesize'] = 16
parameter['labelsize'] = 14

parameter['y_lim_joints'] = [-70., 70.]
parameter['y_lim_skin'] = [-0.05, 1.1]
parameter['x_lim'] = [-3, 740]

trials = 1
figure_video = True
scene_video = True

save_folder = folder + "/plot_data2/" + folder_prefix
Path(save_folder).mkdir(parents=True, exist_ok=True)

for i in range(trials):
    folder_trial = folder + folder_prefix + "trial_" + str(i) + "/"
    if scene_video:
        save_folder_scene = save_folder + "/scene_" + str(i) + "/"
        Path(save_folder_scene).mkdir(parents=True, exist_ok=True)
    if figure_video:
        save_folder_figures = save_folder + "/fig_video/"
        Path(save_folder_figures).mkdir(parents=True, exist_ok=True)


    # load data
    data = {}
    data['skin_data'] = np.load(folder_trial + "/skin_data.npy")
    data['compute_data'] = np.load(folder_trial + "/compute_data.npy")
    data['prop_data'] = np.load(folder_trial + "/prop_data.npy")
    if scene_video:
        scene = np.load(folder_trial + "/scene_imgs.npy")

    with open(folder_trial + "/detect.txt", 'r') as f:
        detect_str = f.read()
    if len(detect_str) == 0:
        data['detect'] = -1
    else:
        data['detect'] = int(detect_str)

    # plot
    generate_data_figure(data, parameter, save_folder, save_postfix=str(i))
    step = 0
    if figure_video:
        for k in range(data['skin_data'].shape[0]):
            if (k%5) == 0:
                data1 = {}
                data1['skin_data'] = data['skin_data'][:k]
                data1['compute_data'] = data['compute_data'][:k]
                data1['prop_data'] = data['prop_data'][:k]
                if k >= data['detect']:
                    data1['detect'] = data['detect']
                else:
                    data1['detect'] = -1
                

                generate_data_figure(data1, parameter, save_folder_figures, save_postfix="_" + str(step))
                step += 1


    if scene_video:
        for j in range(scene.shape[0]):
            plt_img.imsave(save_folder_scene + "/scene_" + str(j) + ".png", scene[j])