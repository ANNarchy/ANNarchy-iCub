"""
Created on 2023-08-01 15:43:28

@author: Torsten Fietzek

Tactile perception example

"""

import sys

import ANNarchy as ann
import example_parameter as params
import iCub_Python_Lib.iCubSim_world_controller as iSim
import matplotlib.pyplot as plt

import ANN_iCub_Interface.Vocabs as iCub_Const
from ANN_iCub_Interface import __ann_compile_args__, __ann_extra_libs__
from ANN_iCub_Interface.ANNarchy_iCub_Populations import SkinPopulation
from ANN_iCub_Interface.iCub import Skin_Reader, iCub_Interface


######################################################################
# Example implementation using the ANNarchy-iCub-Interface
def tactile_prcptn_iCub_ANN():

    print("Example for Skin Reader.")
    ######################################################################
    # Add interface instances

    # Interface main wrapper, is needed once
    iCub = iCub_Interface.ANNiCub_wrapper()

    # Add skin reader instance
    sreader = Skin_Reader.PySkinReader()

    # Init interface instances
    if not sreader.init(iCub, "skin_right", "r", True, ini_path=params.INTERFACE_INI_PATH):
        sys.exit("Initialization failed!")

    ######################################################################
    # Read skin sensor data -> buffered
    for i in range(10):
        # read tactile data
        sreader.read_tactile()

    # print tactile data
    print("Data arm:")
    print(sreader.get_tactile_arm())

    print("Data forearm:")
    print(sreader.get_tactile_forearm())

    print("Data hand:")
    print(sreader.get_tactile_hand())

    ######################################################################
    # Read skin sensor data -> skin section specific
    for i in range(10):
        # print tactile data
        print("Data arm:")
        print(sreader.read_skin_arm())

        print("Data forearm:")
        print(sreader.read_skin_forearm())

        print("Data hand:")
        print(sreader.read_skin_hand())

    ######################################################################
    # Close interface instances
    sreader.close(iCub)


######################################################################
# Example implementation using the ANNarchy-iCub-Interface with gRPC and ANNarchy
def tactile_prcptn_iCub_ANN_grpc():
    # plt.ion()
    print("Example for Skin Reader with direct connection to ANNarchy.")
    ######################################################################
    # Create, compile and connect ANNarchy Skin input population
    pop_sread_arm = SkinPopulation(geometry=(iCub_Const.SKIN_SECTION_SIZE_ARM,), skin_section="arm")
    pop_sread_forearm = SkinPopulation(geometry=(iCub_Const.SKIN_SECTION_SIZE_FOREARM,), skin_section="forearm")
    pop_sread_hand = SkinPopulation(geometry=(iCub_Const.SKIN_SECTION_SIZE_HAND,), skin_section="hand")

    print("Compile ANNarchy network.")
    ann.compile(directory='./annarchy/annarchy_sreader', compiler_flags=__ann_compile_args__, extra_libs=__ann_extra_libs__)

    for pop in ann.populations():
        print(pop.name, ':', pop.geometry)
        print(pop.ip_address, pop.port)
        # connect ANNarchy populations to gRPC-socket
        pop.connect()

    ######################################################################
    # Set-up ANNarchy-iCub-Interface to connect to ANNarchy population

    # Interface main wrapper, is needed once
    iCub = iCub_Interface.ANNiCub_wrapper()

    # Skin Reader instance with ANNarchy connection
    skinreader = Skin_Reader.PySkinReader()
    if not skinreader.init_grpc(iCub, "tactile", arm="r", ini_path=params.INTERFACE_INI_PATH, ip_address=params.ip_address, port=pop_sread_arm.port):
        sys.exit("Initialization failed!")

    print("Skin arm size:", skinreader.get_tactile_arm_size(), "\n    Population size", pop_sread_arm.geometry)
    print("Skin forearm size:", skinreader.get_tactile_forearm_size(), "\n    Population size", pop_sread_forearm.geometry)
    print("Skin forearm size:", skinreader.get_tactile_hand_size(), "\n    Population size", pop_sread_hand.geometry)

    ######################################################################
    # Prepare world for skin test
    wc = iSim.WorldController()
    sphere = wc.create_object("ssph", [0.03], [0, 1, 1], [1, 1, 1])

    ######################################################################
    # Simulate with ANNarchy to retrieve the data via gRPC connection
    plt.ion()

    fig, ax = plt.subplots(1, 3, figsize=(12, 6))

    fig.suptitle("Skin sensors for the right arm")
    ax[0].set_title("Upper arm")
    line0, = ax[0].plot(pop_sread_arm.r, "b")
    ax[0].set_xlabel("Neuron index")
    ax[0].set_ylabel("Neuronal activity")
    ax[0].set_ylim(-0.05, 1.1)

    ax[1].set_title("Forearm")
    line1, = ax[1].plot(pop_sread_forearm.r, "b")
    ax[1].set_xlabel("Neuron index")
    ax[1].set_ylabel("Neuronal activity")
    ax[1].set_ylim(-0.05, 1.1)

    ax[2].set_title("Hand")
    line2, = ax[2].plot(pop_sread_hand.r, "b")
    ax[2].set_xlabel("Neuron index")
    ax[2].set_ylabel("Neuronal activity")
    ax[2].set_ylim(-0.05, 1.1)

    fig.tight_layout()
    fig.canvas.draw()
    fig.canvas.flush_events()
    plt.pause(0.1)

    for i in range(5):
        print("Simulate")
        ann.simulate(1)
        wc.move_object(sphere, [-0.125, 0.6, 0.25])

        # Show skin population firing rate
        line0.set_ydata(pop_sread_arm.r)
        line1.set_ydata(pop_sread_forearm.r)
        line2.set_ydata(pop_sread_hand.r)
        plt.draw()

    plt.show(block=True)

    ######################################################################
    # Clean-up

    # close skin reader
    skinreader.close(iCub)


if __name__ == '__main__':
    if params.GAZEBO_SIM:
        sys.exit("Tactile perception does not yet work with gazebo simulator!")
    if params.use_grpc:
        tactile_prcptn_iCub_ANN_grpc()
    else:
        tactile_prcptn_iCub_ANN()
