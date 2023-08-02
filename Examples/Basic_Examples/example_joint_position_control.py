"""
Created on 2023-07-31 15:57:23

@author: Torsten Fietzek

joint position control example

"""

import sys
import time

import ANNarchy as ann
import example_parameter as params
import matplotlib.pyplot as plt
import numpy as np

from ANN_iCub_Interface import Vocabs as iCub_Const
from ANN_iCub_Interface import __ann_compile_args__, __ann_extra_libs__
from ANN_iCub_Interface.ANNarchy_iCub_Populations import JointControl, JointReadout
from ANN_iCub_Interface.iCub import Joint_Reader, Joint_Writer, iCub_Interface


######################################################################
# Example implementation using the ANNarchy-iCub-Interface
def position_ctrl_ANN_iCub_Interface():
    print("Example for joint position control.")

    ######################################################################
    # Add interface instances

    # Interface main wrapper, is needed once
    iCub = iCub_Interface.ANNiCub_wrapper()

    # Reader/Writer instances
    reader = Joint_Reader.PyJointReader()
    writer = Joint_Writer.PyJointWriter()

    # Init interface instances
    if not reader.init(iCub, "read_head", iCub_Const.PART_KEY_HEAD, 0.5, 15, ini_path=params.INTERFACE_INI_PATH):
        sys.exit("Initialization failed!")
    if not writer.init(iCub, "write_head", iCub_Const.PART_KEY_HEAD, 0.5, 15, ini_path=params.INTERFACE_INI_PATH):
        sys.exit("Initialization failed!")

    ######################################################################
    # Go to head zero position
    writer.write_double_all([0., 0., 0., 0., 0., 0.], mode="abs", blocking=True)

    ######################################################################
    # Move the head to predefined position
    print('----- Move head absolute -----')
    new_pos = np.array([5., 0., -25., 0., 25., 10.])
    writer.write_double_all(new_pos, mode="abs", blocking=True)

    ######################################################################
    # Retrieve head joints position
    print(reader.read_double_all())
    time.sleep(3.)

    ######################################################################
    # Move the head relative to the current position
    print('----- Move head relative -----')
    rel_pos = -new_pos
    writer.write_double_all(rel_pos, mode="rel", blocking=True)

    ######################################################################
    # Retrieve head joints position
    print(reader.read_double_all())
    time.sleep(3.)

    ######################################################################
    # Go to head zero position
    writer.write_double_all([0., 0., 0., 0., 0., 0.], mode="abs", blocking=True)

    ######################################################################
    # Close interface instances
    print('----- Close interface instances -----')
    iCub.clear()


######################################################################
# Example implementation using the ANNarchy-iCub-Interface with gRPC and ANNarchy
def position_ctrl_ANN_iCub_Interface_grpc():
    print("Example for joint position control with direct connection to ANNarchy.")

    ######################################################################
    # Set up ANNarchy network

    # Add ANNarchy-iCub-Populations
    pop_jread_double = JointReadout(geometry=(len(params.joints_head),), joints=params.joints_head, encoded=False, ip_address=params.ip_address, port=50005, name="head_read")
    pop_jread_pop = JointReadout(geometry=(len(params.joints_head), params.popsize), joints=params.joints_head, encoded=True, port=50005)
    pop_jwrite_double = JointControl(geometry=(len(params.joints_head),), neuron=ann.Neuron(equations="r=sum(exc)*1.1 - 0.3"),
                                     ip_address=params.ip_address, port=50010, name="head_write")

    mon_read_double = ann.Monitor(pop_jread_double, ["r"])
    mon_write_double = ann.Monitor(pop_jwrite_double, ["r"])

    read2write = ann.Projection(pop_jread_double, pop_jwrite_double, target="exc", name="read2write")
    read2write.connect_one_to_one()

    print("Compile ANNarchy network.")
    ann.compile(directory='./annarchy/annarchy_pos_ctrl', compiler_flags=__ann_compile_args__, extra_libs=__ann_extra_libs__)

    print("Populations")
    for pop in ann.populations():
        print(pop.name, ':', pop.geometry)
        try:
            print(pop.ip_address, pop.port)
            # connect ANNarchy populations to gRPC-socket
            pop.connect()
        except Exception:
            pass

    print("Projections")
    for proj in ann.projections():
        print(proj.name)

    ######################################################################
    # Set up ANNarchy-iCub-Interface to connect to ANNarchy population

    # Interface main wrapper, is needed once
    iCub = iCub_Interface.ANNiCub_wrapper()

    # Joint Reader
    joint_reader = Joint_Reader.PyJointReader()
    if not joint_reader.init_grpc(iCub, "name", iCub_Const.PART_KEY_HEAD, sigma=params.sigma, n_pop=params.popsize,
                                  ini_path=params.INTERFACE_INI_PATH, ip_address=params.ip_address, port=pop_jread_double.port):
        sys.exit("Initialization failed!")

    # Joint Writer
    joint_writer = Joint_Writer.PyJointWriter()
    if not joint_writer.init_grpc(iCub, "name", iCub_Const.PART_KEY_HEAD, n_pop=params.popsize, joints=params.joints_head, mode="abs", blocking=True,
                                  speed=60., ini_path=params.INTERFACE_INI_PATH, ip_address=params.ip_address, port=pop_jwrite_double.port):
        sys.exit("Initialization failed!")

    ######################################################################
    # Move the joints dependent on the ANNarchy network

    # Save reset position
    start_pos_head = joint_reader.read_double_all()

    # Go to start position
    joint_writer.write_double_all([0., 0., 0., 0., 0., 0.], "abs")

    # Motion with network interaction
    for i in range(params.steps_pos):
        if i % 10 == 0:
            print("Step:", i)
            print("Current joint angles:", np.round(pop_jread_double.r, 2))
            print("Joint command:", np.round(pop_jwrite_double.r, 2))

        ann.step()

        # Retrieve joint command from ANNarchy population and write to robot
        joint_writer.retrieve_ANNarchy_input_multi()
        joint_writer.write_ANNarchy_input_multi()

    ######################################################################
    # Retrieve data from ANNarchy and plot the joint data

    # Readout vs Command

    read_data = mon_read_double.get("r")
    write_data = mon_write_double.get("r")

    fig = plt.figure(figsize=(12, 6))
    fig.suptitle("Joint angles: command vs. readout")

    ax0 = fig.add_subplot(131)
    ax0.set_title("Joint 2")
    ax0.plot(read_data[:, 0], "b", label="Readout")
    ax0.plot(write_data[:, 0], "r", label="Command")
    ax0.set_xlabel("time")
    ax0.set_ylabel("joint angle [deg]")
    ax1 = fig.add_subplot(132)
    ax1.set_title("Joint 3")
    ax1.plot(read_data[:, 1], "b", write_data[:, 1], "r")
    ax1.set_xlabel("time")
    ax1.set_ylabel("joint angle [deg]")
    ax2 = fig.add_subplot(133,)
    ax2.set_title("Joint 4")
    ax2.plot(read_data[:, 2], "b", write_data[:, 2], "r")
    ax2.set_xlabel("time")
    ax2.set_ylabel("joint angle [deg]")

    fig.legend(loc=8, ncol=2)

    # Population Code

    fig1 = plt.figure(figsize=(12, 6))
    fig1.suptitle("Population encoded joint angles")

    ax0_1 = fig1.add_subplot(131)
    ax0_1.set_title("Joint 2")
    ax0_1.plot(pop_jread_pop.r[0, :], "g", label="ANNarchy")
    ax0_1.plot(joint_reader.read_pop_one(params.joints_head[0]), "m", label="Interface")
    ax0_1.set_xlabel("neuron index")
    ax0_1.set_ylabel("neural activity")
    ax1_1 = fig1.add_subplot(132)
    ax1_1.set_title("Joint 3")
    ax1_1.plot(pop_jread_pop.r[1, :], "g", joint_reader.read_pop_one(params.joints_head[1]), "m")
    ax1_1.set_xlabel("neuron index")
    ax1_1.set_ylabel("neural activity")
    ax2_1 = fig1.add_subplot(133,)
    ax2_1.set_title("Joint 4")
    ax2_1.plot(pop_jread_pop.r[2, :], "g", joint_reader.read_pop_one(params.joints_head[2]), "m")
    ax2_1.set_xlabel("neuron index")
    ax2_1.set_ylabel("neural activity")

    fig1.legend(loc=8, ncol=2)
    plt.show()

    ######################################################################
    # Clean-up

    # Return to reset position
    print("Reset position")
    joint_writer.write_double_all(start_pos_head, mode="abs")

    # Clean up the interface
    iCub.clear()


if __name__ == '__main__':
    if params.use_grpc:
        position_ctrl_ANN_iCub_Interface_grpc()
    else:
        position_ctrl_ANN_iCub_Interface()
