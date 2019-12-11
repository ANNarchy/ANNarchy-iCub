import os
import sys
import time

import matplotlib.pylab as plt
import numpy as np

import iCub_Interface  # requires iCub_Interface in the present directory
import Testfiles.lib.world_controller as wc
from Testfiles.joint_limits import joint_limits as j_lim


#########################################################
def normal_pdf(value, mean, sigma):
    """
        params:
                value            -- value to calculate normal distribution at
                mean             -- mean of the normal distribution
                sigma            -- sigma of the normal distribution

        return:
                                -- function value for the normal distribution
    """
    # inv_sqrt_2pi = 4.0 / (sigma * np.sqrt(2 * np.pi))
    inv_sqrt_2pi = 1.0
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
def test_joint_positioning(ann_wrapper):
    n_pop = 100
    sigma = 1.5
    neuron_res = 0.0
    path = './Testfiles/Movement/'
    print('____________________________________________________________')
    print('__ Load test positions __')

    # load test positions
    position_path = "./Testfiles/test_positions/"
    positions = {}
    positions['pos_arm_T_r'] = (np.load(position_path + "test_pos_T.npy"), 'right_arm')
    positions['pos_arm_complex_r'] = (np.load(position_path + "test_hand_complex.npy"), 'right_arm')
    positions['pos_arm_home_r'] = (np.load(position_path + "test_pos_home.npy"), 'right_arm')
    positions['pos_arm_T_l'] = (np.load(position_path + "test_pos_T.npy"), 'left_arm')
    positions['pos_arm_complex_l'] = (np.load(position_path + "test_hand_complex.npy"), 'left_arm')
    positions['pos_arm_home_l'] = (np.load(position_path + "test_pos_home.npy"), 'left_arm')
    positions['pos_head'] = (np.load(position_path + "test_pos_head.npy"), 'head')
    positions['pos_head_complex'] = (np.load(position_path + "test_pos_head_complex.npy"), 'head')
    positions['pos_head_zero'] = (np.load(position_path + "test_pos_head_zero.npy"), 'head')

    if not os.path.isdir(path):
        os.mkdir(path)

    # encode positions
    print('__ Encode test positions __')
    part_enc = {'right_arm': {}, 'head': {}, 'left_arm': {}}
    for key in positions:
        pos_enc = []
        for i in range(positions[key][0].shape[0]):
            positions[key][0][i] = round(positions[key][0][i], 2)
            pos_enc.append(encode(positions[key][1], i, n_pop, positions[key][0][i], sigma, neuron_res))
        np.save(path + key + "_encoded.npy", pos_enc)
        part_enc[positions[key][1]][key] = pos_enc

    print('____________________________________________________________\n')

    print('__ Add and init joint reader and writer modules __')

    # add joint reader instances
    for name in part_enc:
        ann_wrapper.add_joint_reader(name)

        # add joint writer instances
        ann_wrapper.add_joint_writer(name)
    print('____ Added all joint reader and writer ____')

    # init joint reader
    ann_wrapper.jointR_init("right_arm", ann_wrapper.PART_KEY_RIGHT_ARM, sigma, n_pop, neuron_res)
    ann_wrapper.jointR_init("left_arm", ann_wrapper.PART_KEY_LEFT_ARM, sigma, n_pop, neuron_res)
    ann_wrapper.jointR_init("head", ann_wrapper.PART_KEY_HEAD, sigma, n_pop, neuron_res)

    # init joint writer
    ann_wrapper.jointW_init("right_arm", ann_wrapper.PART_KEY_RIGHT_ARM, n_pop, neuron_res, 25.0)
    ann_wrapper.jointW_init("left_arm", ann_wrapper.PART_KEY_LEFT_ARM, n_pop, neuron_res, 25.0)
    ann_wrapper.jointW_init("head", ann_wrapper.PART_KEY_HEAD, n_pop, neuron_res, 25.0)
    print('____ Initialized all joint reader and writer ____')
    print('____________________________________________________________\n')


    # test positioning
    print('__ Type of positioning: Double')
    read_double = {}
    test_results = {}
    for name in part_enc:
        print('____ Test part:', name)
        for key in positions:
            if positions[key][1] == name:
                print('______ Test position:', key)
                for i in range(positions[key][0].shape[0]):
                    ann_wrapper.jointW_write_double(name, positions[key][0][i], i, True)
                time.sleep(1)

                read_pos_double = np.zeros((positions[key][0].shape[0]))
                for i in range(read_pos_double.shape[0]):
                    read_pos_double[i] = round(ann_wrapper.jointR_read_double(name, i), 2)
                read_double[key] = read_pos_double

                test_result = True
                error_joints = []
                for i in range(read_pos_double.shape[0]):
                    max_lim = abs(round(positions[key][0][i], 2)) + 0.1 * abs(round(positions[key][0][i], 2))
                    min_lim = abs(round(positions[key][0][i], 2)) - 0.1 * abs(round(positions[key][0][i], 2))
                    if (abs(round(read_pos_double[i], 2)) > max_lim) or (abs(round(read_pos_double[i], 2)) < min_lim):
                        test_result = False
                        error_joints.append(i)
                test_results[name + '_' + key] = (test_result, error_joints)
                print(test_result)

    for key in read_double:
        np.save(path + key + "_double.npy", read_double[key])

    print('________ Test results: Double')
    for key in test_results:
        print('Test:', key, 'results:', test_results[key])

    print('\n')

    print('__ Type of positioning: Population_single')
    read_pop_single = {}
    test_results = {}
    for name in part_enc:
        print('____ Test part:', name)
        for key in part_enc[name]:
            print('______ Test position:', key)
            for i in range(positions[key][0].shape[0]):
                ann_wrapper.jointW_write_pop_one(name, part_enc[name][key][i], i, True)
            time.sleep(2)

            read_pos_pop_S = []
            for i in range(positions[key][0].shape[0]):
                read_pos_pop_S.append(np.round(ann_wrapper.jointR_read_pop_one(name, i), decimals=3))
            read_pop_single[key] = read_pos_pop_S

            test_result = True
            error_joints = []
            for i in range(len(read_pos_pop_S)):
                if not np.allclose(read_pos_pop_S[i], part_enc[name][key][i], atol=0.1):
                    test_result = False
                    error_joints.append(i)
            test_results[name + '_' + key] = (test_result, error_joints)
            print(test_result)

    for key in read_pop_single:
        np.save(path + key + "_pop_single.npy", read_pop_single[key])

    print('________ Test results: Population_single')
    for key in test_results:
        print('Test:', key, 'results:', test_results[key])

    print('\n')

    print('__ Type of positioning: Population_all')
    read_pop_all = {}
    test_results = {}
    for name in part_enc:
        print('____ Test part:', name)
        for key in part_enc[name]:
            print('______ Test position:', key)
            ann_wrapper.jointW_write_pop_all(name, part_enc[name][key], True)
            time.sleep(2)

            read_pos_pop_a = ann_wrapper.jointR_read_pop_all(name)
            read_pop_all[key] = read_pos_pop_a

            test_result = True
            error_joints = []
            for i in range(len(read_pos_pop_a)):
                if not np.allclose(read_pos_pop_a[i][0:part_enc[name][key][i].shape[0]], part_enc[name][key][i], atol=0.1):
                    test_result = False
                    error_joints.append(i)
            test_results[name + '_' + key] = (test_result, error_joints)
            print(test_result)

    for key in read_pop_all:
        np.save(path + key + "_pop_all.npy", read_pop_all[key])

    print('________ Test results: Population_all')
    for key in test_results:
        print('Test:', key, 'results:', test_results[key])

    print('____________________________________________________________\n')

    # close joint reader
    print('__ Close joint reader and writer modules __')
    for part in part_enc:
        ann_wrapper.jointR_close(part)

        # add joint writer instances
        ann_wrapper.jointW_close(part)

    print('____ Closed joint reader and writer modules ____')
    print('____________________________________________________________\n')


#########################################################
def test_tactile_reading(ann_wrapper):

    path = "./Testfiles/Tactile/"
    if not os.path.isdir(path):
        os.mkdir(path)
    sim_ctrl = wc.WorldController()
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

    sphere = sim_ctrl.create_object("ssph", [0.025], loc_p0, [0.0, 0.0, 1.0])
    data_count = 5

    print('____________________________________________________________')
    print('__ Add and init skin reader module __')

    # add skin reader instances
    ann_wrapper.add_skin_reader("S_Reader")
    ann_wrapper.add_skin_reader("S_Reader1")

    # init skin reader
    print("Init:", ann_wrapper.skinR_init("S_Reader", "r", True))
    print("Init:", ann_wrapper.skinR_init("S_Reader1", "r", False))

    print('____ Initialized skin reader ____')
    print('____________________________________________________________\n')
    data_arm_norm = []
    data_farm_norm = []
    data_hand_norm = []
    pos = loc_p0
    for i in range(len(loc_sph) - 1):
        print("step:", i)
        delta_pos = loc_sph[i+1] - pos
        d_pos = delta_pos/data_count
        if d_pos.sum() != 0:
            for j in range(data_count):
                pos += d_pos
                sim_ctrl.move_object(sphere, pos)
                time.sleep(0.1)

                ann_wrapper.skinR_read_tactile("S_Reader")
                ann_wrapper.skinR_read_tactile("S_Reader1")

                data_arm_norm.append(np.array(ann_wrapper.skinR_get_tactile_arm("S_Reader")))
                data_farm_norm.append(np.array(ann_wrapper.skinR_get_tactile_forearm("S_Reader")))
                data_hand_norm.append(np.array(ann_wrapper.skinR_get_tactile_hand("S_Reader")))

                time.sleep(0.1)
                if np.equal(pos, loc_p1).all():
                    pos = loc_p2
                    sim_ctrl.move_object(sphere, pos)

    data_arm_raw = np.array(ann_wrapper.skinR_get_tactile_arm("S_Reader1"))
    data_farm_raw = np.array(ann_wrapper.skinR_get_tactile_forearm("S_Reader1"))
    data_hand_raw = np.array(ann_wrapper.skinR_get_tactile_hand("S_Reader1"))

    print("Finished tactile sensing process")

    print("________ Test results:")
    print(" Touched arm:\n   ", "norm data:", np.array(data_arm_norm).max() == 1.0, "\n    raw data:", data_arm_raw.max() == 255.0)
    print(" Touched forearm:\n   ", "norm data:", np.array(data_farm_norm).max() == 1.0, "\n    raw data:", data_farm_raw.max() == 255.0)
    print(" Touched hand:\n   ", "norm data:", np.array(data_hand_norm).max() == 1.0, "\n    raw data:", data_hand_raw.max() == 255.)

    np.save(path + "tact_arm_data_norm.npy", data_arm_norm)
    np.save(path + "tact_forearm_data_norm.npy", data_farm_norm)
    np.save(path + "tact_hand_data_norm.npy", data_hand_norm)

    np.save(path + "tact_arm_data_raw.npy", data_arm_raw)
    np.save(path + "tact_forearm_data_raw.npy", data_farm_raw)
    np.save(path + "tact_hand_data_raw.npy", data_hand_raw)
    print('____________________________________________________________')
    print('__ Close skin reader module __')

    # close skin reader
    ann_wrapper.skinR_close("S_Reader")
    ann_wrapper.skinR_close("S_Reader1")

    sim_ctrl.del_all()
    del sim_ctrl


#########################################################
def test_visual_perception(ann_wrapper):

    fov_w = 60
    fov_h = 48
    img_w = 320
    img_h = 240
    img_count = 10
    path = "./Testfiles/Vision/"
    if not os.path.isdir(path):
        os.mkdir(path)

    sim_ctrl = wc.WorldController()
    loc_sph = [0.2, 1.0, 0.7]
    box = sim_ctrl.create_object("sbox", [0.1, 0.1, 0.1], [-0.15, 0.8, 0.6], [1.0, 0.0, 0.0])
    sphere = sim_ctrl.create_object("ssph", [0.05], loc_sph, [0.0, 0.0, 1.0])

    print('____________________________________________________________')
    print('__ Add and init visual reader module __')

    # add visual reader instance
    ann_wrapper.add_visual_reader()

    # init visual reader
    ann_wrapper.visualR_init('r', fov_w, fov_h, img_w, img_h)

    print('____ Initialized visual reader ____')
    print('____________________________________________________________\n')

    read_imgs = []
    ann_wrapper.visualR_start()
    time.sleep(0.15)
    loc_sph[1] = 0.75
    sim_ctrl.move_object(sphere, loc_sph)
    time.sleep(0.35)

    print('____ Obtain visual information ____')

    for i in range(img_count):
        read_img = ann_wrapper.visualR_read_fromBuf()
        if read_img.shape[0] > 0:
            read_img = read_img.reshape(img_h, img_w).T
            read_imgs.append(read_img)
            # plt.imshow(read_img.T, cmap='gray')
            # plt.show()
            # plt.pause(0.05)
        else:
            print('No buffered image!')
    np.save(path + 'Vision_full_size.npy', read_imgs)

    print('____________________________________________________________')
    print('__ Stop and close visual reader module __')
    ann_wrapper.visualR_stop()
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
                print('No valid test command!')
    else:
        print('No valid test command!')

    del wrapper
    print('Finished automated tests.')
