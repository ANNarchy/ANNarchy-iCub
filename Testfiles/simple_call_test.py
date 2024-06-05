"""
 *  Copyright (C) 2019-2022 Torsten Fietzek
 *
 *  simple_call_test.py is part of the ANNarchy iCub interface
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


import sys
import time

import matplotlib.pylab as plt
import numpy as np

from ANN_iCub_Interface.iCub import Joint_Reader, Joint_Writer, iCub_Interface, Visual_Reader, Skin_Reader, Kinematic_Reader, Kinematic_Writer
import ANN_iCub_Interface.Vocabs as iCub_Constants

# Test support files
from supplementary.auxilary_methods import encode

#########################################################
def call_test_jreader(iCub):
    """
        Call test for the joint reader module to check different errors.

        params:
            iCub     -- iCub_ANNarchy Interface
    """

    # add joint reader instances
    jreader = Joint_Reader.PyJointReader()
    jreader1 = Joint_Reader.PyJointReader()
    jreader2 = Joint_Reader.PyJointReader()


    print('finish adding')
    print('\n')

    # init joint reader
    jreader.init(iCub, "JReader", iCub_Constants.PART_KEY_HEAD, 0.5, 15)
    jreader.init(iCub, "JReader", iCub_Constants.PART_KEY_HEAD, 0.5, 15)        # double initialization
    jreader1.init(iCub, "JReader1", iCub_Constants.PART_KEY_RIGHT_ARM, -0.5, 15)      # negative sigma
    jreader1.init(iCub, "JReader1", iCub_Constants.PART_KEY_RIGHT_ARM, 0.5, 0, 2.0)   # neuron resolution
    jreader2.init(iCub, "JReader2", 'false_part_key', 0.5, 15)                     # false part key
    jreader2.init(iCub, "JReader2", iCub_Constants.PART_KEY_LEFT_ARM, 0.5, 0, 0.0)    # wrong population sizing
    if iCub.get_jreader_by_name("NO_NAME") == None:
        print("Not existing name!")

    jreader2.close(iCub)
    del jreader2

    print('finish JReader init')
    print('\n')

    # print joint resolutions for joint reader
    print(jreader.get_joints_deg_res())
    print(jreader.get_neurons_per_joint())

    print(jreader1.get_joints_deg_res())
    print(jreader1.get_neurons_per_joint())

    print('finish JReader resolutions')
    print('\n')

    # test read joints with joint reader
    print('read double_one')
    print(jreader.read_double_one(3))
    print('read double_all')
    print(jreader.read_double_all())
    print('read pop_one')
    print(jreader.read_pop_one(3))
    print('read pop_all')
    print(jreader.read_pop_all())

    print('finish JReader reading joints')
    print('\n')

    # close joint reader
    jreader.close(iCub)
    jreader1.close(iCub)

    print('finish JReader close')
    print('\n')


#########################################################
def call_test_jwriter(iCub):
    """
        Call test for the joint writer module to check different errors.

        params:
            iCub     -- iCub_ANNarchy Interface
    """

    # add joint writer instances
    jwriter = Joint_Writer.PyJointWriter()
    jwriter1 = Joint_Writer.PyJointWriter()
    jwriter2 = Joint_Writer.PyJointWriter()

    print('finish adding')
    print('\n')

    # init joint writer
    jwriter.init(iCub, "JointWriter", iCub_Constants.PART_KEY_HEAD, 15)
    jwriter.init(iCub, "JointWriter", iCub_Constants.PART_KEY_HEAD, 15)               # double initialization
    jwriter1.init(iCub, "JointWriter1", 'false_part_key', 15)               # false part key
    jwriter1.init(iCub, "JointWriter1", iCub_Constants.PART_KEY_RIGHT_ARM, 0, 2.0)

    jwriter2.close(iCub)

    print('finish JWriter init')
    print('\n')

    # print joint population resolutions and velocity for joint writer
    print(jwriter.get_joints_deg_res())
    print(jwriter.get_neurons_per_joint())
    print(jwriter.set_joint_velocity(15.0))


    print(jwriter1.get_joints_deg_res())
    print(jwriter1.get_neurons_per_joint())
    print(jwriter1.set_joint_velocity(10.0, joint=3))

    print(jwriter.get_joint_limits())

    print('finish JWriter resolutions')
    print('\n')

    # define test positions
    double_all = np.zeros(6)
    double_all_rel = np.ones(6) * 5.1
    test_pos = encode(iCub_Constants.PART_KEY_HEAD, 4, 15, 5, 0.5)
    test_pos_rel = encode(iCub_Constants.PART_KEY_HEAD, 4, 15, 5, 0.5, relative=True)
    pop_multiple = np.zeros((3, 15))
    pop_multiple_rel = np.zeros((3, 15))
    pop_all = np.zeros((6, 15))
    pop_all_rel = np.zeros((6, 15))

    for i in range(3):
        pop_multiple[i] = encode(iCub_Constants.PART_KEY_HEAD, i + 3, 15, 10., 0.5)
        pop_multiple_rel[i] = encode(iCub_Constants.PART_KEY_HEAD, i + 3, 15, 10., 0.5, relative=True)


    for i in range(6):
        pop_all[i] = encode(iCub_Constants.PART_KEY_HEAD, i, 15, 5., 0.5)
        pop_all_rel[i] = encode(iCub_Constants.PART_KEY_HEAD, i, 15, 5., 0.5, relative=True)

    print("write absolute values")
    # test writing absolute joint angles
    print('write double_one')
    print(jwriter.write_double_one(10.0, 4, "abs", True))
    time.sleep(2.5)
    print('write double_multiple')
    print(jwriter.write_double_multiple( [10., 10., 10.],  [3, 4, 5], "abs", True))
    time.sleep(2.5)
    print('write double_all')
    print(jwriter.write_double_all(double_all, "abs", True, 0))
    time.sleep(2.5)
    print('write pop_one')
    print(jwriter.write_pop_one(test_pos, 4, "abs", True))
    time.sleep(2.5)
    print('write pop_multiple')
    print(jwriter.write_pop_multiple(pop_multiple, [3, 4, 5], "abs", True))
    time.sleep(2.5)
    print('write pop_all')
    print(jwriter.write_pop_all(pop_all, "abs", True))

    print("write relative values")
    # test writing relative joint angles
    print('write double_one')
    print(jwriter.write_double_one(10.0, 4, "rel", True))
    time.sleep(2.5)
    print('write double_multiple')
    print(jwriter.write_double_multiple([10., 10., 10.], [3, 4, 5], "rel", True))
    time.sleep(2.5)
    print('write double_all')
    print(jwriter.write_double_all(double_all_rel, "rel", True))
    time.sleep(2.5)
    print('write pop_one')
    print(jwriter.write_pop_one(test_pos_rel, 4, "rel", True))
    time.sleep(2.5)
    print('write pop_multiple')
    print(jwriter.write_pop_multiple(pop_multiple_rel, [3, 4, 5], "rel", True))
    time.sleep(2.5)
    print('write pop_all')
    print(jwriter.write_pop_all(pop_all_rel, "rel", True))

    print('reset head position')
    print(jwriter.write_double_all(double_all, "abs", True))
    time.sleep(2.5)

    print('finish JWriter writing joints')
    print('\n')

    # close joint writer modules
    print(jwriter.close(iCub))
    print(jwriter1.close(iCub))

    print('finish JWriter close')
    print('\n')


#########################################################
def call_test_sreader(iCub):
    """
        Call test for the skin reader module to check different errors.

        params:
            iCub     -- iCub_ANNarchy Interface
    """

    # add skin reader instances
    sreader = Skin_Reader.PySkinReader()
    sreader1 = Skin_Reader.PySkinReader()

    print('finish skin reader adding')
    print('\n')

    # init skin reader
    sreader.init(iCub, "SkinReader", "r", True)       # correct init
    sreader.init(iCub, "SkinReader", "r", True)       # double init
    sreader1.init(iCub, "SkinReader1", "g", False)     # wrong eye descriptor
    sreader1.init(iCub, "SkinReader1", "l", False)     # correct init; non norm

    sreader1.close(iCub)

    print('finish SReader init')
    print('\n')

    # print taxel positions
    sreader.read_tactile()
    print(sreader.get_taxel_pos("arm"))
    print(sreader.get_taxel_pos("forearm"))
    print(sreader.get_taxel_pos("hand"))

    # print tactile data
    print(sreader.get_tactile_arm())
    print(sreader.get_tactile_forearm())
    print(sreader.get_tactile_hand())

    # close skin reader
    print(sreader.close(iCub))

    print('finish SReader close')
    print('\n')


#########################################################
def call_test_vreader(iCub):
    """
        Call test for the visual reader module to check different errors.

        params:
            iCub     -- iCub_ANNarchy Interface
    """

    # add visual reader instance
    visreader = Visual_Reader.PyVisualReader()

    print('finish visual reader adding')
    print('\n')

    # init visual reader
    print(visreader.init(iCub, "name", 'r', 75, 48, 320, 240))  # invalid field of view width
    print(visreader.init(iCub, "name", 'r', 60, 56, 320, 240))  # invalid field of view height
    print(visreader.init(iCub, "name", 't', 60, 48, 320, 240))  # invalid eye character
    print(visreader.init(iCub, "name", 'r', 60, 48, 160, 120))  # output size below input size
    print(visreader.init(iCub, "name", 'r'))                    # use of default values; init already done

    print('finish VReader init')
    print('\n')

    # record images from the iCub cameras
    test_img = visreader.read_robot_eyes()
    print(test_img.shape)
    if test_img.shape[0] > 0:
        test_img = test_img.reshape(120, 160)
        print(type(test_img), type(test_img[0][0]))
        plt.imshow(test_img, cmap='gray')
        plt.show()
        plt.pause(0.05)
    else:
        print('Image reading failed!')


    # first remove the old visual reader instance, then add and init a new visual reader instance
    visreader.close(iCub)
    print(visreader.init(iCub, "name", 'l'))                    # use of default values; reinitialization left eye

    # first remove the old visual reader instance, then add and init a new visual reader instance
    visreader.close(iCub)
    print(visreader.init(iCub, "name", 'b'))                    # use of default values; reinitialization binocular
    visreader.close(iCub)


#########################################################
def call_test_kreader(iCub):
    """
        Call test for the kinematic reader module to check different errors.

        params:
            iCub     -- iCub_ANNarchy Interface
    """
    # add kinematic reader instance
    kinreader = Kinematic_Reader.PyKinematicReader()

    # init kinematic reader
    print('Init kinematic reader')
    print(kinreader.init(iCub, "name", part="right_hand", version=2))   # wrong part key
    print(kinreader.init(iCub, "name", part="right_arm", version=-2))   # negative version
    print(kinreader.init(iCub, "name", part="right_arm", version=2))    # correct init
    print(kinreader.init(iCub, "name", part="right_arm", version=2))    # double init

    # get DOF of current kinematic chain
    print(kinreader.get_DOF())

    # print cartesian position of end effector (hand)
    print(kinreader.get_handposition())

    # close kinematic reader module
    kinreader.close(iCub)

    print('Finished Kinematic Reader test')
    print('\n')


#########################################################
def call_test_kwriter(iCub):
    """
        Call test for the kinematic writer module to check different errors.

        params:
            iCub     -- iCub_ANNarchy Interface
    """
    # add kinematic writer instance
    kinwriter = Kinematic_Writer.PyKinematicWriter()

    # init kinematic writer
    print('Init kinematic writer')
    print(kinwriter.init(iCub, "name", part="right_hand", version=2))   # wrong part key
    print(kinwriter.init(iCub, "name", part="right_arm", version=-2))   # negative version
    print(kinwriter.init(iCub, "name", part="right_arm", version=2))    # correct init
    print(kinwriter.init(iCub, "name", part="right_arm", version=2))    # double init

    # get DOF of current kinematic chain
    print(kinwriter.get_DOF())

    # print joint position for given position
    position = [-0.3, 0.0, 0.05 ]
    blocked = [0, 1, 2, 7, 8, 9]
    print(np.round(np.rad2deg(kinwriter.solve_InvKin(position, blocked)), 2))

    # close kinematic writer module
    kinwriter.close(iCub)

    print('Finished Kinematic Writer test')
    print('\n')


#########################################################


if __name__ == "__main__":
    iCub = iCub_Interface.ANNiCub_wrapper()

    if len(sys.argv) > 1:
        for command in sys.argv[1:]:
            if command == 'all':
                call_test_jreader(iCub)
                call_test_jwriter(iCub)
                call_test_sreader(iCub)
                call_test_vreader(iCub)
                call_test_kreader(iCub)
                call_test_kwriter(iCub)
            elif command == "noskin":
                call_test_jreader(iCub)
                call_test_jwriter(iCub)
                call_test_vreader(iCub)
                call_test_kreader(iCub)
                call_test_kwriter(iCub)
            elif command == "jreader":
                call_test_jreader(iCub)
            elif command == "jwriter":
                call_test_jwriter(iCub)
            elif command == "sreader":
                call_test_sreader(iCub)
            elif command == "vreader":
                call_test_vreader(iCub)
            elif command == "kreader":
                call_test_kreader(iCub)
            elif command == "kwriter":
                call_test_kwriter(iCub)
            else:
                print('No valid test command! Valid are: all, noskin, jreader, jwriter, sreader, vreader, kreader, kwriter')
    else:
        print('No valid test command! Valid are: all, noskin, jreader, jwriter, sreader, vreader, kreader, kwriter')

    print('finished call tests')
