"""
Created on 2023-07-31 15:57:59

@author: Torsten Fietzek

Visual perception example

"""

import sys

import ANNarchy as ann
import example_parameter as params
import iCub_Python_Lib.plot_image_processing as plot
import matplotlib.pyplot as plt
import numpy as np

from ANN_iCub_Interface import __ann_compile_args__, __ann_extra_libs__
from ANN_iCub_Interface.ANNarchy_iCub_Populations import VisionPopulation
from ANN_iCub_Interface.iCub import Visual_Reader, iCub_Interface


######################################################################
# Example implementation using the ANNarchy-iCub-Interface
def visual_input_ANN_iCub_Interface():

    print("Example for Visual Reader.")
    ######################################################################
    # Add interface instances

    # Interface main wrapper, is needed once
    iCub = iCub_Interface.ANNiCub_wrapper()

    # Add visual reader instances
    visreader = Visual_Reader.PyVisualReader()
    visreader_r = Visual_Reader.PyVisualReader()
    visreader_l = Visual_Reader.PyVisualReader()

    # Init interface instances
    init = visreader.init(iCub, "both", 'b', ini_path=params.INTERFACE_INI_PATH)
    init &= visreader_r.init(iCub, "right", 'r', ini_path=params.INTERFACE_INI_PATH)
    init &= visreader_l.init(iCub, "left", 'l', ini_path=params.INTERFACE_INI_PATH)
    if not init:
        sys.exit("Initialization failed!")

    ######################################################################
    # Read camera images from robot

    # grayscale/RGB images (dependent on INI-file parameter); preprocessed -> range [0., 1.]
    test_imgs = visreader.read_robot_eyes()
    test_imgs = test_imgs.reshape(2, 240, 320)

    plt.figure(figsize=(10, 5))
    plt.tight_layout()
    plt.subplot(121)
    plt.title("Left camera image")
    plt.imshow(test_imgs[1], cmap="gray")

    plt.subplot(122)
    plt.title("Right camera image")
    plt.imshow(test_imgs[0], cmap="gray")
    plt.show()

    # RGB images; no preprocessing -> range [0, 255]
    imgleft = np.array(visreader_l.retrieve_robot_eye()).reshape(240, 320, 3)
    imgright = np.array(visreader_r.retrieve_robot_eye()).reshape(240, 320, 3)

    plt.figure(figsize=(10, 5))
    plt.tight_layout()
    plt.subplot(121)
    plt.title("Left camera image")
    plt.imshow(imgleft)

    plt.subplot(122)
    plt.title("Right camera image")
    plt.imshow(imgright)
    plt.show()

    ######################################################################
    # Close interface instances
    iCub.clear()


######################################################################
# Example implementation using the ANNarchy-iCub-Interface with gRPC and ANNarchy
def visual_input_ANN_iCub_Interface_grpc():

    print("Example for Visual Reader with direct connection to ANNarchy.")
    ######################################################################
    # Create, compile and connect ANNarchy visual input population

    pop_vis = VisionPopulation(geometry=(240, 320))

    print("Compile ANNarchy network.")
    ann.compile(directory='./annarchy/annarchy_vreader', compiler_flags=__ann_compile_args__, extra_libs=__ann_extra_libs__)

    for pop in ann.populations():
        print(pop.name, ':', pop.geometry)
        print(pop.ip_address, pop.port)
        # connect ANNarchy populations to gRPC-socket
        pop.connect()

    print("offset", pop_vis.offset)
    print("period", pop_vis.period)

    ######################################################################
    # Set-up ANNarchy-iCub-Interface to connect to ANNarchy population

    # Interface main wrapper, is needed once
    iCub = iCub_Interface.ANNiCub_wrapper()

    # Add visual reader instance
    visreader = Visual_Reader.PyVisualReader()
    print('Init visual reader')
    if not visreader.init_grpc(iCub, "name", 'l', ini_path=params.INTERFACE_INI_PATH, ip_address=params.ip_address, port=pop_vis.port):
        sys.exit("Initialization failed!")

    ######################################################################
    # Simulate with ANNarchy to retrieve and show the image data via gRPC connection

    ann.simulate(1)
    print("Simulated")

    # Show visual population firing rate
    plot.show_image_matplot(pop_vis.r, "pop_vis", "", "")

    ######################################################################
    # Clean-up

    # Close visual reader module
    visreader.close(iCub)   # or iCub.clear() for closing all interface instances


if __name__ == '__main__':
    if params.use_grpc:
        visual_input_ANN_iCub_Interface_grpc()
    else:
        visual_input_ANN_iCub_Interface()
