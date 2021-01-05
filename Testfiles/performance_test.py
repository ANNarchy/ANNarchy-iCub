"""
 *  Copyright (C) 2019-2021 Torsten Fietzek
 *
 *  performance_test.py is part of the iCub ANNarchy interface
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
import iCub_Interface  # requires iCub_Interface in the present directory

# Python libraries for simulator control
import iCub_Python_Lib.iCubSim_world_controller as iSim_wc
import iCub_Python_Lib.gazebo_world_controller as gzbo_wc

# Test support files
import supplementary.testing_parameter as params
from supplementary.auxilary_methods import encode

####################### parameter #######################
bog2deg = 180.0 / np.pi         # factor for radiant to degree conversion
eye_distance = 0.07             # distance between left and right eye
eye_loc = [0.0, 0.9375, 0.055]  # location of the center point between both eyes

#########################################################
def speed_test_jreader(ann_wrapper, test_count):
    """
        Test the performance of the joint reader module.

        params:
            ann_wrapper     -- iCub_ANNarchy Interface
            test_count      -- number of test trials
    """

    n_pop = params.n_pop_jr         # population size
    sigma = params.sigma_jr         # sigma for population coding gaussian
    neuron_res = params.neuron_res_jr    # population resolution
    parts = params.parts   # tested iCub parts

    print('____________________________________________________________\n')
    print('__ Add and init joint reader modules __')

    # add joint reader instances
    ann_wrapper.add_joint_reader("right_arm")
    ann_wrapper.add_joint_reader("head")

    print('____ Added all joint reader ____')

    # init joint reader
    ann_wrapper.parts_reader["right_arm"].init(ann_wrapper.PART_KEY_RIGHT_ARM, sigma, n_pop, neuron_res)
    ann_wrapper.parts_reader["head"].init(ann_wrapper.PART_KEY_HEAD, sigma, n_pop, neuron_res)

    print('____ Initialized all joint reader and writer ____')
    print('____________________________________________________________\n')

    # test speed for reading joint angles as double values
    print('__ Type of reading: Double_one')
    results_double_one = {}
    for name in parts:
        print('____ Test part:', name)
        joints = ann_wrapper.parts_reader[name].get_joint_count()
        print(joints)
        read_pos_double = np.zeros((test_count, joints))
        time_start_double = time.time()
        for i in range(test_count):
            for j in range(joints):
                read_pos_double[i, j] = ann_wrapper.parts_reader[name].read_double_one(j)
        time_stop_double = time.time()
        print(np.round(read_pos_double, 2))
        results_double_one[name] = (time_stop_double - time_start_double) / (test_count*joints)

    # show the test results
    print('________ Test results: Double_one')
    for part in results_double_one:
        print("Time double ", part, ":", round(results_double_one[part] * 1000., 4), 'ms')
    print('\n')

    # test speed for reading joint angles as population code, coding all joints combined
    print('__ Type of reading: Double_all')
    results_double_all = {}
    for name in parts:
        print('____ Test part:', name)
        joints = ann_wrapper.parts_reader[name].get_joint_count()
        read_pos_double_all = np.zeros((test_count, joints))
        time_start_double_all = time.time()
        for i in range(test_count):
            read_pos_double_all[i] = ann_wrapper.parts_reader[name].read_double_all()
        time_stop_double_all = time.time()
        print(np.round(read_pos_double_all, 2))
        results_double_all[name] = (time_stop_double_all - time_start_double_all) / test_count

    # show the test results
    print('________ Test results: Double_all')
    for part in results_double_all:
        print("Time Double_all", part , ":", round(results_double_all[part] * 1000., 4), 'ms')
    print('\n')

    # test speed for reading joint angles as population code, coding a single joint
    print('__ Type of reading: Population_one')
    results_pop_single = {}
    for name in parts:
        print('____ Test part:', name)
        joints = ann_wrapper.parts_reader[name].get_joint_count()
        read_pos_pop_single = np.zeros((joints, n_pop))
        time_start_pop_single = time.time()
        for i in range(test_count):
            for j in range(joints):
                read_pos_pop_single[i] = ann_wrapper.parts_reader[name].read_pop_one(j)
        time_stop_pop_single = time.time()
        results_pop_single[name] = (time_stop_pop_single - time_start_pop_single) / test_count

    # show the test results
    print('________ Test results: Population_one')
    for part in results_pop_single:
        print("Time pop_single", part , ":", round(results_pop_single[part], 4), 's')
    print('\n')

    # test speed for reading joint angles as population code, coding all joints combined
    print('__ Type of reading: Population_all')
    results_pop_all = {}
    for name in parts:
        print('____ Test part:', name)
        joints = ann_wrapper.parts_reader[name].get_joint_count()
        time_start_pop_all = time.time()
        for i in range(test_count):
            read_pos_pop_all = ann_wrapper.parts_reader[name].read_pop_all()
        time_stop_pop_all = time.time()
        results_pop_all[name] = (time_stop_pop_all - time_start_pop_all) / test_count

    # show the test results
    print('________ Test results: Population_all')
    for part in results_pop_all:
        print("Time pop_all", part , ":", round(results_pop_all[part], 4), 's')
    print('\n')

    print('____________________________________________________________\n')

    # close joint reader
    print('__ Close joint reader modules __')
    for part in parts:
        ann_wrapper.parts_reader[part].close()

    print('____ Closed joint reader modules ____')
    print('____________________________________________________________\n')


#########################################################
def speed_test_jwriter(ann_wrapper, test_count):
    """
        Test the performance of the joint writer module.

        params:
            ann_wrapper     -- iCub_ANNarchy Interface
            test_count      -- number of test trials
    """

    n_pop = params.n_pop_jw             # population size
    sigma = params.sigma_jw             # sigma for population coding gaussian
    neuron_res = params.neuron_res_jw   # population resolution
    position_path = params.position_path

    print('____________________________________________________________')
    print('__ Load test positions __')

    # load test positions
    positions = {}
    positions['pos_arm_T_r'] = (np.load(position_path + "test_pos_T.npy"), 'right_arm')
    positions['pos_arm_complex_r'] = (np.load(position_path + "test_hand_complex.npy"), 'right_arm')
    positions['pos_arm_home_r'] = (np.load(position_path + "test_pos_home.npy"), 'right_arm')
    positions['pos_head'] = (np.load(position_path + "test_pos_head.npy"), 'head')
    positions['pos_head_complex'] = (np.load(position_path + "test_pos_head_complex.npy"), 'head')
    positions['pos_head_zero'] = (np.load(position_path + "test_pos_head_zero.npy"), 'head')

    zero_pos = {}
    zero_pos['head'] = np.zeros(6)
    zero_pos['right_arm'] = np.load(position_path + "zero_pos_arm.npy")

    for idx, data in enumerate(positions):
        print(idx, positions[data][0])
    for idx, data in enumerate(zero_pos):
        print(idx, zero_pos[data][0])

    # delta positions
    deltas = {}
    deltas['pos_arm_T_r'] = (positions['pos_arm_T_r'][0] - zero_pos['right_arm'], 'right_arm')
    deltas['pos_arm_complex_r'] = (positions['pos_arm_complex_r'][0] - zero_pos['right_arm'], 'right_arm')
    deltas['pos_arm_home_r'] = (positions['pos_arm_home_r'][0] - zero_pos['right_arm'], 'right_arm')
    deltas['pos_head'] = (positions['pos_head'][0] - zero_pos['head'], 'head')
    deltas['pos_head_complex'] = (positions['pos_head_complex'][0] - zero_pos['head'], 'head')
    deltas['pos_head_zero'] = (positions['pos_head_zero'][0] - zero_pos['head'], 'head')

    # encode absolute positions
    print('__ Encode test positions __')
    part_enc = {'right_arm': {}, 'head': {}}
    for key in positions:
        pos_enc = []
        for i in range(positions[key][0].shape[0]):
            positions[key][0][i] = round(positions[key][0][i], 2)
            pos_enc.append(encode(positions[key][1], i, n_pop, positions[key][0][i], sigma, neuron_res))
        part_enc[positions[key][1]][key] = pos_enc

    # encode relative positions
    print('__ Encode test positions __')
    part_enc_delta = {'right_arm': {}, 'head': {}}
    for key in deltas:
        pos_enc = []
        for i in range(deltas[key][0].shape[0]):
            deltas[key][0][i] = round(deltas[key][0][i], 2)
            pos_enc.append(encode(deltas[key][1], i, n_pop, deltas[key][0][i], sigma, neuron_res, relative=True))
        part_enc_delta[deltas[key][1]][key] = pos_enc

    print('____________________________________________________________\n')
    print('__ Add and init joint writer modules __')

    # add joint writer instances
    for name in part_enc:
        ann_wrapper.add_joint_writer(name)
    print('____ Added all joint writer ____')

    # init joint writer instances
    ann_wrapper.parts_writer["right_arm"].init(ann_wrapper.PART_KEY_RIGHT_ARM, n_pop, neuron_res, 100.0)
    ann_wrapper.parts_writer["head"].init(ann_wrapper.PART_KEY_HEAD, n_pop, neuron_res, 100.0)
    print('____ Initialized all joint writer ____')
    print('____________________________________________________________\n')

    #########################################################
    # test joint motion with the joint angle as double value for one joint (absolute position)
    print('__ Type of positioning: Double_one (absolute)')
    results_double_one = {}
    for name in part_enc:
        joints = ann_wrapper.parts_writer[name].get_joint_count()
        print('____ Test part:', name)
        for key in positions:
            if positions[key][1] == name:
                print('______ Test position:', key)
                results_double_one[name + '_' + key] = 0
                for i in range(test_count):
                    time_start = time.time()
                    for j in range(joints):
                        ann_wrapper.parts_writer[name].write_double_one(positions[key][0][j], j, "abs", True)
                    time_stop = time.time()
                    results_double_one[name + '_' + key] += time_stop -time_start

                    for j in range(joints):
                        ann_wrapper.parts_writer[name].write_double_one(zero_pos[name][j], j, "abs", True)
                    time.sleep(0.5)
                results_double_one[name + '_' + key] /= test_count

    # show test results
    print('________ Test results: Double_one (absolute)')
    for key in results_double_one:
        print('Test:', key, 'results:', round(results_double_one[key], 4), 's')
    print('\n')

    # test joint motion with the joint angles as double values for multiple joints (absolute position)
    print('__ Type of positioning: Double_multiple (absolute)')
    results_double_multiple = {}
    for name in part_enc:
        joints = ann_wrapper.parts_writer[name].get_joint_count()
        print('____ Test part:', name)
        for key in positions:
            if positions[key][1] == name:
                print('______ Test position:', key)
                results_double_multiple[name + '_' + key] = 0
                for i in range(test_count):
                    time_start = time.time()
                    ann_wrapper.parts_writer[name].write_double_multiple(positions[key][0][3:6], range(3, 6), "abs", True)
                    time_stop = time.time()
                    results_double_multiple[name + '_' + key] += time_stop -time_start

                    ann_wrapper.parts_writer[name].write_double_all(zero_pos[name], "abs", True)
                    time.sleep(0.5)
                results_double_multiple[name + '_' + key] /= test_count

    # show test results
    print('________ Test results: Double_multiple (absolute)')
    for key in results_double_one:
        print('Test:', key, 'results:', round(results_double_multiple[key], 4), 's')
    print('\n')

    # test joint motion with the joint angles as double values for all joints (absolute position)
    print('__ Type of positioning: Double_all (absolute)')
    results_double_all = {}
    for name in part_enc:
        joints = ann_wrapper.parts_writer[name].get_joint_count()
        print('____ Test part:', name)
        for key in positions:
            if positions[key][1] == name:
                print('______ Test position:', key)
                results_double_all[name + '_' + key] = 0
                for i in range(test_count):
                    time_start = time.time()
                    ann_wrapper.parts_writer[name].write_double_all(positions[key][0], "abs", True)
                    time_stop = time.time()
                    results_double_all[name + '_' + key] += time_stop -time_start

                    ann_wrapper.parts_writer[name].write_double_all(zero_pos[name], "abs", True)
                    time.sleep(0.5)
                results_double_all[name + '_' + key] /= test_count

    # show test results
    print('________ Test results: Double_all (absolute)')
    for key in results_double_all:
        print('Test:', key, 'results:', round(results_double_all[key], 4), 's')
    print('\n')

    #########################################################
    # test joint motion with joint angles encoded in population code, coding single joint (absolute position)
    print('__ Type of positioning: Population_one (absolute)')
    results_pop_one = {}
    for name in part_enc:
        joints = ann_wrapper.parts_writer[name].get_joint_count()
        print('____ Test part:', name)
        for key in part_enc[name]:
            print('______ Test position:', key)
            results_pop_one[name + '_' + key] = 0
            for i in range(test_count):
                time_start = time.time()
                for j in range(joints):
                    ann_wrapper.parts_writer[name].write_pop_one(part_enc[name][key][j], j, "abs", True)
                time_stop = time.time()
                results_pop_one[name + '_' + key] += time_stop -time_start

                ann_wrapper.parts_writer[name].write_double_all(zero_pos[name], "abs", True)
                time.sleep(0.5)
            results_pop_one[name + '_' + key] /= test_count

    # show test results
    print('________ Test results: Population_one (absolute)')
    for key in results_pop_one:
        print('Test:', key, 'results:', round(results_pop_one[key], 4), 's')
    print('\n')

    # test joint motion with joint angles encoded in population code, coding multiple joints combined (absolute position)
    print('__ Type of positioning: Population_multiple (absolute)')
    results_pop_multiple = {}
    for name in part_enc:
        joints = ann_wrapper.parts_writer[name].get_joint_count()
        print('____ Test part:', name)
        for key in part_enc[name]:
            print('______ Test position:', key)
            results_pop_multiple[name + '_' + key] = 0
            for i in range(test_count):
                time_start = time.time()
                ann_wrapper.parts_writer[name].write_pop_multiple(part_enc[name][key][3:6], range(3, 6), "abs", True)
                time_stop = time.time()
                results_pop_multiple[name + '_' + key] += time_stop -time_start

                ann_wrapper.parts_writer[name].write_double_all(zero_pos[name], "abs", True)
                time.sleep(0.5)
            results_pop_multiple[name + '_' + key] /= test_count

    # show test results
    print('________ Test results: Population_multiple (absolute)')
    for key in results_pop_multiple:
        print('Test:', key, 'results:', round(results_pop_multiple[key], 4), 's')
    print('\n')

    # test joint motion with joint angles encoded in population code, coding all joints combined (absolute position)
    print('__ Type of positioning: Population_all (absolute)')
    results_pop_all = {}
    for name in part_enc:
        print('____ Test part:', name)
        for key in part_enc[name]:
            print('______ Test position:', key)
            results_pop_all[name + '_' + key] = 0
            for i in range(test_count):
                time_start = time.time()
                ann_wrapper.parts_writer[name].write_pop_all(part_enc[name][key], "abs", True)
                time_stop = time.time()
                results_pop_all[name + '_' + key] += time_stop -time_start

                ann_wrapper.parts_writer[name].write_double_all(zero_pos[name], "abs", True)
                time.sleep(0.5)
            results_pop_all[name + '_' + key] /= test_count

    # show test results
    print('________ Test results: Population_all (absolute)')
    for key in results_pop_all:
        print('Test:', key, 'results:', round(results_pop_all[key], 4), 's')
    print('\n')

    #########################################################
    # test joint motion with the joint angle as double value for one joint (relative position)
    print('__ Type of positioning: Double_one (relative)')
    results_double_one = {}
    for name in part_enc:
        joints = ann_wrapper.parts_writer[name].get_joint_count()
        print('____ Test part:', name)
        for key in positions:
            if positions[key][1] == name:
                print('______ Test position:', key)
                results_double_one[name + '_' + key] = 0
                for i in range(test_count):
                    time_start = time.time()
                    for j in range(joints):
                        ann_wrapper.parts_writer[name].write_double_one(deltas[key][0][j], j, "rel", True)
                    time_stop = time.time()
                    results_double_one[name + '_' + key] += time_stop -time_start

                    for j in range(joints):
                        ann_wrapper.parts_writer[name].write_double_one(zero_pos[name][j], j, "abs", True)
                    time.sleep(0.5)
                results_double_one[name + '_' + key] /= test_count

    # show test results
    print('________ Test results: Double_one (relative)')
    for key in results_double_one:
        print('Test:', key, 'results:', round(results_double_one[key], 4), 's')
    print('\n')

    # test joint motion with the joint angles as double values for multiple joints (relative position)
    print('__ Type of positioning: Double_multiple (relative)')
    results_double_multiple = {}
    for name in part_enc:
        joints = ann_wrapper.parts_writer[name].get_joint_count()
        print('____ Test part:', name)
        for key in positions:
            if positions[key][1] == name:
                print('______ Test position:', key)
                results_double_multiple[name + '_' + key] = 0
                for i in range(test_count):
                    time_start = time.time()
                    ann_wrapper.parts_writer[name].write_double_multiple(deltas[key][0][3:6], range(3, 6), "rel", True)
                    time_stop = time.time()
                    results_double_multiple[name + '_' + key] += time_stop -time_start

                    ann_wrapper.parts_writer[name].write_double_all(zero_pos[name], "abs", True)
                    time.sleep(0.5)
                results_double_multiple[name + '_' + key] /= test_count

    # show test results
    print('________ Test results: Double_multiple (relative)')
    for key in results_double_one:
        print('Test:', key, 'results:', round(results_double_multiple[key], 4), 's')
    print('\n')

    # test joint motion with the joint angles as double values for all joints (relative position)
    print('__ Type of positioning: Double_all (relative)')
    results_double_all = {}
    for name in part_enc:
        joints = ann_wrapper.parts_writer[name].get_joint_count()
        print('____ Test part:', name)
        for key in positions:
            if positions[key][1] == name:
                print('______ Test position:', key)
                results_double_all[name + '_' + key] = 0
                for i in range(test_count):
                    time_start = time.time()
                    ann_wrapper.parts_writer[name].write_double_all(deltas[key][0], "rel", True)
                    time_stop = time.time()
                    results_double_all[name + '_' + key] += time_stop -time_start

                    ann_wrapper.parts_writer[name].write_double_all(zero_pos[name], "abs", True)
                    time.sleep(0.5)
                results_double_all[name + '_' + key] /= test_count

    # show test results
    print('________ Test results: Double_all (relative)')
    for key in results_double_all:
        print('Test:', key, 'results:', round(results_double_all[key], 4), 's')
    print('\n')

    #########################################################
    # test joint motion with joint angles encoded in population code, coding single joint (relative position)
    print('__ Type of positioning: Population_one (relative)')
    results_pop_one = {}
    for name in part_enc:
        joints = ann_wrapper.parts_writer[name].get_joint_count()
        print('____ Test part:', name)
        for key in part_enc[name]:
            print('______ Test position:', key)
            results_pop_one[name + '_' + key] = 0
            for i in range(test_count):
                time_start = time.time()
                for i in range(joints):
                    ann_wrapper.parts_writer[name].write_pop_one(part_enc_delta[name][key][i], i, "rel", True)
                time_stop = time.time()
                results_pop_one[name + '_' + key] += time_stop -time_start

                ann_wrapper.parts_writer[name].write_double_all(zero_pos[name], "abs", True)
                time.sleep(0.5)
            results_pop_one[name + '_' + key] /= test_count

    # show test results
    print('________ Test results: Population_one (relative)')
    for key in results_pop_one:
        print('Test:', key, 'results:', round(results_pop_one[key], 4), 's')
    print('\n')

    # test joint motion with joint angles encoded in population code, coding multiple joints combined (relative position)
    print('__ Type of positioning: Population_multiple (relative)')
    results_pop_multiple = {}
    for name in part_enc:
        joints = ann_wrapper.parts_writer[name].get_joint_count()
        print('____ Test part:', name)
        for key in part_enc[name]:
            print('______ Test position:', key)
            results_pop_multiple[name + '_' + key] = 0
            for i in range(test_count):
                time_start = time.time()
                ann_wrapper.parts_writer[name].write_pop_multiple(part_enc_delta[name][key][3:6], range(3, 6), "rel", True)
                time_stop = time.time()
                results_pop_multiple[name + '_' + key] += time_stop -time_start

                ann_wrapper.parts_writer[name].write_double_all(zero_pos[name], "abs", True)
                time.sleep(0.5)
            results_pop_multiple[name + '_' + key] /= test_count

    # show test results
    print('________ Test results: Population_multiple (relative)')
    for key in results_pop_multiple:
        print('Test:', key, 'results:', round(results_pop_multiple[key], 4), 's')
    print('\n')

    # test joint motion with joint angles encoded in population code, coding all joints combined (relative position)
    print('__ Type of positioning: Population_all (relative)')
    results_pop_all = {}
    for name in part_enc:
        print('____ Test part:', name)
        for key in part_enc[name]:
            print('______ Test position:', key)
            results_pop_all[name + '_' + key] = 0
            for i in range(test_count):
                time_start = time.time()
                ann_wrapper.parts_writer[name].write_pop_all(part_enc_delta[name][key], "rel", True)
                time_stop = time.time()
                results_pop_all[name + '_' + key] += time_stop -time_start

                ann_wrapper.parts_writer[name].write_double_all(zero_pos[name], "abs", True)
                time.sleep(0.5)
            results_pop_all[name + '_' + key] /= test_count

    # show test results
    print('________ Test results: Population_all (relative)')
    for key in results_pop_all:
        print('Test:', key, 'results:', round(results_pop_all[key], 4), 's')

    #########################################################

    print('____________________________________________________________\n')
    print('__ Close joint writer modules __')

    # close joint writer instances
    for part in part_enc:
        ann_wrapper.parts_writer[part].close()

    print('____ Closed joint writer modules ____')
    print('____________________________________________________________\n')


#########################################################
def speed_test_sreader(ann_wrapper, test_count):
    """
        Test the performance of the skin reader module.

        params:
            ann_wrapper     -- iCub_ANNarchy Interface
            test_count      -- number of test trials
    """

    print('____________________________________________________________')
    print('__ Add and init skin reader module __')
    # add skin reader instances
    ann_wrapper.add_skin_reader("S_Reader")
    ann_wrapper.add_skin_reader("S_Reader1")

    # init skin reader
    print("Init:", ann_wrapper.tactile_reader["S_Reader"].init("r", True)) # normalized
    print("Init:", ann_wrapper.tactile_reader["S_Reader1"].init("r", False)) # non-normalized

    print('____ Initialized skin reader ____')
    print('____________________________________________________________\n')


    print('____ Test speed performance with normalization ____')
    t_start_norm = time.time()
    for i in range(test_count):
        ann_wrapper.tactile_reader["S_Reader"].read_tactile()
    t_stop_norm = time.time()

    data_arm_norm = np.array(ann_wrapper.tactile_reader["S_Reader"].get_tactile_arm())
    data_farm_norm = np.array(ann_wrapper.tactile_reader["S_Reader"].get_tactile_forearm())
    data_hand_norm = np.array(ann_wrapper.tactile_reader["S_Reader"].get_tactile_hand())


    print('____ Test speed performance without normalization ____')
    t_start_non_norm = time.time()
    for i in range(test_count):
        ann_wrapper.tactile_reader["S_Reader"].read_tactile()
    t_stop_non_norm = time.time()

    data_arm_non_norm = np.array(ann_wrapper.tactile_reader["S_Reader1"].get_tactile_arm())
    data_farm_non_norm = np.array(ann_wrapper.tactile_reader["S_Reader1"].get_tactile_forearm())
    data_hand_non_norm = np.array(ann_wrapper.tactile_reader["S_Reader1"].get_tactile_hand())

    print('____________________________________________________________')
    print('__ Close skin reader module __')

    # close skin reader
    print(ann_wrapper.tactile_reader["S_Reader"].close())
    print(ann_wrapper.tactile_reader["S_Reader1"].close())


    print('____________________________________________________________')
    print('__ Results __')

    print("Data shape normalized data:", data_arm_norm.shape, data_farm_norm.shape, data_hand_norm.shape)
    print("Data shape non-normalized data:", data_arm_non_norm.shape, data_farm_non_norm.shape, data_hand_non_norm.shape)

    print('Time with normalized data:', (t_stop_norm - t_start_norm)/test_count, "s")
    print('Time with non-normalized data:', (t_stop_non_norm - t_start_non_norm)/test_count, "s")


#########################################################
def speed_test_vreader(ann_wrapper, test_count):
    """
        Test the performance of the visual reader module.

        params:
            ann_wrapper     -- iCub_ANNarchy Interface
            test_count      -- number of test trials
    """

    imgs_full = []
    imgs_quarter = []
    imgs_field = []

    path = params.save_path_vr
    if not os.path.isdir(path):
        os.mkdir(path)

    print('____________________________________________________________')
    print('__ Add and init visual reader module with full resolution __')
    # add visual reader instance
    ann_wrapper.add_visual_reader()

    # init visual reader
    print(ann_wrapper.visual_input.init('r'))                    # use of default values
    print('____ Initialized visual reader ____')
    print('____________________________________________________________\n')

    print('____ Test speed performance with full resolution ____')
    t_start_full = time.time()
    ann_wrapper.visual_input.start()
    while len(imgs_full) < test_count:
        img_full = ann_wrapper.visual_input.read_from_buffer()
        if img_full.shape[0] != 0:
            imgs_full.append(img_full)
    t_stop_full = time.time()

    print('____________________________________________________________')
    print('__ Stop and close visual reader module __')
    ann_wrapper.visual_input.stop()
    ann_wrapper.rm_visual_reader()

    # store obtained images
    np.save(path + 'full_size.npy', img_full)

    time.sleep(1.0)
    # add visual reader instance
    ann_wrapper.add_visual_reader()

    print('____________________________________________________________')
    print('__ Reinit visual reader module with quarter resolution __')
    print(ann_wrapper.visual_input.init('r', 60, 48, 80, 60))    # lower resolution
    print('____ Initialized visual reader ____')
    print('____________________________________________________________\n')

    print('____ Test speed performance with quarter resolution ____')
    t_start_quart = time.time()
    ann_wrapper.visual_input.start()
    while len(imgs_quarter) < test_count:
        img_quarter = ann_wrapper.visual_input.read_from_buffer()
        if img_quarter.shape[0] != 0:
            imgs_quarter.append(img_quarter)
    t_stop_quart = time.time()

    print('____________________________________________________________')
    print('__ Stop and close visual reader module __')
    ann_wrapper.visual_input.stop()
    ann_wrapper.rm_visual_reader()

    # store obtained images
    np.save(path + 'quarter_size.npy', img_quarter)

    time.sleep(1.0)
    # add visual reader instance
    ann_wrapper.add_visual_reader()

    print('____________________________________________________________')
    print('__ Reinit visual reader module with half visual field and quarter resolution __')
    print(ann_wrapper.visual_input.init('r', 30, 24, 80, 60))    # lower resolution and smaller visual field
    print('____ Initialized visual reader ____')
    print('____________________________________________________________\n')

    print('____ Test speed performance with quarter resolution and reduced visual field ____')
    t_start_field = time.time()
    ann_wrapper.visual_input.start()
    while len(imgs_field) < test_count:
        img_field = ann_wrapper.visual_input.read_from_buffer()
        if img_field.shape[0] != 0:
            imgs_field.append(img_field)
    t_stop_field = time.time()

    print('____________________________________________________________')
    print('__ Stop and close visual reader module __')
    ann_wrapper.visual_input.stop()

    np.save(path + 'field_size.npy', img_field)

    print('Time with full resolution:', round(1. / ((t_stop_full - t_start_full) / test_count), 4), "fps")
    print('Time with quarter resolution:', round(1.0 / ((t_stop_quart - t_start_quart) / test_count), 4), "fps")
    print('Time with quarter resolution and half visual field:', round(1/ ((t_stop_field - t_start_field) / test_count), 4), "fps")


#########################################################
def vis_move_test(ann_wrapper):
    """
        Test the performance of the visual reader module.

        params:
            ann_wrapper     -- iCub_ANNarchy Interface
            test_count      -- number of test trials
    """
    n_pop = params.n_pop_vm
    speed_arm = params.speed_arm_vm
    speed_head = params.speed_head_vm

    position_path = params.position_path
    pos = {}
    pos[True] = np.load(position_path + "test_vismov0.npy")
    pos[False] = np.load(position_path + "test_vismov1.npy")

    zero_pos = {}
    zero_pos['head'] = np.zeros(6)
    zero_pos['right_arm'] = np.load(position_path + "test_pos_home.npy")

    # create folder to store test results, in case it does not exist already
    path = params.save_path_vm
    if not os.path.isdir(path):
        os.mkdir(path)

    # add visual reader and joint writer instances
    ann_wrapper.add_visual_reader()
    ann_wrapper.add_joint_writer("moving")
    ann_wrapper.add_joint_writer("head")

    # init visual reader and joint writer instances
    ann_wrapper.visual_input.init('r', 60, 48, 80, 60)
    ann_wrapper.parts_writer["moving"].init(ann_wrapper.PART_KEY_RIGHT_ARM, n_pop, speed_arm)
    ann_wrapper.parts_writer["head"].init(ann_wrapper.PART_KEY_HEAD, n_pop, speed_head)

    # move the right arm to the start position
    for i in range(ann_wrapper.parts_writer["moving"].get_joint_count()):
        ann_wrapper.parts_writer["moving"].write_double_one(pos[True][i], i, "abs", True)

    if (params.gazebo):
        hand_loc = [ 0.19, -0.043, 0.67 ]
    else:
        # create a simulator world controller instance
        sim_ctrl = iSim_wc.WorldController()

        # obtain the iCub hand position in the world reference frame
        hand_loc = sim_ctrl.get_hand_location("rhand")

        del sim_ctrl

    # compute the eye and and head position to look the iCub hand
    dx = hand_loc[0] - eye_loc[0]
    dy = hand_loc[1] - eye_loc[1]
    dz = hand_loc[2] - eye_loc[2]

    alpha = bog2deg * np.arctan(dy/dz)
    beta =  - bog2deg * np.arctan(dx/dz)
    target_pos = np.zeros(ann_wrapper.parts_writer["head"].get_joint_count())

    target_pos[0] = 3.0/4.0 * alpha
    target_pos[3] = 1.0/ 4.0 * alpha - 3
    target_pos[2] = -1.0/2.0 * beta
    target_pos[4] = 1.0/2.0 * beta - 10

    # move the head and eyes to look at the iCub right hand
    for i in range(ann_wrapper.parts_writer["head"].get_joint_count()):
        ann_wrapper.parts_writer["head"].write_double_all(target_pos, "abs", True)
    time.sleep(2)

    # start the the visual reader module to obtain images from the iCub
    ann_wrapper.visual_input.start()

    # move the arm, while recording the images
    for i in range(ann_wrapper.parts_writer["moving"].get_joint_count()):
        ann_wrapper.parts_writer["moving"].write_double_all(pos[False], "abs", True)
    imgs = []
    t_start = time.time()
    pos_choice = True
    while len(imgs) < 100:
        imgs.append(np.array(ann_wrapper.visual_input.read_from_buffer()))
        dt = time.time() - t_start
        if dt > 0.5:
            for i in range(ann_wrapper.parts_writer["moving"].get_joint_count()):
                ann_wrapper.parts_writer["moving"].write_double_all(pos[pos_choice], "abs", False)
                pos_choice = not pos_choice
                t_start = time.time()

    # stop the visual reader
    ann_wrapper.visual_input.stop()

    # save the recorded images
    np.save(path + 'visual_percept_' + str(speed_arm) + '.npy', imgs)

    # return the arm and the head to a defined position
    ann_wrapper.parts_writer["moving"].write_double_all(zero_pos["right_arm"], "abs", True)
    ann_wrapper.parts_writer["head"].write_double_all(zero_pos["head"], "abs", True)

    # close the joint writer modules
    ann_wrapper.parts_writer["moving"].close()
    ann_wrapper.parts_writer["head"].close()


#########################################################
if __name__ == "__main__":
    wrapper = iCub_Interface.iCubANN_wrapper()
    test_cnt = params.test_count

    if len(sys.argv) > 1:
        for command in sys.argv[1:]:
            if command == 'all':
                speed_test_jreader(wrapper, test_cnt)
                speed_test_jwriter(wrapper, test_cnt)
                speed_test_sreader(wrapper, test_cnt)
                speed_test_vreader(wrapper, test_cnt)
                vis_move_test(wrapper)
            elif command == 'noskin':
                speed_test_jreader(wrapper, test_cnt)
                speed_test_jwriter(wrapper, test_cnt)
                speed_test_vreader(wrapper, test_cnt)
                vis_move_test(wrapper)
            elif command == "jreader":
                speed_test_jreader(wrapper, test_cnt)
            elif command == "jwriter":
                speed_test_jwriter(wrapper, test_cnt)
            elif command == "sreader":
                speed_test_sreader(wrapper, test_cnt)
            elif command == "vreader":
                speed_test_vreader(wrapper, test_cnt)
            elif command == "vis_move":
                vis_move_test(wrapper)
            else:
                print('No valid test command! Possible are: all; noskin; jreader; jwriter; sreader; vreader; vis_move')
    else:
        print('No valid test command! Possible are: all; noskin; jreader; jwriter; sreader; vreader; vis_move')

    del wrapper
    print('finish')
