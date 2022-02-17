"""
 *  Copyright (C) 2021 Torsten Fietzek
 *
 *  create_visualization.py is part of the ANNarchy iCub interface
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

import matplotlib.pyplot as plt
import numpy as np
import os

print("load data")
left_eye_imgs = np.load("./results/left_eye_imgs.npy")
right_eye_imgs = np.load("./results/right_eye_imgs.npy")
show_angles = np.load("./results/show_angles.npy")
scene_images= np.load("./results/scene_images.npy")

savedir = "./results/video/"
if not os.path.isdir(savedir):
    os.mkdir(savedir)

print("min", np.amin(show_angles[0]))
print("max", np.amax(show_angles[0]))

print("min", np.amin(show_angles[1]))
print("max", np.amax(show_angles[1]))

color_map = plt.cm.get_cmap('gray').reversed()

plt.rcParams['figure.constrained_layout.h_pad'] = 0.2
plt.rcParams['figure.constrained_layout.w_pad'] = 0.2
# plt.rcParams['figure.constrained_layout.hspace'] = 0.25
# plt.rcParams['figure.constrained_layout.wspace'] = 0.5

print("Create Visualization")
for i in range(show_angles.shape[1]):
    if i%5==0:
        print("img:", i)

    plt.figure(figsize=(12,8), constrained_layout=True)

    plt.subplot(2, 2, 1)
    plt.xticks([])
    plt.yticks([])
    plt.title("Simulator scene")
    plt.imshow(scene_images[i//5])

    plt.subplot(3, 4, 9)
    plt.xticks([])
    plt.yticks([])
    plt.title("Left eye image")
    plt.imshow(left_eye_imgs[i].reshape(240,320), cmap="gray")

    plt.subplot(3, 4, 10)
    plt.xticks([])
    plt.yticks([])
    plt.title("Right eye image")
    plt.imshow(right_eye_imgs[i].reshape(240,320), cmap="gray")

    plt.subplot(2, 2, 2)
    plt.xticks(np.arange(-50., 51., step=25.))
    plt.yticks(np.arange(-30., 17., step=15.))
    plt.xlim(-52., 53.)
    plt.ylim(-37., 17.)
    plt.title("Focus position (joint space)")
    plt.xlabel('joint angle (horizontal) [deg]')
    plt.ylabel('joint angle (vertical) [deg]')
    idx = i+1
    if i == 0:
        plt.scatter(show_angles[1, 0:idx], show_angles[0, 0:idx], c=np.arange(idx), cmap=color_map.reversed())
    else:
        plt.scatter(show_angles[1, 0:idx], show_angles[0, 0:idx], c=np.arange(idx), cmap=color_map)

    plt.subplot(3, 4, 11)
    if i < show_angles.shape[1]//10:
        plt.xticks(np.arange(0., show_angles.shape[1]//10 + 1, step=20.))
        plt.xlim(-10., show_angles.shape[1]//10 + 10)
    elif i < show_angles.shape[1]//2:
        plt.xticks(np.arange(0., show_angles.shape[1]//2 + 1, step=show_angles.shape[1]//10))
        plt.xlim(-20., show_angles.shape[1]//2 + 40)
    else:
        plt.xticks(np.arange(0., show_angles.shape[1] + 1, step=show_angles.shape[1]//5))
        plt.xlim(-50., show_angles.shape[1] + 100)
    plt.yticks(np.arange(-30., 17., step=15.))
    plt.ylim(-37., 17.)
    plt.title("Vertical gaze")
    plt.xlabel('timesteps [ms]')
    plt.ylabel('joint angle [deg]')
    if i == 0:
        plt.plot(show_angles[0, 0:idx], 'b.')
    else:
        plt.plot(show_angles[0, 0:idx], 'b-')

    plt.subplot(3, 4, 12)
    if i < show_angles.shape[1]//10:
        plt.xticks(np.arange(0., show_angles.shape[1]//10 + 1, step=20.))
        plt.xlim(-10., show_angles.shape[1]//10 + 10)
    elif i < show_angles.shape[1]//2:
        plt.xticks(np.arange(0., show_angles.shape[1]//2 + 1, step=show_angles.shape[1]//10))
        plt.xlim(-20., show_angles.shape[1]//2 + 40)
    else:
        plt.xticks(np.arange(0., show_angles.shape[1] + 1, step=show_angles.shape[1]//5))
        plt.xlim(-50., show_angles.shape[1] + 100)
    plt.yticks(np.arange(-50., 51., step=25.))
    plt.ylim(-52., 53.)
    plt.title("Horizontal gaze")
    plt.xlabel('timesteps [ms]')
    plt.ylabel('joint angle [deg]')
    if i == 0:
        plt.plot(show_angles[1, 0:idx], 'b.')
    else:
        plt.plot(show_angles[1, 0:idx], 'b-')
    # plt.show()
    plt.savefig(savedir + "Figure_" + str(i) + ".png", bbox_inches='tight',  pad_inches = 0.25)
    plt.close()