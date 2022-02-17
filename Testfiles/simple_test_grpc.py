
"""
 *  Copyright (C) 2019-2022 Helge Uelo Dinkelbach, Torsten Fietzek
 *
 *  simple_test_grpc.py is part of the ANNarchy iCub interface
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
import subprocess
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

# ANNarchy iCub interface
from ANN_iCub_Interface import __root_path__ as interface_root
import ANN_iCub_Interface.Vocabs as iCub_Constants
from ANN_iCub_Interface.ANNarchy_iCub_Populations import *
from ANN_iCub_Interface.iCub import Joint_Reader, Joint_Writer, Skin_Reader, Visual_Reader, Kinematic_Reader, iCub_Interface

# ANNarchy
from ANNarchy import *

# Support functions
import supplementary.auxilary_methods as aux
import iCub_Python_Lib.plot_image_processing as plot


#########################################################
def call_test_jreader(iCub, ann_interface_root):
    """
        Simple test of the grpc connection between the iCub Interface and ANNarchy.
        -> Joint input

        params:
            iCub                -- iCub_ANNarchy Interface
            ann_interface_root  -- interface root path
    """
    joints = [3, 4, 5]
    popsize = 25

    # Add ANNarchy joint input population
    pop_jread = JointReadout(geometry = (len(joints), popsize), joints=joints, encoded=True)

    grpc_cpp_plugin = subprocess.check_output(["which", "grpc_cpp_plugin"]).strip().decode(sys.stdout.encoding)
    grpc_path = str(Path(grpc_cpp_plugin).resolve().parents[1]) + "/"
    grpc_include_path = grpc_path + "/include"
    grpc_lib_path = grpc_path + "/lib"
    print("Compile ANNarchy network.")
    compile(directory='results/annarchy_jreader', compiler_flags="-I"+ann_interface_root+" -Wl,-rpath,"+ann_interface_root+"/ANN_iCub_Interface/grpc/ -I" + grpc_include_path,
    extra_libs="-L" + grpc_lib_path + " -lprotobuf -lgrpc++ -lgrpc++_reflection -L"+ann_interface_root+"ANN_iCub_Interface/grpc/ -liCub_ANN_grpc",)

    # fancy other stuff ...
    for pop in populations():
        print(pop.ip_address, pop.port)
        print(pop.name, ':', pop.geometry)
        # connect ANNarchy populations via gRPC
        pop.connect()

    # add joint reader instances
    print('Add JReader module')
    jointreader = Joint_Reader.PyJointReader()
    if not jointreader.init_grpc(iCub, "name", iCub_Constants.PART_KEY_HEAD, sigma=1.5, n_pop=popsize, ip_address="0.0.0.0", port=pop_jread.port):
        print("Init Reader failed")
        exit(0)
    # print("Resolution", jointreader.get_joints_deg_res())

    # add joint writer instance
    jointwriter = Joint_Writer.PyJointWriter()
    if not jointwriter.init(iCub, "name", iCub_Constants.PART_KEY_HEAD, n_pop=popsize):
        print("Init Writer failed")
        exit(0)

    print("Simulate")
    # do something!
    simulate(1)
    print("Simulated")

    # Show ANNarchy input population firing rate
    print("Joint:", pop_jread.joints, "Value:", pop_jread.r)
    for j in joints:
        activity = pop_jread.r[j-np.amin(joints)]
        plt.subplot(1,2, 1)
        plt.plot(activity)
        plt.subplot(1,2, 2)
        plt.plot(jointreader.read_pop_one(j))
        plt.show()
        print("Joint " + str(j) + " decoded:", jointwriter.decode(activity, j))
        print("Read double:", jointreader.read_double_one(j))

    # close joint modules
    jointreader.close(iCub)
    jointwriter.close(iCub)

    clear()

    print('Finished Joint Reader test')
    print('\n')


#########################################################
def call_test_jwriter(iCub, ann_interface_root):
    """
        Simple test of the grpc connection between the iCub Interface and ANNarchy.
        -> Joint output

        params:
            iCub                -- iCub_ANNarchy Interface
            ann_interface_root  -- interface root path
    """

    popsize = 25
    sigma = 1.5

    # Add ANNarchy joint output population
    ## single joint motions
    joints_single = [4]
    pop_jctrl_single_double = JointControl(geometry = (len(joints_single), ), port=50010)
    pop_jctrl_single_pop = JointControl(geometry = (len(joints_single), popsize), port=50011)
    ## multiple joint motions
    joints_multi = [3, 4, 5]
    pop_jctrl_multi_double = JointControl(geometry = (len(joints_multi),), port=50012)
    pop_jctrl_multi_pop = JointControl(geometry = (len(joints_multi), popsize), port=50013)
    ## all joint motions
    joints_all = [0, 1, 2, 3, 4, 5]
    pop_jctrl_all_double = JointControl(geometry = (len(joints_all),), port=50014)
    pop_jctrl_all_pop = JointControl(geometry = (len(joints_all), popsize), port=50015)

    grpc_cpp_plugin = subprocess.check_output(["which", "grpc_cpp_plugin"]).strip().decode(sys.stdout.encoding)
    grpc_path = str(Path(grpc_cpp_plugin).resolve().parents[1]) + "/"
    grpc_include_path = grpc_path + "/include"
    grpc_lib_path = grpc_path + "/lib"
    print("Compile ANNarchy network.")
    compile(directory='results/annarchy_jwriter', compiler_flags="-I"+ann_interface_root+" -Wl,-rpath,"+ann_interface_root+"/ANN_iCub_Interface/grpc/ -I" + grpc_include_path,
    extra_libs="-L" + grpc_lib_path + " -lprotobuf -lgrpc++ -lgrpc++_reflection -L"+ann_interface_root+"ANN_iCub_Interface/grpc/ -liCub_ANN_grpc",)

    # fancy other stuff ...
    for pop in populations():
        print(pop.ip_address, pop.port)
        print(pop.name, ':', pop.geometry)
        # connect ANNarchy populations to interface via gRPC
        pop.connect()

    # add joint reader instances
    print('Add joint reader module')
    jointreader = Joint_Reader.PyJointReader()

    # Add joint writer modules, one for each writer population
    print('Add joint writer module')
    jointwriter = Joint_Writer.PyJointWriter()

    # init joint reader instance
    if not jointreader.init(iCub, "name", iCub_Constants.PART_KEY_HEAD, sigma=sigma, n_pop=popsize):
        print("Init Reader failed")
        exit(0)

    angles = np.array([15., 20., 25., -15., 25., 15.])
    angles_zero = [0., 0., 0., -0., 0., 0.]

    r_encoded = aux.encode(iCub_Constants.PART_KEY_HEAD, 0, popsize, angles[0], sigma)
    for i in range(1, angles.shape[0]):
        r_encoded = np.vstack((r_encoded, aux.encode(iCub_Constants.PART_KEY_HEAD, i, popsize, angles[i], sigma)))

    # set populations firing rates
    print("Set firing rates")
    pop_jctrl_single_double.r = angles[joints_single[0]]
    pop_jctrl_single_pop.r = r_encoded[joints_single[0]]

    pop_jctrl_multi_double.r = angles[joints_multi[0]:joints_multi[-1]+1]
    pop_jctrl_multi_pop.r = r_encoded[joints_multi[0]:joints_multi[-1]+1]

    pop_jctrl_all_double.r = angles
    pop_jctrl_all_pop.r = r_encoded

    print("Simulate")
    # do something!
    simulate(1)
    print("Simulated")

    # Test single joint motions
    if not jointwriter.init_grpc(iCub, "sd", iCub_Constants.PART_KEY_HEAD, n_pop=popsize, joints=joints_single, mode="abs", port=pop_jctrl_single_double.port):
        print("Init Writer failed")
        exit(0)
    print("r:", pop_jctrl_single_double.r)
    print(jointreader.read_double_one(joints_single[0]))
    jointwriter.retrieve_ANNarchy_input_single()
    jointwriter.write_ANNarchy_input_single()
    print(jointreader.read_double_one(joints_single[0]))

    jointwriter.write_double_one(0., joints_single[0], "abs")
    jointwriter.close(iCub)

    if not jointwriter.init_grpc(iCub, "sp", iCub_Constants.PART_KEY_HEAD, n_pop=popsize, joints=joints_single, mode="abs", port=pop_jctrl_single_pop.port):
        print("Init Writer failed")
        exit(0)
    print("r:", pop_jctrl_single_pop.r)
    print(jointreader.read_double_one(joints_single[0]))
    jointwriter.retrieve_ANNarchy_input_single_enc()
    jointwriter.write_ANNarchy_input_single_enc()
    print(jointreader.read_double_one(joints_single[0]))

    jointwriter.write_double_one(0., joints_single[0], "abs")
    jointwriter.close(iCub)

    # Test multiple joint motions
    if not jointwriter.init_grpc(iCub, "md", iCub_Constants.PART_KEY_HEAD, n_pop=popsize, joints=joints_multi, mode="abs", port=pop_jctrl_multi_double.port):
        print("Init Writer failed")
        exit(0)
    print("r:", pop_jctrl_multi_double.r)
    print(jointreader.read_double_all())
    jointwriter.retrieve_ANNarchy_input_multi()
    jointwriter.write_ANNarchy_input_multi()
    print(jointreader.read_double_all())

    jointwriter.write_double_all(angles_zero, "abs")
    jointwriter.close(iCub)

    if not jointwriter.init_grpc(iCub, "mp", iCub_Constants.PART_KEY_HEAD, n_pop=popsize, joints=joints_multi, mode="abs", port=pop_jctrl_multi_pop.port):
        print("Init Writer failed")
        exit(0)
    print("r:", pop_jctrl_multi_pop.r)
    print(jointreader.read_double_all())
    jointwriter.retrieve_ANNarchy_input_multi_enc()
    jointwriter.write_ANNarchy_input_multi_enc()
    print(jointreader.read_double_all())

    jointwriter.write_double_all(angles_zero, "abs")
    jointwriter.close(iCub)

    # Test all joint motions
    if not jointwriter.init_grpc(iCub, "ad", iCub_Constants.PART_KEY_HEAD, n_pop=popsize, joints=[], mode="abs", port=pop_jctrl_all_double.port):
        print("Init Writer failed")
        exit(0)
    print("r:", pop_jctrl_all_double.r)
    print(jointreader.read_double_all())
    jointwriter.retrieve_ANNarchy_input_all()
    jointwriter.write_ANNarchy_input_all()
    print(jointreader.read_double_all())

    jointwriter.write_double_all(angles_zero, "abs")
    jointwriter.close(iCub)

    if not jointwriter.init_grpc(iCub, "ap", iCub_Constants.PART_KEY_HEAD, n_pop=popsize, joints=[], mode="abs", port=pop_jctrl_all_pop.port):
        print("Init Writer failed")
        exit(0)
    print("r:", pop_jctrl_all_pop.r)
    print(jointreader.read_double_all())
    jointwriter.retrieve_ANNarchy_input_all_enc()
    jointwriter.write_ANNarchy_input_all_enc()
    print(jointreader.read_double_all())

    jointwriter.write_double_all(angles_zero, "abs")

    # Close joint modules
    jointwriter.close(iCub)
    jointreader.close(iCub)

    clear()

    print('Finished Joint Writer test')
    print('\n')


#########################################################
def call_test_sreader(iCub, ann_interface_root):
    """
        Simple test of the grpc connection between the iCub Interface and ANNarchy.
        -> Tactile input

        params:
            iCub     -- iCub_ANNarchy Interface
            ann_interface_root  -- interface root path
    """

    # Add ANNarchy tactile input population
    pop_sread_arm = SkinPopulation(geometry = (380,), skin_section="arm")
    pop_sread_forearm = SkinPopulation(geometry = (240,), skin_section="forearm")

    # gRPC paths, only needed for local gRPC installation
    grpc_cpp_plugin = subprocess.check_output(["which", "grpc_cpp_plugin"]).strip().decode(sys.stdout.encoding)
    grpc_path = str(Path(grpc_cpp_plugin).resolve().parents[1]) + "/"
    grpc_include_path = grpc_path + "/include"
    grpc_lib_path = grpc_path + "/lib"

    print("Compile ANNarchy network.")
    # compile ANNarchy network
    compile(directory='results/annarchy_sreader', compiler_flags="-I"+ann_interface_root+" -Wl,-rpath,"+ann_interface_root+"/ANN_iCub_Interface/grpc/ -I" + grpc_include_path,
    extra_libs="-L" + grpc_lib_path + " -lprotobuf -lgrpc++ -lgrpc++_reflection -L"+ann_interface_root+"ANN_iCub_Interface/grpc/ -liCub_ANN_grpc",)

    # fancy other stuff ...
    for pop in populations():
        print(pop.ip_address, pop.port)
        print(pop.name, ':', pop.geometry)
        # connect ANNarchy populations via gRPC
        pop.connect()

    # add skin reader instances
    print('Add skin reader')
    skinreader = Skin_Reader.PySkinReader()

    # init skin reader
    if not skinreader.init_grpc(iCub, "name", arm="r", ip_address="0.0.0.0", port=pop_sread_arm.port):
        print("Init failed")
        exit(0)

    print("Skin arm size:", skinreader.get_tactile_arm_size())
    print("Skin forearm size:", skinreader.get_tactile_forearm_size())

    print("Simulate")
    # do something!
    simulate(1)
    print("Simulated")

    # Show skin population firing rate
    print("arm:", pop_sread_arm.r)
    print("forearm:", pop_sread_forearm.r)


    # close skin reader
    skinreader.close(iCub)

    clear()

    print('Finished Skin Reader test')
    print('\n')


#########################################################
def call_test_vreader(iCub, ann_interface_root):
    """
        Simple test of the grpc connection between the iCub Interface and ANNarchy.
        -> Visual input

        params:
            iCub                -- iCub_ANNarchy Interface
            ann_interface_root  -- interface root path
    """

    # Create ANNarchy visual input population
    pop_vis = VisionPopulation( geometry = (240,320) )

    grpc_cpp_plugin = subprocess.check_output(["which", "grpc_cpp_plugin"]).strip().decode(sys.stdout.encoding)
    grpc_path = str(Path(grpc_cpp_plugin).resolve().parents[1]) + "/"
    grpc_include_path = grpc_path + "/include"
    grpc_lib_path = grpc_path + "/lib"
    print("Compile ANNarchy network.")
    compile(directory='results/annarchy_vreader', compiler_flags="-I"+ann_interface_root+" -Wl,-rpath,"+ann_interface_root+"/ANN_iCub_Interface/grpc/ -I" + grpc_include_path,
    extra_libs="-L" + grpc_lib_path + " -lprotobuf -lgrpc++ -lgrpc++_reflection -L"+ann_interface_root+"ANN_iCub_Interface/grpc/ -liCub_ANN_grpc",)

    # fancy other stuff ...
    for pop in populations():
        print(pop.ip_address, pop.port)
        print(pop.name, ':', pop.geometry)
        # connect ANNarchy populations via gRPC
        pop.connect()

    print("offset", pop_vis.offset)
    print("period", pop_vis.period)

    # add visual reader instance
    visreader = Visual_Reader.PyVisualReader()

    # init visual reader
    print('Init visual reader')
    if not visreader.init_grpc(iCub, "name", 'l', ip_address="0.0.0.0", port=pop_vis.port):
        print("Init failed")
        exit(0)

    print("Simulate")
    # do something!
    simulate(1)
    print("Simulated")

    # Show visual population firing rate
    plot.show_image_matplot(pop_vis.r, "pop_vis", "x", "y")
    print(np.amax(pop_vis.r))

    # Close visual reader module
    visreader.close(iCub)

    clear()

    print('Finished Visual Reader test')
    print('\n')


#########################################################
def call_test_kreader(iCub, ann_interface_root):
    """
        Simple test of the grpc connection between the iCub Interface and ANNarchy.
        -> Kinematic input

        params:
            iCub                -- iCub_ANNarchy Interface
            ann_interface_root  -- interface root path
    """

    # Create ANNarchy kinematic input population
    pop_kin = KinematicForward(geometry = (3,) )

    grpc_cpp_plugin = subprocess.check_output(["which", "grpc_cpp_plugin"]).strip().decode(sys.stdout.encoding)
    grpc_path = str(Path(grpc_cpp_plugin).resolve().parents[1]) + "/"
    grpc_include_path = grpc_path + "/include"
    grpc_lib_path = grpc_path + "/lib"
    print("Compile ANNarchy network.")
    compile(directory='results/annarchy_kreader', compiler_flags="-I"+ann_interface_root+" -Wl,-rpath,"+ann_interface_root+"/ANN_iCub_Interface/grpc/ -I" + grpc_include_path,
    extra_libs="-L" + grpc_lib_path + " -lprotobuf -lgrpc++ -lgrpc++_reflection -L"+ann_interface_root+"ANN_iCub_Interface/grpc/ -liCub_ANN_grpc",)
    for pop in populations():
        print(pop.ip_address, pop.port)
        print(pop.name, ':', pop.geometry)
        # connect ANNarchy populations via gRPC
        pop.connect()

    # add kinematic reader instance
    kinreader = Kinematic_Reader.PyKinematicReader()

    # init kinematic reader
    print('Init kinematic reader')
    if not kinreader.init_grpc(iCub, "name", part="right_arm", version=2, ip_address="0.0.0.0", port=pop_kin.port):
        print("Init failed")
        exit(0)

    print("Simulate")
    # do something!
    simulate(1)
    print("Simulated")

    # Show kinematic population firing rate
    print(pop_kin.r)

    # Close kinematic reader module
    kinreader.close(iCub)

    clear()

    print('Finished Kinematic Reader test')
    print('\n')

#########################################################
if __name__ == "__main__":
    # prepare iCub Interface
    iCub = iCub_Interface.ANNiCub_wrapper()
    ann_interface_root = interface_root + "/"

    if not os.path.isdir("./results"):
        os.mkdir("./results")

    if len(sys.argv) > 1:
        for command in sys.argv[1:]:
            if command == 'all':
                call_test_jreader(iCub, ann_interface_root)
                call_test_jwriter(iCub, ann_interface_root)
                call_test_sreader(iCub, ann_interface_root)
                call_test_vreader(iCub, ann_interface_root)
                call_test_kreader(iCub, ann_interface_root)
            elif command == "noskin":
                call_test_jreader(iCub, ann_interface_root)
                call_test_jwriter(iCub, ann_interface_root)
                call_test_vreader(iCub, ann_interface_root)
                call_test_kreader(iCub, ann_interface_root)
            elif command == "jreader":
                call_test_jreader(iCub, ann_interface_root)
            elif command == "jwriter":
                call_test_jwriter(iCub, ann_interface_root)
            elif command == "sreader":
                call_test_sreader(iCub, ann_interface_root)
            elif command == "vreader":
                call_test_vreader(iCub, ann_interface_root)
            elif command == "kreader":
                call_test_kreader(iCub, ann_interface_root)
            else:
                print('No valid test command! Valid are: all, noskin, jreader, jwriter, sreader, vreader, kreader')
    else:
        print('No valid test command! Valid are: all, noskin, jreader, jwriter, sreader, vreader, kreader')

    del iCub
    print('finished grpc tests')
