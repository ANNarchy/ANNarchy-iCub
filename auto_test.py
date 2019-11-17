import matplotlib.pylab as plt
import numpy as np
import sys
import time
import os
import Testfiles.lib.world_controller as wc

import iCubCPP # requires iCubCPP in the present directory

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

    ## load test positions
    positions = {}
    positions['pos_hand_T_r'] = (np.load("./Testfiles/test_pos_T.npy"), 'right_arm')
    positions['pos_hand_complex_r'] = (np.load("./Testfiles/test_hand_complex.npy"), 'right_arm')
    positions['pos_hand_home_r'] = (np.load("./Testfiles/test_pos_home.npy"), 'right_arm')
    positions['pos_hand_T_l'] = (np.load("./Testfiles/test_pos_T.npy"), 'left_arm')
    positions['pos_hand_complex_l'] = (np.load("./Testfiles/test_hand_complex.npy"), 'left_arm')
    positions['pos_hand_home_l'] = (np.load("./Testfiles/test_pos_home.npy"), 'left_arm')
    positions['pos_head'] = (np.load("./Testfiles/test_pos_head.npy"), 'head')
    positions['pos_head_complex'] = (np.load("./Testfiles/test_pos_head_complex.npy"), 'head')
    positions['pos_head_zero'] = (np.load("./Testfiles/test_pos_head_zero.npy"), 'head')

    if not os.path.isdir(path):
        os.mkdir(path)

    ## encode positions
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

    ## add joint reader instances
    for name in part_enc:
        ann_wrapper.add_joint_reader(name)

        ## add joint writer instances
        ann_wrapper.add_joint_writer(name)
    print('____ Added all joint reader and writer ____')

    ## init joint reader
    ann_wrapper.jointR_init("right_arm", ann_wrapper.PART_KEY_RIGHT_ARM, sigma, n_pop, neuron_res)
    ann_wrapper.jointR_init("left_arm", ann_wrapper.PART_KEY_LEFT_ARM, sigma, n_pop, neuron_res)
    ann_wrapper.jointR_init("head", ann_wrapper.PART_KEY_HEAD, sigma, n_pop, neuron_res)

    ## init joint writer
    ann_wrapper.jointW_init("right_arm", ann_wrapper.PART_KEY_RIGHT_ARM, n_pop, neuron_res)
    ann_wrapper.jointW_init("left_arm", ann_wrapper.PART_KEY_LEFT_ARM, n_pop, neuron_res)
    ann_wrapper.jointW_init("head", ann_wrapper.PART_KEY_HEAD, n_pop, neuron_res)
    print('____ Initialized all joint reader and writer ____')
    print('____________________________________________________________\n')


    # test positioning
    print('__ Type of positioning: Double')
    read_double = {}
    test_results = {}
    for name in part_enc:
        print('____ Test part:', name)
        for key in positions:
            if (positions[key][1] == name):
                print('______ Test position:', key)
                for i in range(positions[key][0].shape[0]): 
                    ann_wrapper.jointW_write_double(name, positions[key][0][i], i, True)
                time.sleep(1)

                read_pos = np.zeros((positions[key][0].shape[0]))
                for i in range(read_pos.shape[0]):
                    read_pos[i] = round(ann_wrapper.jointR_read_double(name, i), 2)
                read_double[key] = read_pos

                test_result = True
                error_joints = []
                for i in range(read_pos.shape[0]):
                    max_lim = abs(round(positions[key][0][i], 2)) + 0.01 * abs(round(positions[key][0][i], 2))
                    min_lim = abs(round(positions[key][0][i], 2)) - 0.01 * abs(round(positions[key][0][i], 2))
                    if ((abs(round(read_pos[i], 2)) > max_lim) or (abs(round(read_pos[i], 2)) < min_lim) ):
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
                ann_wrapper.jointW_write_one(name, part_enc[name][key][i], i, True)
            time.sleep(2)

            read_pos = []
            for i in range(len(read_pos)):
                read_pos.append(np.round(ann_wrapper.jointR_read_one(name, i), decimals=3))
            read_pop_single[key] = read_pos
            
            test_result = True
            error_joints = []
            for i in range(len(read_pos)):
                if (not np.allclose(read_pos[i], part_enc[name][key][i], atol=0.1)):
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
            ann_wrapper.jointW_write_all(name, part_enc[name][key], True)
            time.sleep(2)

            read_pos = ann_wrapper.jointR_read_all(name)
            # print(read_pos, type(read_pos))
            read_pop_all[key] = read_pos
            
            test_result = True
            error_joints = []
            for i in range(len(read_pos)):
                if (not np.allclose(read_pos[i][0:part_enc[name][key][i].shape[0]], part_enc[name][key][i], atol=0.1)):
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

    ## close joint reader
    print('__ Close joint reader and writer modules __')
    for part in part_enc:
        ann_wrapper.jointR_close(part)

        ## add joint writer instances
        ann_wrapper.jointW_close(part)

    print('____ Closed joint reader and writer modules ____')
    print('____________________________________________________________\n')

# #########################################################
# def test_tactile_reading(ann_wrapper):
#     ## add skin reader instances
#     ann_wrapper.add_skin_reader("S_Reader")
#     ann_wrapper.add_skin_reader("S_Reader")    ## dublicate check
#     ann_wrapper.add_skin_reader("S_Reader1")

#     print('finish skin reader adding')
#     print('\n')

#     ## init skin reader
#     ann_wrapper.skinR_init("S_Reader", "r")
#     ann_wrapper.skinR_init("S_Reader", "r")
#     ann_wrapper.skinR_init("NO_NAME", "r")
#     ann_wrapper.skinR_init("S_Reader1", "g")

#     print('finish SReader init')
#     print('\n')

#     ## print taxel positions
#     ann_wrapper.skinR_read_tactile("S_Reader")
#     print(ann_wrapper.skinRGet_taxel_pos("S_Reader", "arm"))
#     print(ann_wrapper.skinRGet_taxel_pos("S_Reader", "forearm"))
#     print(ann_wrapper.skinRGet_taxel_pos("S_Reader", "hand"))

#     ## print tactile data
#     print(ann_wrapper.skinR_get_tactile_arm("S_Reader"))
#     print(ann_wrapper.skinR_get_tactile_forearm("S_Reader"))
#     print(ann_wrapper.skinR_get_tactile_hand("S_Reader"))


#     ## close skin reader
#     print(ann_wrapper.skinR_close("S_Reader"))

#     print('finish SReader close')
#     print('\n')

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

    ## add visual reader instance
    ann_wrapper.add_visual_reader()

    ## init visual reader
    ann_wrapper.visualR_init('r', fov_w, fov_h, img_w, img_h)

    print('____ Initialized visual reader ____')
    print('____________________________________________________________\n')
    
    read_imgs = []
    ann_wrapper.visualR_start()
    time.sleep(0.15)
    loc_sph[1] = 0.75
    sim_ctrl.move_object(sphere, loc_sph)
    time.sleep(0.35)

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

    ann_wrapper.visualR_stop()
    sim_ctrl.del_all()
    del sim_ctrl

#########################################################

if __name__ == "__main__":
    wrapper = iCubCPP.iCubANN_wrapper()

    if (len(sys.argv) > 1):
        command = sys.argv[1]
        if (command == 'all'):
            test_joint_positioning(wrapper)
            test_visual_perception(wrapper)
        elif (command == "positioning"):
            test_joint_positioning(wrapper)
        # elif (command == "sreader"):
        #     call_test_sreader(wrapper)
        elif (command == "vision"):
            test_visual_perception(wrapper)
    else:
        print('No valid test command!')

    del wrapper
    print('Finished automated tests.')
