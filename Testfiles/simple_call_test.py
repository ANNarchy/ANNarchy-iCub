"""
 *  Copyright (C) 2019-2020 Torsten Follak
 *
 *  simple_call_test.py is part of the iCub ANNarchy interface
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
import time

import matplotlib.pylab as plt
import numpy as np

sys.path.append("../build/")
import iCub_Interface   # requires iCub_Interface.so in the present directory

# Test support files
from supplementary.auxilary_methods import encode

#########################################################
def call_test_jreader(ann_wrapper):
    """
        Call test for the joint reader module to check different errors.

        params:
            ann_wrapper     -- iCub_ANNarchy Interface
    """

    # add joint reader instances
    ann_wrapper.add_joint_reader("J_Reader")
    ann_wrapper.add_joint_reader("J_Reader")    # duplicate check
    ann_wrapper.add_joint_reader("J_Reader1")
    ann_wrapper.add_joint_reader("J_Reader2")

    print('finish adding')
    print('\n')

    # init joint reader
    ann_wrapper.parts_reader["J_Reader"].init(ann_wrapper.PART_KEY_HEAD, 0.5, 15)
    ann_wrapper.parts_reader["J_Reader"].init(ann_wrapper.PART_KEY_HEAD, 0.5, 15)        # double initialization
    ann_wrapper.parts_reader["J_Reader1"].init(ann_wrapper.PART_KEY_RIGHT_ARM, -0.5, 15)      # negative sigma
    ann_wrapper.parts_reader["J_Reader1"].init(ann_wrapper.PART_KEY_RIGHT_ARM, 0.5, 0, 2.0)   # neuron resolution
    ann_wrapper.parts_reader["J_Reader2"].init('false_part_key', 0.5, 15)                     # false part key
    ann_wrapper.parts_reader["J_Reader2"].init(ann_wrapper.PART_KEY_LEFT_ARM, 0.5, -15)       # negative population size
    ann_wrapper.parts_reader["J_Reader2"].init(ann_wrapper.PART_KEY_LEFT_ARM, 0.5, 0, 0.0)    # wrong population sizing
    if "NO_NAME" in ann_wrapper.parts_reader:
        ann_wrapper.parts_reader["NO_NAME"].init(ann_wrapper.PART_KEY_LEFT_ARM, 0.5, 15)          # not existent name
    else:
        print("Not existing name!")

    ann_wrapper.rm_joint_reader("J_Reader2")

    print('finish JReader init')
    print('\n')

    # print joint resolutions for joint reader
    print(ann_wrapper.parts_reader["J_Reader"].get_joints_deg_res())
    print(ann_wrapper.parts_reader["J_Reader"].get_neurons_per_joint())

    print(ann_wrapper.parts_reader["J_Reader1"].get_joints_deg_res())
    print(ann_wrapper.parts_reader["J_Reader1"].get_neurons_per_joint())

    print('finish JReader resolutions')
    print('\n')

    # test read joints with joint reader
    print('read double_one')
    print(ann_wrapper.parts_reader["J_Reader"].read_double_one(3))
    print('read double_all')
    print(ann_wrapper.parts_reader["J_Reader"].read_double_all())
    print('read pop_one')
    print(ann_wrapper.parts_reader["J_Reader"].read_pop_one(3))
    print('read pop_all')
    print(ann_wrapper.parts_reader["J_Reader"].read_pop_all())

    print('finish JReader reading joints')
    print('\n')

    # close joint reader
    ann_wrapper.parts_reader["J_Reader"].close()
    ann_wrapper.parts_reader["J_Reader1"].close()

    print('finish JReader close')
    print('\n')


#########################################################
def call_test_jwriter(ann_wrapper):
    """
        Call test for the joint writer module to check different errors.

        params:
            ann_wrapper     -- iCub_ANNarchy Interface
    """

    # add joint writer instances
    ann_wrapper.add_joint_writer("J_Writer")
    ann_wrapper.add_joint_writer("J_Writer")   # duplicate check
    ann_wrapper.add_joint_writer("J_Writer1")
    ann_wrapper.add_joint_writer("J_Writer2")

    print('finish adding')
    print('\n')

    # init joint writer
    ann_wrapper.parts_writer["J_Writer"].init(ann_wrapper.PART_KEY_HEAD, 15)
    ann_wrapper.parts_writer["J_Writer"].init(ann_wrapper.PART_KEY_HEAD, 15)          # double initialization
    ann_wrapper.parts_writer["J_Writer1"].init('false_part_key', 15)                  # false part key
    ann_wrapper.parts_writer["J_Writer2"].init(ann_wrapper.PART_KEY_LEFT_ARM, -15)    # negative population size
    ann_wrapper.parts_writer["J_Writer1"].init(ann_wrapper.PART_KEY_RIGHT_ARM, 0, 2.0)
    # ann_wrapper.parts_writer["NO_NAME"].init(ann_wrapper.PART_KEY_LEFT_ARM, 15)       # not existent name

    ann_wrapper.rm_joint_writer("J_Writer2")

    print('finish JWriter init')
    print('\n')

    # print joint population resolutions and velocity for joint writer
    print(ann_wrapper.parts_writer["J_Writer"].get_joints_deg_res())
    print(ann_wrapper.parts_writer["J_Writer"].get_neurons_per_joint())
    print(ann_wrapper.parts_writer["J_Writer"].set_joint_velocity(15.0))


    print(ann_wrapper.parts_writer["J_Writer1"].get_joints_deg_res())
    print(ann_wrapper.parts_writer["J_Writer1"].get_neurons_per_joint())
    print(ann_wrapper.parts_writer["J_Writer1"].set_joint_velocity(10.0, joint=3))

    print('finish JWriter resolutions')
    print('\n')

    # define test positions
    double_all = np.zeros(6)
    double_all_rel = np.ones(6) * 5.1
    test_pos = encode(ann_wrapper.PART_KEY_HEAD, 4, 15, 5, 0.5)
    test_pos_rel = encode(ann_wrapper.PART_KEY_HEAD, 4, 15, 5, 0.5, relative=True)
    pop_multiple = np.zeros((3, 15))
    pop_multiple_rel = np.zeros((3, 15))
    pop_all = np.zeros((6, 15))
    pop_all_rel = np.zeros((6, 15))

    for i in range(3):
        pop_multiple[i] = encode(ann_wrapper.PART_KEY_HEAD, i + 3, 15, 10., 0.5)
        pop_multiple_rel[i] = encode(ann_wrapper.PART_KEY_HEAD, i + 3, 15, 10., 0.5, relative=True)


    for i in range(6):
        pop_all[i] = encode(ann_wrapper.PART_KEY_HEAD, i, 15, 5., 0.5)
        pop_all_rel[i] = encode(ann_wrapper.PART_KEY_HEAD, i, 15, 5., 0.5, relative=True)

    print("write absolute values")
    # test writing absolute joint angles
    print('write double_one')
    print(ann_wrapper.parts_writer["J_Writer"].write_double_one(10.0, 4, "abs", True))
    time.sleep(2.5)
    print('write double_multiple')
    print(ann_wrapper.parts_writer["J_Writer"].write_double_multiple( [10., 10., 10.],  [3, 4, 5], "abs", True))
    time.sleep(2.5)
    print('write double_all')
    print(ann_wrapper.parts_writer["J_Writer"].write_double_all(double_all, "abs", True))
    time.sleep(2.5)
    print('write pop_one')
    print(ann_wrapper.parts_writer["J_Writer"].write_pop_one(test_pos, 4, "abs", True))
    time.sleep(2.5)
    print('write pop_multiple')
    print(ann_wrapper.parts_writer["J_Writer"].write_pop_multiple(pop_multiple, [3, 4, 5], "abs", True))
    time.sleep(2.5)
    print('write pop_all')
    print(ann_wrapper.parts_writer["J_Writer"].write_pop_all(pop_all, "abs", True))

    print("write relative values")
    # test writing relative joint angles
    print('write double_one')
    print(ann_wrapper.parts_writer["J_Writer"].write_double_one(10.0, 4, "rel", True))
    time.sleep(2.5)
    print('write double_multiple')
    print(ann_wrapper.parts_writer["J_Writer"].write_double_multiple([10., 10., 10.], [3, 4, 5], "rel", True))
    time.sleep(2.5)
    print('write double_all')
    print(ann_wrapper.parts_writer["J_Writer"].write_double_all(double_all_rel, "rel", True))
    time.sleep(2.5)
    print('write pop_one')
    print(ann_wrapper.parts_writer["J_Writer"].write_pop_one(test_pos_rel, 4, "rel", True))
    time.sleep(2.5)
    print('write pop_multiple')
    print(ann_wrapper.parts_writer["J_Writer"].write_pop_multiple(pop_multiple_rel, [3, 4, 5], "rel", True))
    time.sleep(2.5)
    print('write pop_all')
    print(ann_wrapper.parts_writer["J_Writer"].write_pop_all(pop_all_rel, "rel", True))

    print('reset head position')
    print(ann_wrapper.parts_writer["J_Writer"].write_double_all(double_all, "abs", True))
    time.sleep(2.5)

    print('finish JWriter writing joints')
    print('\n')

    # close joint writer modules
    print(ann_wrapper.parts_writer["J_Writer"].close())
    print(ann_wrapper.parts_writer["J_Writer1"].close())

    print('finish JWriter close')
    print('\n')


#########################################################
def call_test_sreader(ann_wrapper):
    """
        Call test for the skin reader module to check different errors.

        params:
            ann_wrapper     -- iCub_ANNarchy Interface
    """

    # add skin reader instances
    ann_wrapper.add_skin_reader("S_Reader")
    ann_wrapper.add_skin_reader("S_Reader")    # duplicate check
    ann_wrapper.add_skin_reader("S_Reader1")

    print('finish skin reader adding')
    print('\n')

    # init skin reader
    ann_wrapper.tactile_reader["S_Reader"].init("r", True)       # correct init
    ann_wrapper.tactile_reader["S_Reader"].init("r", True)       # double init
    # ann_wrapper.tactile_reader["NO_NAME"].init("r", True)        # non existent name
    ann_wrapper.tactile_reader["S_Reader1"].init("g", False)     # wrong eye descriptor
    ann_wrapper.tactile_reader["S_Reader1"].init("l", False)     # correct init; non norm

    ann_wrapper.rm_skin_reader("S_Reader1")

    print('finish SReader init')
    print('\n')

    # print taxel positions
    ann_wrapper.tactile_reader["S_Reader"].read_tactile()
    print(ann_wrapper.tactile_reader["S_Reader"].get_taxel_pos("arm"))
    print(ann_wrapper.tactile_reader["S_Reader"].get_taxel_pos("forearm"))
    print(ann_wrapper.tactile_reader["S_Reader"].get_taxel_pos("hand"))

    # print tactile data
    print(ann_wrapper.tactile_reader["S_Reader"].get_tactile_arm())
    print(ann_wrapper.tactile_reader["S_Reader"].get_tactile_forearm())
    print(ann_wrapper.tactile_reader["S_Reader"].get_tactile_hand())

    # close skin reader
    print(ann_wrapper.tactile_reader["S_Reader"].close())

    print('finish SReader close')
    print('\n')


#########################################################
def call_test_vreader(ann_wrapper):
    """
        Call test for the visual reader module to check different errors.

        params:
            ann_wrapper     -- iCub_ANNarchy Interface
    """

    # add visual reader instance
    ann_wrapper.add_visual_reader()
    ann_wrapper.add_visual_reader()

    print('finish visual reader adding')
    print('\n')

    # init visual reader
    print(ann_wrapper.visual_input.init('r', 75, 48, 320, 240))  # invalid field of view width
    print(ann_wrapper.visual_input.init('r', 60, 56, 320, 240))  # invalid field of view height
    print(ann_wrapper.visual_input.init('t', 60, 48, 320, 240))  # invalid eye character
    print(ann_wrapper.visual_input.init('r', 60, 48, 160, 120))  # output size below input size
    print(ann_wrapper.visual_input.init('r'))                    # use of default values; init already done

    print('finish VReader init')
    print('\n')

    # record images from the iCub cameras
    ann_wrapper.visual_input.start()
    time.sleep(1.5)
    test_img = ann_wrapper.visual_input.read_from_buffer()
    print(test_img.shape)
    if test_img.shape[0] > 0:
        test_img = test_img.reshape(120, 160)
        print(type(test_img), type(test_img[0][0]))
        plt.imshow(test_img, cmap='gray')
        plt.show()
        plt.pause(0.05)
    else:
        print('No buffered image!')

    # stop the visual reader instance
    ann_wrapper.visual_input.stop()
    # first remove the old visual reader instance, then add and init a new visual reader instance
    ann_wrapper.rm_visual_reader()
    ann_wrapper.add_visual_reader()
    print(ann_wrapper.visual_input.init('l'))                    # use of default values; reinitialization left eye

    # first remove the old visual reader instance, then add and init a new visual reader instance
    ann_wrapper.rm_visual_reader()
    ann_wrapper.add_visual_reader()
    print(ann_wrapper.visual_input.init('b'))                    # use of default values; reinitialization binocular
    ann_wrapper.rm_visual_reader()


#########################################################
if __name__ == "__main__":
    wrapper = iCub_Interface.iCubANN_wrapper()

    if len(sys.argv) > 1:
        for command in sys.argv[1:]:
            if command == 'all':
                call_test_jreader(wrapper)
                call_test_jwriter(wrapper)
                call_test_sreader(wrapper)
                call_test_vreader(wrapper)
            elif command == "noskin":
                call_test_jreader(wrapper)
                call_test_jwriter(wrapper)
                call_test_vreader(wrapper)
            elif command == "jreader":
                call_test_jreader(wrapper)
            elif command == "jwriter":
                call_test_jwriter(wrapper)
            elif command == "sreader":
                call_test_sreader(wrapper)
            elif command == "vreader":
                call_test_vreader(wrapper)
            else:
                print('No valid test command! Valid are: all, noskin, jreader, jwriter, sreader, vreader')
    else:
        print('No valid test command! Valid are: all, noskin, jreader, jwriter, sreader, vreader')

    del wrapper
    print('finished call tests')
