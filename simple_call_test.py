import iCubCPP # requires iCubCPP in the present directory
import matplotlib.pylab as plt
import image_processing as img
import numpy as np
import sys
import time

from joint_limits import joint_limits as j_lim

#########################################################
def normal_pdf(value, mean, sigma):
    """
        params: value            -- value to calculate normal distribution at
                mean             -- mean of the normal distribution
                sigma            -- sigma of the normal distribution

        return:                  -- function value for the normal distribution
    """
    inv_sqrt_2pi = 1 / (sigma * np.sqrt(2 * np.pi))
    a = (value - mean) / sigma
    
    return inv_sqrt_2pi * np.exp(-0.5 * a * a)

def encode(part, joint, pop_size, joint_angle, sigma):
    """
        params: joint_angle      -- joint angle read from the robot
                size             -- size of the population coding 

        return:                  -- population encoded joint angle
    """
    neuron_deg = np.zeros((pop_size,))
    pos_pop = np.zeros((pop_size,))

    joint_min = j_lim[part]['joint_' + str(joint) + '_min'] 
    joint_max = j_lim[part]['joint_' + str(joint) + '_max']
    joint_range = joint_max - joint_min

    joint_deg_res = joint_range / pop_size

    for j in range(pop_size):
        neuron_deg[j] = joint_min + j * joint_deg_res
    
    for i in range(pop_size):
        pos_pop[i] = normal_pdf(neuron_deg[i], joint_angle, sigma)

    return pos_pop


#########################################################
def call_test_jreader(ann_wrapper):
    ## add joint reader instances
    ann_wrapper.add_joint_reader("J_Reader")
    ann_wrapper.add_joint_reader("J_Reader")    ## dublicate check
    ann_wrapper.add_joint_reader("J_Reader1")
    ann_wrapper.add_joint_reader("J_Reader2")

    print('finish adding')
    print('\n')

    ## init joint reader
    ann_wrapper.jointR_init("J_Reader", ann_wrapper.PART_KEY_HEAD, 0.5, 15)
    ann_wrapper.jointR_init("J_Reader", ann_wrapper.PART_KEY_HEAD, 0.5, 15) ## double initialization
    ann_wrapper.jointR_init("J_Reader1", ann_wrapper.PART_KEY_RIGHT_ARM, -0.5, 15)   ## negative sigma
    ann_wrapper.jointR_init("J_Reader1", ann_wrapper.PART_KEY_RIGHT_ARM, 0.5, 0, 2.0)   ## neuron resolution
    ann_wrapper.jointR_init("J_Reader2", 'false_part_key', 0.5, 15) ## false part key
    ann_wrapper.jointR_init("J_Reader2", ann_wrapper.PART_KEY_LEFT_ARM, 0.5, -15) ## negative population size
    ann_wrapper.jointR_init("J_Reader2", ann_wrapper.PART_KEY_LEFT_ARM, 0.5, 0, 0.0) ## wrong population sizing
    ann_wrapper.jointR_init("NO_NAME", ann_wrapper.PART_KEY_LEFT_ARM, 0.5, 15) ## not existent name

    print('finish JReader init')
    print('\n')

    ## print joint resolutions for joint reader
    print(ann_wrapper.jointR_get_joints_deg_res("J_Reader"))
    print(ann_wrapper.jointR_get_neurons_per_joint("J_Reader"))

    print(ann_wrapper.jointR_get_joints_deg_res("J_Reader1"))
    print(ann_wrapper.jointR_get_neurons_per_joint("J_Reader1"))

    print('finish JReader resolutions')
    print('\n')

    ## test read joints with joint reader
    print('readdouble')
    print(ann_wrapper.jointR_read_double("J_Reader", 3))
    print('readone')
    print(ann_wrapper.jointR_read_one("J_Reader", 3))
    print('readall')
    print(ann_wrapper.jointR_read_all("J_Reader"))

    print('finish JReader reading joints')
    print('\n')

    ## close joint reader
    print(ann_wrapper.jointR_close("J_Reader"))
    print(ann_wrapper.jointR_close("J_Reader1"))

    print('finish JReader close')
    print('\n')


#########################################################
def call_test_jwriter(ann_wrapper):
    ## add joint writer instances
    ann_wrapper.add_joint_writer("J_Writer")
    ann_wrapper.add_joint_writer("J_Writer")   ## dublicate check
    ann_wrapper.add_joint_writer("J_Writer1")
    ann_wrapper.add_joint_writer("J_Writer2")

    print('finish adding')
    print('\n')

    ## init joint writer
    ann_wrapper.jointW_init("J_Writer", ann_wrapper.PART_KEY_HEAD, 15)
    ann_wrapper.jointW_init("J_Writer", ann_wrapper.PART_KEY_HEAD, 15) ## double initialization
    ann_wrapper.jointW_init("J_Writer1", 'false_part_key', 15) ## false part key
    ann_wrapper.jointW_init("J_Writer2", ann_wrapper.PART_KEY_LEFT_ARM, -15) ## negative population size
    ann_wrapper.jointW_init("NO_NAME", ann_wrapper.PART_KEY_LEFT_ARM, 15) ## not existent name
    ann_wrapper.jointW_init("J_Writer1", ann_wrapper.PART_KEY_RIGHT_ARM, 0, 2.0)

    print('finish JWriter init')
    print('\n')

    ## print joint resolutions for joint writer
    print(ann_wrapper.jointW_get_joints_deg_res("J_Writer"))
    print(ann_wrapper.jointW_get_neurons_per_joint("J_Writer"))

    print(ann_wrapper.jointW_get_joints_deg_res("J_Writer1"))
    print(ann_wrapper.jointW_get_neurons_per_joint("J_Writer1"))

    print('finish JWriter resolutions')
    print('\n')

    test_pos = encode(ann_wrapper.PART_KEY_HEAD, 4, 15, 5, 0.5)
    print(test_pos)
    pop_all = np.zeros((6, 15))
    for i in range(6):
        pop_all[i] = encode(ann_wrapper.PART_KEY_HEAD, i, 15, 1, 0.5)

    print('writedouble')
    print(ann_wrapper.jointW_write_double("J_Writer", 10.0, 4, True))
    time.sleep(2.5)
    print('writeone')
    print(ann_wrapper.jointW_write_one("J_Writer", test_pos, 4, True))
    time.sleep(2.5)
    print('writeall')
    print(ann_wrapper.jointW_write_all("J_Writer", pop_all, True))

    print('finish JWriter writing joints')
    print('\n')

    print(ann_wrapper.jointW_close("J_Writer"))
    print(ann_wrapper.jointW_close("J_Writer1"))

    print('finish JWriter close')
    print('\n')


#########################################################
def call_test_sreader(ann_wrapper):
    ## add skin reader instances
    ann_wrapper.add_skin_reader("S_Reader")
    ann_wrapper.add_skin_reader("S_Reader")    ## dublicate check
    ann_wrapper.add_skin_reader("S_Reader1")

    print('finish skin reader adding')
    print('\n')

    ## init skin reader
    ann_wrapper.skinR_init("S_Reader", "r")
    ann_wrapper.skinR_init("S_Reader", "r")
    ann_wrapper.skinR_init("NO_NAME", "r")
    ann_wrapper.skinR_init("S_Reader1", "g")

    print('finish SReader init')
    print('\n')

    ## print taxel positions
    ann_wrapper.skinR_read_tactile("S_Reader")
    print(ann_wrapper.skinRGet_taxel_pos("S_Reader", "arm"))
    print(ann_wrapper.skinRGet_taxel_pos("S_Reader", "forearm"))
    print(ann_wrapper.skinRGet_taxel_pos("S_Reader", "hand"))

    ## print tactile data
    print(ann_wrapper.skinR_get_tactile_arm("S_Reader"))
    print(ann_wrapper.skinR_get_tactile_forearm("S_Reader"))
    print(ann_wrapper.skinR_get_tactile_hand("S_Reader"))


    ## close skin reader
    print(ann_wrapper.skinR_close("S_Reader"))

    print('finish SReader close')
    print('\n')

#########################################################
def call_test_vreader(ann_wrapper):
    ## add visual reader instance
    ann_wrapper.add_visual_reader()
    ann_wrapper.add_visual_reader()

    print('finish visual reader adding')
    print('\n')

    ## init visual reader
    print(ann_wrapper.visualR_init('r', 75, 48, 320, 240))  ## invalid field of view width
    print(ann_wrapper.visualR_init('r', 60, 56, 320, 240))  ## invalid field of view height
    print(ann_wrapper.visualR_init('t', 60, 48, 320, 240))  ## invalid eye character
    print(ann_wrapper.visualR_init('r', 60, 48, 160, 120))  ## output size above input size
    print(ann_wrapper.visualR_init('r'))                    ## use of default values 

    print('finish VReader init')
    print('\n')

    ann_wrapper.visualR_start()
    time.sleep(0.5)
    test_img = ann_wrapper.visualR_read_fromBuf().reshape(160, 120) 
    print(test_img.shape)
    print(type(test_img), type(test_img[0][0]))
    print(test_img)
    test_bild = np.ones((160,120))
    # show image
    img.show_image_matplot(test_bild, 'test', 'x', 'y')
    # plt.imshow(test_bild, cmap='gray', interpolation=None)
    # plt.show()
    # plt.pause(0.05)
    ann_wrapper.visualR_stop()


#########################################################

if __name__ == "__main__":
    wrapper = iCubCPP.iCubANN_wrapper()

    if (len(sys.argv) > 1):
        command = sys.argv[1]
        if (command == 'all'):
            call_test_jreader(wrapper)
            call_test_jwriter(wrapper)
            call_test_sreader(wrapper)
            call_test_vreader(wrapper)
        elif (command == "jreader"):
            call_test_jreader(wrapper)
        elif (command == "jwriter"):
            call_test_jwriter(wrapper)
        elif (command == "sreader"):
            call_test_sreader(wrapper)
        elif (command == "vreader"):
            call_test_vreader(wrapper)
    else:
        print('No valid test command!')

    del wrapper
    print('finish')
