import os
import sys
import time

import matplotlib.pylab as plt
import numpy as np

import iCubCPP  # requires iCubCPP in the present directory
import Testfiles.lib.world_controller as wc
from Testfiles.joint_limits import joint_limits as j_lim

bog2deg = 180.0 / np.pi         # factor for radiant to degree conversion
eye_distance = 0.07             # distance between left and right eye
eye_loc = [0.0, 0.9375, 0.055]  # location of the center point between both eyes

#########################################################
def normal_pdf(value, mean, sigma):
    """
        Calculate the normal distribution function value for a given value.

        params:
            value            -- value to calculate normal distribution at
            mean             -- mean of the normal distribution
            sigma            -- sigma of the normal distribution

        return:
            function value for the normal distribution
    """
    inv_sqrt_2pi = 1 / (sigma * np.sqrt(2 * np.pi))
    a = (value - mean) / sigma

    return inv_sqrt_2pi * np.exp(-0.5 * a * a)


def encode(part, joint, pop_size, joint_angle, sigma, resolution=0.0):
    """
        params:
                joint_angle      -- joint angle read from the robot
                size             -- size of the population coding

        return:
                                -- population encoded joint angle
    """

    joint_min = j_lim[part]['joint_' + str(joint) + '_min']
    joint_max = j_lim[part]['joint_' + str(joint) + '_max']
    joint_range = joint_max - joint_min
    if resolution == 0:
        joint_deg_res = joint_range / pop_size
    else:
        joint_deg_res = resolution
        pop_size = int(np.floor(joint_range / resolution))

    neuron_deg = np.zeros((pop_size,))
    pos_pop = np.zeros((pop_size,))

    for j in range(pop_size):
        neuron_deg[j] = joint_min + j * joint_deg_res
        pos_pop[j] = round(normal_pdf(neuron_deg[j], joint_angle, sigma), 3)

    pos_pop = pos_pop/np.amax(pos_pop)

    return pos_pop


#########################################################
def speed_test_jreader(ann_wrapper, test_count):
    n_pop = 100
    sigma = 1.5
    neuron_res = 0.0
    parts = ["right_arm", "head"]

    print('____________________________________________________________\n')
    print('__ Add and init joint reader modules __')

    # add joint reader instances
    ann_wrapper.add_joint_reader("right_arm")
    ann_wrapper.add_joint_reader("head")

    print('____ Added all joint reader ____')

    # init joint reader
    ann_wrapper.jointR_init("right_arm", ann_wrapper.PART_KEY_RIGHT_ARM, sigma, n_pop, neuron_res)
    ann_wrapper.jointR_init("head", ann_wrapper.PART_KEY_HEAD, sigma, n_pop, neuron_res)

    print('____ Initialized all joint reader and writer ____')
    print('____________________________________________________________\n')


    # test speed reading double
    print('__ Type of reading: Double')
    results_double = {}
    for name in parts:
        print('____ Test part:', name)
        joints = ann_wrapper.jointR_get_joint_count(name)
        read_pos_double = np.zeros((joints))
        time_start_double = time.time()
        for i in range(test_count):
            for i in range(read_pos_double.shape[0]):
                read_pos_double[i] = ann_wrapper.jointR_read_double(name, i)
        time_stop_double = time.time()
        results_double[name] = (time_stop_double - time_start_double) / test_count

    print('________ Test results: Double')
    for part in results_double:
        print("Time double ", part, ":", results_double[part])
    print('\n')

    # test speed reading population single
    print('__ Type of reading: Population_single')
    results_pop_single = {}
    for name in parts:
        print('____ Test part:', name)
        joints = ann_wrapper.jointR_get_joint_count(name)
        read_pos_pop_single = np.zeros((joints, n_pop))
        time_start_pop_single = time.time()
        for i in range(test_count):
            for i in range(read_pos_pop_single.shape[0]):
                read_pos_pop_single[i] = ann_wrapper.jointR_read_one(name, i)
        time_stop_pop_single = time.time()
        results_pop_single[name] = (time_stop_pop_single - time_start_pop_single) / test_count

    print('________ Test results: Population_single')
    for part in results_pop_single:
        print("Time pop_single", part , ":", results_pop_single[part])
    print('\n')

    # test speed reading population all
    print('__ Type of reading: Population_all')
    results_pop_all = {}
    for name in parts:
        print('____ Test part:', name)
        joints = ann_wrapper.jointR_get_joint_count(name)
        read_pos_pop_all = np.zeros((joints, n_pop))
        time_start_pop_all = time.time()
        for i in range(test_count):
            read_pos_pop_all = ann_wrapper.jointR_read_all(name)
        time_stop_pop_all = time.time()
        results_pop_all[name] = (time_stop_pop_all - time_start_pop_all) / test_count

    print('________ Test results: Population_all')
    for part in results_pop_all:
        print("Time pop_all", part , ":", results_pop_all[part])
    print('\n')

    print('____________________________________________________________\n')

    # close joint reader
    print('__ Close joint reader modules __')
    for part in parts:
        ann_wrapper.jointR_close(part)

    print('____ Closed joint reader modules ____')
    print('____________________________________________________________\n')


#########################################################
def speed_test_jwriter(ann_wrapper, test_count):
    n_pop = 100
    sigma = 1.5
    neuron_res = 0.0

    print('____________________________________________________________')
    print('__ Load test positions __')

    # load test positions
    position_path = "./Testfiles/test_positions/"
    positions = {}
    positions['pos_hand_T_r'] = (np.load(position_path + "test_pos_T.npy"), 'right_arm')
    positions['pos_hand_complex_r'] = (np.load(position_path + "test_hand_complex.npy"), 'right_arm')
    positions['pos_hand_home_r'] = (np.load(position_path + "test_pos_home.npy"), 'right_arm')
    positions['pos_head'] = (np.load(position_path + "test_pos_head.npy"), 'head')
    positions['pos_head_complex'] = (np.load(position_path + "test_pos_head_complex.npy"), 'head')
    positions['pos_head_zero'] = (np.load(position_path + "test_pos_head_zero.npy"), 'head')

    zero_pos = {}
    zero_pos['head'] = np.zeros(6)
    zero_pos['right_arm'] = np.load(position_path + "zero_pos_arm.npy")
    zero_pos['left_arm'] = np.load(position_path + "zero_pos_arm.npy")

    # encode positions
    print('__ Encode test positions __')
    part_enc = {'right_arm': {}, 'head': {}}
    for key in positions:
        pos_enc = []
        for i in range(positions[key][0].shape[0]):
            positions[key][0][i] = round(positions[key][0][i], 2)
            pos_enc.append(encode(positions[key][1], i, n_pop, positions[key][0][i], sigma, neuron_res))
        part_enc[positions[key][1]][key] = pos_enc

    print('____________________________________________________________\n')
    print('__ Add and init joint writer modules __')

    for name in part_enc:
        # add joint writer instances
        ann_wrapper.add_joint_writer(name)
    print('____ Added all joint writer ____')

    # init joint writer
    ann_wrapper.jointW_init("right_arm", ann_wrapper.PART_KEY_RIGHT_ARM, n_pop, neuron_res, 100.0)
    ann_wrapper.jointW_init("left_arm", ann_wrapper.PART_KEY_LEFT_ARM, n_pop, neuron_res, 100.0)
    ann_wrapper.jointW_init("head", ann_wrapper.PART_KEY_HEAD, n_pop, neuron_res, 100.0)
    print('____ Initialized all joint writer ____')
    print('____________________________________________________________\n')


    # test positioning
    print('__ Type of positioning: Double')
    results_double = {}
    for name in part_enc:
        joints = ann_wrapper.jointW_get_joint_count(name)
        print('____ Test part:', name)
        for key in positions:
            if positions[key][1] == name:
                print('______ Test position:', key)
                for i in range(test_count):
                    time_start = time.time()
                    for i in range(joints):
                        ann_wrapper.jointW_write_double(name, positions[key][0][i], i, True)
                    time_stop = time.time()
                    results_double[name + '_' + key] += time_stop -time_start

                    for i in range(joints):
                        ann_wrapper.jointW_write_double(name, zero_pos[name][i], i, True)
                    time.sleep(0.5)
                results_double[name + '_' + key] /= test_count


    print('________ Test results: Double')
    for key in results_double:
        print('Test:', key, 'results:', results_double[key])
    print('\n')


    print('__ Type of positioning: Population_single')
    results_pop_single = {}
    for name in part_enc:
        joints = ann_wrapper.jointW_get_joint_count(name)
        print('____ Test part:', name)
        for key in part_enc[name]:
            print('______ Test position:', key)
            for i in range(test_count):
                time_start = time.time()
                for i in range(joints):
                    ann_wrapper.jointW_write_one(name, part_enc[name][key][i], i, True)
                time_stop = time.time()
                results_pop_single[name + '_' + key] += time_stop -time_start

                for i in range(joints):
                    ann_wrapper.jointW_write_double(name, zero_pos[name][i], i, True)
                time.sleep(0.5)
            results_pop_single[name + '_' + key] /= test_count

    print('________ Test results: Population_single')
    for key in results_pop_single:
        print('Test:', key, 'results:', results_pop_single[key])
    print('\n')


    print('__ Type of positioning: Population_all')
    results_pop_all = {}
    for name in part_enc:
        print('____ Test part:', name)
        for key in part_enc[name]:
            print('______ Test position:', key)
            for i in range(test_count):
                time_start = time.time()
                ann_wrapper.jointW_write_all(name, part_enc[name][key], True)
                time_stop = time.time()
                results_pop_all[name + '_' + key] += time_stop -time_start

                for i in range(joints):
                    ann_wrapper.jointW_write_double(name, zero_pos[name][i], i, True)
                time.sleep(0.5)
            results_pop_all[name + '_' + key] /= test_count

    print('________ Test results: Population_all')
    for key in results_pop_all:
        print('Test:', key, 'results:', results_pop_all[key])

    print('____________________________________________________________\n')

    print('__ Close joint writer modules __')
    for part in part_enc:
        # close joint writer instances
        ann_wrapper.jointW_close(part)

    print('____ Closed joint writer modules ____')
    print('____________________________________________________________\n')


#########################################################
def speed_test_sreader(ann_wrapper, test_count):

    print('____________________________________________________________')
    print('__ Add and init skin reader module __')
    # add skin reader instances
    ann_wrapper.add_skin_reader("S_Reader")
    ann_wrapper.add_skin_reader("S_Reader1")


    # init skin reader
    print("Init:", ann_wrapper.skinR_init("S_Reader", "r", True)) # normalized
    print("Init:", ann_wrapper.skinR_init("S_Reader1", "r", False)) # non-normalized

    print('____ Initialized skin reader ____')
    print('____________________________________________________________\n')


    print('____ Test speed performance with normalization ____')
    t_start_norm = time.time()
    for i in range(test_count):
        ann_wrapper.skinR_read_tactile("S_Reader")
    t_stop_norm = time.time()

    data_arm_norm = np.array(ann_wrapper.skinR_get_tactile_arm("S_Reader"))
    data_farm_norm = np.array(ann_wrapper.skinR_get_tactile_forearm("S_Reader"))
    data_hand_norm = np.array(ann_wrapper.skinR_get_tactile_hand("S_Reader"))


    print('____ Test speed performance without normalization ____')
    t_start_non_norm = time.time()
    for i in range(test_count):
        ann_wrapper.skinR_read_tactile("S_Reader1")
    t_stop_non_norm = time.time()

    data_arm_non_norm = np.array(ann_wrapper.skinR_get_tactile_arm("S_Reader1"))
    data_farm_non_norm = np.array(ann_wrapper.skinR_get_tactile_forearm("S_Reader1"))
    data_hand_non_norm = np.array(ann_wrapper.skinR_get_tactile_hand("S_Reader1"))

    print('____________________________________________________________')
    print('__ Close skin reader module __')

    # close skin reader
    print(ann_wrapper.skinR_close("S_Reader"))
    print(ann_wrapper.skinR_close("S_Reader1"))


    print('____________________________________________________________')
    print('__ Results __')

    print("Data shape normalized data:", data_arm_norm.shape, data_farm_norm.shape, data_hand_norm.shape)
    print("Data shape non-normalized data:", data_arm_non_norm.shape, data_farm_non_norm.shape, data_hand_non_norm.shape)

    print('Time with normalized data:', (t_stop_norm - t_start_norm)/test_count, "s")
    print('Time with non-normalized data:', (t_stop_non_norm - t_start_non_norm)/test_count, "s")


#########################################################
def speed_test_vreader(ann_wrapper, test_count):

    imgs_full = []
    imgs_quarter = []
    imgs_field = []

    path = "./Testfiles/Vision/"
    if not os.path.isdir(path):
        os.mkdir(path)

    print('____________________________________________________________')
    print('__ Add and init visual reader module with full resolution __')
    # add visual reader instance
    ann_wrapper.add_visual_reader()

    # init visual reader
    print(ann_wrapper.visualR_init('r'))                    # use of default values
    print('____ Initialized visual reader ____')
    print('____________________________________________________________\n')

    print('____ Test speed performance with full resolution ____')
    t_start_full = time.time()
    ann_wrapper.visualR_start()
    while len(imgs_full) < test_count:
        img_full = ann_wrapper.visualR_read_fromBuf()
        if img_full.shape[0] != 0:
            imgs_full.append(img_full)
    t_stop_full = time.time()

    print('____________________________________________________________')
    print('__ Stop and close visual reader module __')
    ann_wrapper.visualR_stop()
    ann_wrapper.rm_visual_reader()

    np.save(path + 'full_size.npy', img_full)

    time.sleep(1.0)
    ann_wrapper.add_visual_reader()

    print('____________________________________________________________')
    print('__ Reinit visual reader module with quarter resolution __')
    print(ann_wrapper.visualR_init('r', 60, 48, 80, 60))    # lower resolution
    print('____ Initialized visual reader ____')
    print('____________________________________________________________\n')

    print('____ Test speed performance with quarter resolution ____')
    t_start_quart = time.time()
    ann_wrapper.visualR_start()
    while len(imgs_quarter) < test_count:
        img_quarter = ann_wrapper.visualR_read_fromBuf()
        if img_quarter.shape[0] != 0:
            imgs_quarter.append(img_quarter)
    t_stop_quart = time.time()

    print('____________________________________________________________')
    print('__ Stop and close visual reader module __')
    ann_wrapper.visualR_stop()
    ann_wrapper.rm_visual_reader()

    np.save(path + 'quarter_size.npy', img_quarter)

    time.sleep(1.0)
    ann_wrapper.add_visual_reader()

    print('____________________________________________________________')
    print('__ Reinit visual reader module with half visual field and quarter resolution __')
    print(ann_wrapper.visualR_init('r', 30, 24, 80, 60))    # lower resolution and smaller visual field
    print('____ Initialized visual reader ____')
    print('____________________________________________________________\n')

    print('____ Test speed performance with quarter resolution ____')
    t_start_field = time.time()
    ann_wrapper.visualR_start()
    while len(imgs_field) < test_count:
        img_field = ann_wrapper.visualR_read_fromBuf()
        if img_field.shape[0] != 0:
            imgs_field.append(img_field)
    t_stop_field = time.time()

    print('____________________________________________________________')
    print('__ Stop and close visual reader module __')
    ann_wrapper.visualR_stop()

    np.save(path + 'field_size.npy', img_field)

    print('Time with full resolution:', 1. / ((t_stop_full - t_start_full) / test_count), "fps")
    print('Time with quarter resolution:', 1.0 / ((t_stop_quart - t_start_quart) / test_count), "fps")
    print('Time with quarter resolution and half visual field:', 1/ ((t_stop_field - t_start_field) / test_count), "fps")


#########################################################
def vis_move_test(ann_wrapper):
    position_path = "./Testfiles/test_positions/"
    # position = np.load(position_path + "test_visuomove.npy")
    pos = {}
    pos[True] = np.load(position_path + "test_vismov0.npy")
    pos[False] = np.load(position_path + "test_vismov1.npy")

    zero_pos = {}
    zero_pos['head'] = np.zeros(6)
    zero_pos['right_arm'] = np.load(position_path + "test_pos_home.npy")

    path = "./Testfiles/Visiou_movement/"
    if not os.path.isdir(path):
        os.mkdir(path)

    n_pop = 50
    imgs = []

    ann_wrapper.add_visual_reader()
    ann_wrapper.add_joint_writer("moving")
    ann_wrapper.add_joint_writer("head")
    speed_arm = 1
    ann_wrapper.visualR_init('r', 60, 48, 80, 60)
    ann_wrapper.jointW_init("moving", ann_wrapper.PART_KEY_RIGHT_ARM, n_pop, speed_arm)
    ann_wrapper.jointW_init("head", ann_wrapper.PART_KEY_HEAD, n_pop, 100)

    for i in range(ann_wrapper.jointW_get_joint_count("moving")):
        ann_wrapper.jointW_write_double("moving", pos[True][i], i, True)

    sim_ctrl = wc.WorldController()
    hand_loc = sim_ctrl.get_hand_location("rhand")

    dx = hand_loc[0] - eye_loc[0]
    dy = hand_loc[1] - eye_loc[1]
    dz = hand_loc[2] - eye_loc[2]
    alpha = bog2deg * np.arctan(dy/dz)
    beta =  - bog2deg * np.arctan(dx/dz)
    target_pos = np.zeros(ann_wrapper.jointW_get_joint_count("head"))

    target_pos[0] = 3.0/4.0 * alpha
    target_pos[3] = 1.0/ 4.0 * alpha - 3
    target_pos[2] = -1.0/2.0 * beta
    target_pos[4] = 1.0/2.0 * beta - 10

    for i in range(ann_wrapper.jointW_get_joint_count("head")):
        ann_wrapper.jointW_write_double_all("head", target_pos, True)
    time.sleep(2)

    ann_wrapper.visualR_start()

    for i in range(ann_wrapper.jointW_get_joint_count("moving")):
        ann_wrapper.jointW_write_double_all("moving", pos[False], True)
    t_start = time.time()
    pos_choice = True
    while len(imgs) < 100:
        imgs.append(np.array(ann_wrapper.visualR_read_fromBuf()))
        dt = time.time() - t_start
        if dt > 0.5:
            for i in range(ann_wrapper.jointW_get_joint_count("moving")):
                ann_wrapper.jointW_write_double_all("moving", pos[pos_choice], False)
                pos_choice = not pos_choice
                t_start = time.time()

    ann_wrapper.visualR_stop()

    np.save(path + 'visual_percept_' + str(speed_arm) + '.npy', imgs)

    ann_wrapper.jointW_write_double_all("moving", zero_pos["right_arm"], True)
    ann_wrapper.jointW_write_double_all("head", zero_pos["head"], True)

    ann_wrapper.jointW_close("moving")
    ann_wrapper.jointW_close("head")


#########################################################
if __name__ == "__main__":
    wrapper = iCubCPP.iCubANN_wrapper()
    test_cnt = 10

    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == 'all':
            speed_test_jreader(wrapper, test_cnt)
            speed_test_jwriter(wrapper, test_cnt)
            speed_test_sreader(wrapper, test_cnt)
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
        elif command == "visuo_move":
            vis_move_test(wrapper)
    else:
        print('No valid test command!')

    del wrapper
    print('finish')