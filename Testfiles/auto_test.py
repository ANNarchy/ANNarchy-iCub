"""
 *  Copyright (C) 2019-2021 Torsten Fietzek
 *
 *  auto_test.py is part of the iCub ANNarchy interface
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

import os
import sys
import time

import matplotlib.pylab as plt
import numpy as np

sys.path.append("../build/")
import iCub_Interface  # requires iCub_Interface.so in the present directory

# Python libraries for simulator control
import iCub_Python_Lib.iCubSim_world_controller as iSim_wc
import iCub_Python_Lib.gazebo_world_controller as gzbo_wc

# Test support files
import supplementary.testing_parameter as params
from supplementary.auxilary_methods import encode


#########################################################
def check_position_double_mult(name, start, jnt_count, read_method, position):
    # read the joint positions
    read_pos = np.zeros((start + jnt_count), dtype=np.float64)
    for i in range(start, start + jnt_count):
        read_pos[i] = round(read_method(i), 2)

    # compare the written positions with the returned joint positions
    test_result = True
    error_joints = []
    for i in range(start, start + jnt_count):
        max_lim = abs(round(position[i], 2))  + 0.3 # + 0.1 * abs(round(position[i], 2)
        min_lim = abs(round(position[i], 2))  - 0.3 # - 0.1 * abs(round(position[i], 2))
        if (abs(round(read_pos[i], 2)) > max_lim) or (abs(round(read_pos[i], 2)) < min_lim):
            test_result = False
            error_joints.append(i)

    return (test_result, error_joints), read_pos


def check_position_double_all(name, read_method, position):
    # read the joint positions
    read_pos = read_method()

    # compare the written positions with the returned joint positions
    test_result = True
    error_joints = []
    for i in range(len(read_pos)):
        max_lim = abs(round(position[i], 2)) + 0.3 # + 0.1 * abs(round(position[i], 2))
        min_lim = abs(round(position[i], 2)) - 0.3 # - 0.1 * abs(round(position[i], 2))
        if (abs(round(read_pos[i], 2)) > max_lim) or (abs(round(read_pos[i], 2)) < min_lim):
            test_result = False
            error_joints.append(i)

    return (test_result, error_joints), read_pos


def check_position_pop_mult(name, start, jnt_count, read_method, position):
    # read the joint positions
    read_pos = []
    for i in range(start, start + jnt_count):
        read_pos.append(np.round(read_method(i), decimals=3))

    # compare the written positions with the returned joint positions
    test_result = True
    error_joints = []
    for i in range(len(read_pos)):
        if not np.allclose(read_pos[i], position[start + i], atol=0.1):
            test_result = False
            error_joints.append(i)

    return (test_result, error_joints), read_pos


def check_position_pop_all(name, read_method, position):
    # read the joint positions
    read_pos = read_method()

    # compare the written positions with the returned joint positions
    test_result = True
    error_joints = []
    for i in range(len(read_pos)):
        if not np.allclose(read_pos[i], position[i], atol=0.1):
            test_result = False
            error_joints.append(i)

    return (test_result, error_joints), read_pos


def rel_pos_double(ann_wrapper, name, key, target_positions):

    act_pos = np.array(ann_wrapper.parts_reader[name].read_double_all(), dtype=np.float64)
    rel_pos = target_positions[name][key] - act_pos

    return rel_pos


def rel_pos_pop(ann_wrapper, name, key, target_positions):

    act_pos = np.array(ann_wrapper.parts_reader[name].read_double_all(), dtype=np.float64)
    rel_pos_d = target_positions[name][key] - act_pos
    rel_pos = np.zeros((act_pos.shape[0], params.n_pop_pos))

    for i in range(rel_pos_d.shape[0]):
        rel_pos[i] = encode(name, i, params.n_pop_pos, rel_pos_d[i], params.sigma_pos, relative=True)
    return rel_pos


def write_joint_each(ann_wrapper, pos_type, positioning, block, name, target_positions, write_method, read_method, check_method, res_path, jnts, rel_method=None, positions_double=None):

    # test the positioning with values for a single joint and motion of all joints
    read = {}
    test_results = {}

    for key in target_positions[name]:
        print('______ Test position:', key)
        if positioning == "abs":
            target_pos = target_positions[name][key]
            check_pos = target_positions
        elif positioning == "rel":
            target_pos = rel_method(ann_wrapper, name, key, positions_double)
            check_pos = positions_double
        else:
            print("No correct positioning type: valid are \"abs\" and \"rel\"")
            return

        # move the joints
        for i in range(jnts[name]):
            write_method(target_pos[i], i, positioning, block)
        time.sleep(3.)

        test_results[name + '_' + key], read[name + '_' + key] = check_method(name, 0, jnts[name], read_method, check_pos[name][key])

    # save the read joint positions
    for key in read:
        np.save(res_path + key + "_" + pos_type + "_" + positioning + ".npy", read[key])

    print("________ Test results: " + pos_type + "_" + positioning)
    for key in test_results:
        print('Test:', key, 'results:', test_results[key])

    print('\n')


def write_joint_mult(ann_wrapper, pos_type, positioning, block, name, target_positions, write_method, read_method, check_method, res_path, jnt_sel, rel_method=None, positions_double=None):

    # test the positioning with values for a single joint and motion of all joints
    read = {}
    test_results = {}

    print('____ Test part:', name)
    for key in target_positions[name]:
        print('______ Test position:', key)
        if positioning == "abs":
            target_pos = target_positions[name][key]
            check_pos = target_positions
        elif positioning == "rel":
            target_pos = rel_method(ann_wrapper, name, key, positions_double)
            check_pos = positions_double
        else:
            print("No correct positioning type: valid are \"abs\" and \"rel\"")
            return

        # move the joints
        write_method(target_pos[jnt_sel[name]], jnt_sel[name], positioning, block)
        time.sleep(2.)

        test_results[name + '_' + key], read[name + '_' + key] = check_method(name, jnt_sel[name][0], jnt_sel[name].shape[0], read_method, check_pos[name][key])

    # save the read joint positions
    for key in read:
        np.save(res_path + key + "_" + pos_type + "_" + positioning + ".npy", read[key])

    print("________ Test results: " + pos_type + "_" + positioning)
    for key in test_results:
        print('Test:', key, 'results:', test_results[key])

    print('\n')


def write_joint_all(ann_wrapper, pos_type, positioning, block, name, target_positions, write_method, read_method, check_method, res_path, rel_method=None, positions_double=None):

    # test the positioning with values for a single joint and motion of all joints
    print('__ Type of positioning: ' + pos_type)
    read = {}
    test_results = {}

    print('____ Test part:', name)
    for key in target_positions[name]:
        print('______ Test position:', key)
        if positioning == "abs":
            target_pos = target_positions[name][key]
            check_pos = target_positions
        elif positioning == "rel":
            target_pos = rel_method(ann_wrapper, name, key, positions_double)
            check_pos = positions_double
        else:
            print("No correct positioning type: valid are \"abs\" and \"rel\"")
            return

        # move the joints
        write_method(target_pos, positioning, block)
        time.sleep(2.)

        test_results[name + '_' + key], read[name + '_' + key] = check_method(name, read_method, check_pos[name][key])

    # save the read joint positions
    for key in read:
        np.save(res_path + key + "_" + pos_type + "_" + positioning + ".npy", read[key])

    print("________ Test results: " + pos_type + "_" + positioning)
    for key in test_results:
        print('Test:', key, 'results:', test_results[key])

    print('\n')


#########################################################
def test_joint_positioning(ann_wrapper):
    """
        Test the joint control in case of writing and reading. The results are compared to check the correct movement of the joints.

        params:
            ann_wrapper     -- iCub_ANNarchy Interface
    """
    n_pop = params.n_pop_pos
    sigma = params.sigma_pos
    neuron_res = params.neuron_res_pos
    path = params.path_pos
    position_path = params.position_path_pos

    if not os.path.isdir(path):
        os.mkdir(path)

    print('____________________________________________________________')
    print('__ Load test positions __')

    # load test positions
    positions = {'right_arm':{}, 'left_arm':{}, 'head': {}}
    positions['right_arm']['pos_arm_T_r']       = np.load(position_path + "test_pos_T.npy")
    positions['right_arm']['pos_arm_complex_r'] = np.load(position_path + "test_hand_complex.npy")
    positions['right_arm']['pos_arm_home_r']    = np.load(position_path + "test_pos_home.npy")
    positions['left_arm']['pos_arm_T_l']        = np.load(position_path + "test_pos_T.npy")
    positions['left_arm']['pos_arm_complex_l']  = np.load(position_path + "test_hand_complex.npy")
    positions['left_arm']['pos_arm_home_l']     = np.load(position_path + "test_pos_home.npy")
    positions['head']['pos_head']               = np.load(position_path + "test_pos_head.npy")
    positions['head']['pos_head_complex']       = np.load(position_path + "test_pos_head_complex.npy")
    positions['head']['pos_head_zero']          = np.load(position_path + "test_pos_head_zero.npy")

    # encode positions
    print('__ Encode test positions __')
    part_enc = {'right_arm': {}, 'head': {}, 'left_arm': {}}
    for name in part_enc:
        for key in positions[name]:
            pos_enc = []
            for i in range(positions[name][key].shape[0]):
                positions[name][key][i] = round(positions[name][key][i], 2)
                pos_enc.append(encode(name, i, n_pop, positions[name][key][i], sigma, neuron_res))
            np.save(path + key + "_encoded.npy", pos_enc)
            part_enc[name][key] = pos_enc

    print('____________________________________________________________\n')
    print('__ Add and init joint reader and writer modules __')

    # add joint reader instances
    for name in part_enc:
        ann_wrapper.add_joint_reader(name)

        # add joint writer instances
        ann_wrapper.add_joint_writer(name)
    print('____ Added all joint reader and writer ____')

    # init joint reader
    ann_wrapper.parts_reader["right_arm"].init(ann_wrapper.PART_KEY_RIGHT_ARM, sigma, n_pop, neuron_res)
    ann_wrapper.parts_reader["left_arm"].init(ann_wrapper.PART_KEY_LEFT_ARM, sigma, n_pop, neuron_res)
    ann_wrapper.parts_reader["head"].init(ann_wrapper.PART_KEY_HEAD, sigma, n_pop, neuron_res)

    # init joint writer
    ann_wrapper.parts_writer["right_arm"].init(ann_wrapper.PART_KEY_RIGHT_ARM, n_pop, neuron_res, 25.0)
    ann_wrapper.parts_writer["left_arm"].init(ann_wrapper.PART_KEY_LEFT_ARM, n_pop, neuron_res, 25.0)
    ann_wrapper.parts_writer["head"].init(ann_wrapper.PART_KEY_HEAD, n_pop, neuron_res, 25.0)
    print('____ Initialized all joint reader and writer ____')
    print('____________________________________________________________\n')

    jnts = {}
    jnts['right_arm'] = ann_wrapper.parts_writer["right_arm"].get_joint_count()
    jnts['left_arm'] = ann_wrapper.parts_writer["left_arm"].get_joint_count()
    jnts['head'] = ann_wrapper.parts_writer["head"].get_joint_count()

    jnt_sel = {}
    jnt_sel['right_arm'] = np.array([0, 1, 2, 3, 4], dtype=np.int)
    jnt_sel['left_arm'] = np.array([0, 1, 2, 3, 4], dtype=np.int)
    jnt_sel['head'] = np.array([0, 1, 2], dtype=np.int)

    # test the positioning with double values for a motion of per single, multiple and all joints
    for name in part_enc:
        print('____ Test part:', name)
        print('__ Type of positioning: Double single')
        write_joint_each(ann_wrapper, "double_single", "abs", True, name, positions, ann_wrapper.parts_writer[name].write_double_one, ann_wrapper.parts_reader[name].read_double_one, check_position_double_mult, path, jnts)
        write_joint_each(ann_wrapper, "double_single", "rel", True, name, positions, ann_wrapper.parts_writer[name].write_double_one, ann_wrapper.parts_reader[name].read_double_one, check_position_double_mult, path, jnts, rel_pos_double, positions)

        print('__ Type of positioning: Double multiple')
        write_joint_mult(ann_wrapper, "double_mult", "abs", True, name, positions, ann_wrapper.parts_writer[name].write_double_multiple, ann_wrapper.parts_reader[name].read_double_one, check_position_double_mult, path, jnt_sel)
        write_joint_mult(ann_wrapper, "double_mult", "rel", True, name, positions, ann_wrapper.parts_writer[name].write_double_multiple, ann_wrapper.parts_reader[name].read_double_one, check_position_double_mult, path, jnt_sel, rel_pos_double, positions)

        print('__ Type of positioning: Double all')
        write_joint_all(ann_wrapper, "double_all", "abs", True, name, positions, ann_wrapper.parts_writer[name].write_double_all, ann_wrapper.parts_reader[name].read_double_all, check_position_double_all, path)
        write_joint_all(ann_wrapper, "double_all", "rel", True, name, positions, ann_wrapper.parts_writer[name].write_double_all, ann_wrapper.parts_reader[name].read_double_all, check_position_double_all, path, rel_pos_double, positions)


        # TODO: relative motion: problems with joint position
        # test the positioning with population coding for per single joint, multiple and all joints
        print('__ Type of positioning: Population single')
        write_joint_each(ann_wrapper, "pop_single", "abs", True, name, part_enc, ann_wrapper.parts_writer[name].write_pop_one, ann_wrapper.parts_reader[name].read_pop_one, check_position_pop_mult, path, jnts)
        # write_joint_each(ann_wrapper, "pop_single", "rel", True, name, part_enc, ann_wrapper.parts_writer[name].write_pop_one, ann_wrapper.parts_reader[name].read_pop_one, check_position_pop_mult, path, jnts, rel_pos_pop, positions)

        print('__ Type of positioning: Population multiple')
        # write_joint_mult(ann_wrapper, "pop_mult", "abs", True, name, part_enc, ann_wrapper.parts_writer[name].write_pop_multiple, ann_wrapper.parts_reader[name].read_pop_one, check_position_pop_mult, path, jnt_sel)
        # write_joint_mult(ann_wrapper, "pop_mult", "rel", True, name, part_enc, ann_wrapper.parts_writer[name].write_pop_multiple, ann_wrapper.parts_reader[name].read_pop_one, check_position_pop_mult, path, jnt_sel, rel_pos_pop, positions)

        print('__ Type of positioning: Population all')
        write_joint_all(ann_wrapper, "pop_all", "abs", True, name, part_enc, ann_wrapper.parts_writer[name].write_pop_all, ann_wrapper.parts_reader[name].read_pop_all, check_position_pop_all, path)
        # write_joint_all(ann_wrapper, "pop_all", "rel", True, name, part_enc, ann_wrapper.parts_writer[name].write_pop_all, ann_wrapper.parts_reader[name].read_pop_all, check_position_pop_all, path, rel_pos_pop, positions)


    print('____________________________________________________________\n')

    # close joint reader and writer instances
    print('__ Close joint reader and writer modules __')
    for part in part_enc:
        ann_wrapper.parts_reader[part].close()
        ann_wrapper.parts_writer[part].close()

    print('____ Closed joint reader and writer modules ____')
    print('____________________________________________________________\n')


#########################################################
def test_tactile_reading(ann_wrapper):
    """
        Test the tactile sensing module of the interface, by touching the robot arm with a sphere at multiple points.

        params:
            ann_wrapper     -- iCub_ANNarchy Interface
    """
    data_count = 5

    path = "./results/Tactile/"
    if not os.path.isdir(path):
        os.mkdir(path)

    # set sphere positions
    loc_sph = []
    loc_p0 = np.array([-0.0, 0.6, 0.22])
    loc_p1 = np.array([-0.14, 0.6, 0.22])
    loc_p2 = np.array([-0.26, 0.62, 0.12])
    loc_p3 = np.array([-0.1975, 0.62, 0.12])
    loc_p4 = np.array([-0.25, 0.7, 0.05])
    loc_p5 = np.array([-0.18, 0.715, 0.04])
    loc_sph.append(loc_p0)
    loc_sph.append(loc_p1)
    loc_sph.append(loc_p2)
    loc_sph.append(loc_p3)
    loc_sph.append(loc_p4)
    loc_sph.append(loc_p5)

    # instanciate the simulator world controller
    sim_ctrl = iSim_wc.WorldController()

    # create a sphere in the simulator
    sphere = sim_ctrl.create_object("ssph", [0.025], loc_p0, [0.0, 0.0, 1.0])

    print('____________________________________________________________')
    print('__ Add and init skin reader module __')

    # add skin reader instances
    ann_wrapper.add_skin_reader("S_Reader")
    ann_wrapper.add_skin_reader("S_Reader1")

    # init skin reader
    print("Init:", ann_wrapper.tactile_reader["S_Reader"].init("r", True))
    print("Init:", ann_wrapper.tactile_reader["S_Reader1"].init("r", False))

    print('____ Initialized skin reader ____')
    print('____________________________________________________________\n')
    data_arm_norm = []
    data_farm_norm = []
    data_hand_norm = []
    pos = loc_p0
    # test the tactile sensing
    for i in range(len(loc_sph) - 1):
        print("step:", i)
        delta_pos = loc_sph[i+1] - pos
        d_pos = delta_pos/data_count
        if d_pos.sum() != 0:
            for j in range(data_count):
                pos += d_pos
                # move the sphere in the simulator
                sim_ctrl.move_object(sphere, pos)
                time.sleep(0.1)

                # read the tactile information from the sensors
                ann_wrapper.tactile_reader["S_Reader"].read_tactile()
                ann_wrapper.tactile_reader["S_Reader1"].read_tactile()

                # return the read data from the interface
                data_arm_norm.append(np.array(ann_wrapper.tactile_reader["S_Reader"].get_tactile_arm()))
                data_farm_norm.append(np.array(ann_wrapper.tactile_reader["S_Reader"].get_tactile_forearm()))
                data_hand_norm.append(np.array(ann_wrapper.tactile_reader["S_Reader"].get_tactile_hand()))

                time.sleep(0.1)
                if np.equal(pos, loc_p1).all():
                    pos = loc_p2
                    sim_ctrl.move_object(sphere, pos)

    # return the read data from the interface
    data_arm_raw = np.array(ann_wrapper.tactile_reader["S_Reader1"].get_tactile_arm())
    data_farm_raw = np.array(ann_wrapper.tactile_reader["S_Reader1"].get_tactile_forearm())
    data_hand_raw = np.array(ann_wrapper.tactile_reader["S_Reader1"].get_tactile_hand())

    print("Finished tactile sensing process")

    print("________ Test results:")
    print(" Touched arm:\n   ", "norm data:", np.array(data_arm_norm).max() == 1.0, "\n    raw data:", data_arm_raw.max() == 255.0)
    print(" Touched forearm:\n   ", "norm data:", np.array(data_farm_norm).max() == 1.0, "\n    raw data:", data_farm_raw.max() == 255.0)
    print(" Touched hand:\n   ", "norm data:", np.array(data_hand_norm).max() == 1.0, "\n    raw data:", data_hand_raw.max() == 255.)

    # save the tactile data normalized and raw
    np.save(path + "tact_arm_data_norm.npy", data_arm_norm)
    np.save(path + "tact_forearm_data_norm.npy", data_farm_norm)
    np.save(path + "tact_hand_data_norm.npy", data_hand_norm)

    np.save(path + "tact_arm_data_raw.npy", data_arm_raw)
    np.save(path + "tact_forearm_data_raw.npy", data_farm_raw)
    np.save(path + "tact_hand_data_raw.npy", data_hand_raw)
    print('____________________________________________________________')
    print('__ Close skin reader module __')

    # close skin reader
    ann_wrapper.tactile_reader["S_Reader"].close()
    ann_wrapper.tactile_reader["S_Reader1"].close()

    # remove all objects from the simulator and delete the world controller
    sim_ctrl.del_all()
    del sim_ctrl


#########################################################
def test_visual_perception(ann_wrapper):
    """
        Test the visual perception module, by presenting the iCub several objects and save the recorded images.

        params:
            ann_wrapper     -- iCub_ANNarchy Interface
    """
    fov_w = 60
    fov_h = 48
    img_w = 320
    img_h = 240

    path = "./Vision/"
    if not os.path.isdir(path):
        os.mkdir(path)

    if(params.gazebo):
        # instanciate the simulator world controller
        sim_ctrl = gzbo_wc.WorldController()

        # create a sphere and a box object in the simulator
        box = sim_ctrl.create_object("box", [0.1, 0.1, 0.1], params.loc_box, [0.0, 0., 0.], [255, 0, 0])
        sphere = sim_ctrl.create_object("sphere", [0.05], params.loc_sph, [0.0, 0., 0.], [0, 0, 255])
    else:
        # instanciate the simulator world controller
        sim_ctrl = iSim_wc.WorldController()

        # create a sphere and a box object in the simulator
        box = sim_ctrl.create_object("sbox", [0.1, 0.1, 0.1], params.loc_box, [255, 0, 0])
        sphere = sim_ctrl.create_object("ssph", [0.05], params.loc_sph, [0, 0, 255])

    print('____________________________________________________________')
    print('__ Add and init visual reader module __')

    # add visual reader instance
    ann_wrapper.add_visual_reader()

    # init visual reader
    ann_wrapper.visual_input.init('r', fov_w, fov_h, img_w, img_h)

    print('____ Initialized visual reader ____')
    print('____________________________________________________________\n')

    # start the RFModule to obtain the images from the iCub
    read_imgs = []
    ann_wrapper.visual_input.start()
    time.sleep(0.15)
    if(params.gazebo):
        # move the sphere object
        params.loc_sph[2] = 0.75
        sim_ctrl.set_pose(sphere, params.loc_sph, [0., 0., 0.])
    else:
        # move the sphere object
        params.loc_sph[1] = 0.75
        sim_ctrl.move_object(sphere, params.loc_sph)
    time.sleep(0.35)

    print('____ Obtain visual information ____')
    t = 0
    t_start = time.time()
    while len(read_imgs) < params.img_count or t > 10.0:
        t = time.time() - t_start
        read_img = ann_wrapper.visual_input.read_fromBuf()
        if read_img.shape[0] > 0:
            print('Obtained new image.')
            read_img = read_img.reshape(img_h, img_w).T
            read_imgs.append(read_img)
        # else:
        #     print('No buffered image!')
    print(round(t, 4), 's')
    # store the recorded images
    np.save(path + 'Vision_full_size.npy', read_imgs)

    print('____________________________________________________________')
    print('__ Stop and close visual reader module __')
    ann_wrapper.visual_input.stop()

    # remove all objects in the simulator and remove the world controller
    sim_ctrl.del_all()
    del sim_ctrl


#########################################################
if __name__ == "__main__":
    wrapper = iCub_Interface.iCubANN_wrapper()

    if len(sys.argv) > 1:
        for command in sys.argv[1:]:
            if command == 'all':
                test_joint_positioning(wrapper)
                test_visual_perception(wrapper)
                test_tactile_reading(wrapper)
            elif command == "positioning":
                test_joint_positioning(wrapper)
            elif command == "tactile":
                test_tactile_reading(wrapper)
            elif command == "vision":
                test_visual_perception(wrapper)
            else:
                print('No valid test command! Possible are: all; positioning; tactile; vision')
    else:
        print('No valid test command! Possible are: all; positioning; tactile; vision')

    del wrapper
    print('Finished automated tests.')
