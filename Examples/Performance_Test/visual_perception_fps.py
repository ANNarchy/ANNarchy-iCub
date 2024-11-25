"""
###### Created on Thu Jan 27 17:43:07 CET 2022

@author: Torsten Fietzek

Visual perception performance test

"""
######################################################################
########################## Import modules  ###########################
######################################################################

import sys
import subprocess
from pathlib import Path
from timeit import default_timer as timer

import ANNarchy as ann
import cv2
import matplotlib.pyplot as plt
import numpy as np


#########################################################
def speed_test_yarp_manual(test_count):
    """
        Test the performance of the visual perception with YARP-Python API and a manual transfer to ANNarchy.

    """
    print("----- Python YARP performance test -----")

    import yarp

    ROBOT_PREFIX = "icubSim"
    CLIENT_PREFIX = "client"
    norm = 1./255

    ######################################################################
    ######################### Init YARP network ##########################

    print('----- Init YARP network -----')
    # network initialization and check
    yarp.Network.init()
    if not yarp.Network.checkNetwork():
        print('[ERROR] Please try running yarp server')

    print('----- Open ports -----')
    # Initialization of all needed ports
    # Port for right eye image
    input_port_right_eye = yarp.Port()
    if not input_port_right_eye.open("/" + CLIENT_PREFIX + "/eyes/right"):
        print("[ERROR] Could not open right eye port")
    if not yarp.Network.connect("/" + ROBOT_PREFIX + "/cam/right", "/" + CLIENT_PREFIX + "/eyes/right"):
        print("[ERROR] Could not connect input_port_right_eye")


    ######################################################################
    ################## Initialization of both eye images #################

    print('----- Init image array structures -----')
    # Create numpy array to receive the image and the YARP image wrapped around it
    right_eye_img_array = np.ones((240, 320, 3), np.uint8)
    right_eye_yarp_image = yarp.ImageRgb()
    right_eye_yarp_image.resize(320, 240)

    right_eye_yarp_image.setExternal(
        right_eye_img_array.data, right_eye_img_array.shape[1], right_eye_img_array.shape[0])


    ######################################################################
    ######################## Init ANNarchy network #######################

    print('----- Init ANNarchy network -----')
    neuron = ann.Neuron(
        parameters=
            """
                baseline = 0 :int
            """,
        equations=
            """
                r = baseline :int
            """
    )

    vis_pop = ann.Population(geometry=(240, 320,3), neuron=neuron)
    ann.compile()


    ######################################################################
    ################ Performance test for reading images #################

    duration = np.zeros((test_count,))
    print("----- Start Performance Test -----")
    for i in range(test_count):
        start = timer()
        # Read the images from the robot cameras
        read = input_port_right_eye.read(right_eye_yarp_image)
        while not read:
            time.sleep(0.001)
            read = input_port_right_eye.read(right_eye_yarp_image)

        if right_eye_yarp_image.getRawImage().__int__() != right_eye_img_array.__array_interface__['data'][0]:
            print("read() reallocated my right_eye_yarp_image!")
        # vis_pop.baseline = right_eye_img_array
        # vis_pop.baseline = cv2.cvtColor(right_eye_img_array, cv2.COLOR_RGB2GRAY) * norm
        # ann.simulate(1)
        duration[i] = timer() - start
        if np.amax(right_eye_img_array) == 0:
            print("Read failed!")
            i -= 1
        right_eye_img_array[:] = 0.


    print("----- Performance Test Finished -----")
    mean_time = round(np.mean(duration)*1000, 2)
    std_time = round(np.std(duration)*1000, 2)
    print("Mean:", mean_time)
    print("STD:", std_time)
    print("Mean FPS:", round(1./(mean_time/1000), 2))


    ######################################################################
    ######################## Closing the program: ########################
    #### Delete objects/models and close ports, network, motor cotrol ####
    print('----- Close opened ports -----')

    # disconnect the ports
    if not yarp.Network.disconnect("/" + ROBOT_PREFIX + "/cam/right", input_port_right_eye.getName()):
        print("[ERROR] Could not disconnect input_port_right_eye")

    # close the ports
    input_port_right_eye.close()

    # close the yarp network
    yarp.Network.fini()

    print('Finished Visual Perception test\n')

    return mean_time, std_time


#########################################################
def speed_test_interface_manual(test_count):
    """
        Test the performance of the visual perception with the ANNarchy-iCub-Interface and a manual transfer to ANNarchy.

    """
    print("----- Interface with manual transport performance test -----")

    # ANNarchy iCub Interface
    import ANN_iCub_Interface.Vocabs as iCub_Constants
    from ANN_iCub_Interface.iCub import Visual_Reader, iCub_Interface

    ######################################################################
    ######################### Init iCub Interface ########################
    print('----- Init ANNarchy-iCub-Interface -----')

    ann_wrapper = iCub_Interface.ANNiCub_wrapper()

    # add visual reader instance
    visread = Visual_Reader.PyVisualReader()

    # init visual reader
    print(visread.init(ann_wrapper, "right_eye", 'r', ini_path="./data"))


    ######################################################################
    ######################## Init ANNarchy network #######################

    print('----- Init ANNarchy network -----')
    neuron = ann.Neuron(
        parameters=
            """
                baseline = 0: int
            """,
        equations=
            """
                r = baseline :int
            """
    )

    vis_pop = ann.Population(geometry=(240, 320, 3), neuron=neuron)
    ann.compile()


    ######################################################################
    ################ Performance test for reading images #################

    duration = np.zeros((test_count,))
    print("----- Start Performance Test -----")
    for i in range(test_count):
        start = timer()
        img = visread.retrieve_robot_eye()
        # vis_pop.baseline = img

        # plt.imshow(np.reshape(img, (240,320,3)))
        # plt.show()

        # ann.simulate(1)
        duration[i] = timer() - start
    print(np.amax(vis_pop.r))

    print("----- Performance Test Finished -----")
    mean_time = round(np.mean(duration)*1000, 2)
    std_time = round(np.std(duration)*1000, 2)
    print("Mean:", mean_time)
    print("STD:", std_time)
    print("Mean FPS:", 1./(mean_time/1000))


    ######################################################################
    ######################## Closing the program: ########################

    print('----- Close visual reader module -----')
    visread.close(ann_wrapper)

    print('Finished Visual Perception test\n')

    return mean_time, std_time


#########################################################
def speed_test_interface_grpc(test_count):
    """
        Test the performance of the visual perception with the ANNarchy-iCub-Interface and an automatic transfer to ANNarchy.

    """

    # ANNarchy iCub Interface
    import ANN_iCub_Interface.Vocabs as iCub_Constants
    from ANN_iCub_Interface import __root_path__ as interface_root
    from ANN_iCub_Interface.ANNarchy_iCub_Populations import VisionPopulation
    from ANN_iCub_Interface.iCub import Visual_Reader, iCub_Interface

    ######################################################################
    ######################### Init iCub Interface ########################
    print('----- Init ANNarchy-iCub-Interface -----')

    iCub = iCub_Interface.ANNiCub_wrapper()

    # init visual reader
    visreader = Visual_Reader.PyVisualReader()
    if not visreader.init_grpc(iCub, "right_eye", 'r', ini_path="./data", ip_address="0.0.0.0", port=50000):
        print("Init failed")
        exit(0)


    ######################################################################
    ######################## Init ANNarchy network #######################
    print('----- Init ANNarchy network -----')

    ann_interface_root = interface_root + "/"

    # Create ANNarchy visual input population
    pop_vis = VisionPopulation(geometry=(240,320), port=50000)

    # Compile network
    # gRPC paths, only needed for local gRPC installation
    grpc_cpp_plugin = subprocess.check_output(["which", "grpc_cpp_plugin"]).strip().decode(sys.stdout.encoding)
    grpc_path = str(Path(grpc_cpp_plugin).resolve().parents[1]) + "/"
    grpc_include_path = grpc_path + "/include"
    grpc_lib_path = grpc_path + "/lib"
    compiler_flags = "-march=native -O2" + " -I"+ann_interface_root+" -Wl,-rpath,"+ann_interface_root+"/ANN_iCub_Interface/grpc/ -I" + grpc_include_path
    extra_libs = "-lprotobuf -lgrpc++ -lgrpc++_reflection -L"+ann_interface_root+"/ANN_iCub_Interface/grpc/ -liCub_ANN_grpc -L" + grpc_lib_path
    ann.compile(directory='annarchy_vreader', compiler_flags=compiler_flags, extra_libs=extra_libs)

    for pop in ann.populations():
        print(pop.ip_address, pop.port)
        print(pop.name, ':', pop.geometry)
        # connect ANNarchy populations via gRPC
        pop.connect()


    ######################################################################
    ################ Performance test for reading images #################

    duration = np.zeros((test_count,))
    print("----- Start Performance Test -----")
    # do something!
    for i in range(test_count):
        start = timer()
        ann.simulate(1)
        duration[i] = timer() -start
        np.amax(pop_vis.r)

    print("----- Performance Test Finished -----")
    mean_time = round(np.mean(duration)*1000, 2)
    std_time = round(np.std(duration)*1000, 2)
    print("Mean", mean_time)
    print("STD", std_time)


    ######################################################################
    ######################## Closing the program: ########################

    print('----- Close visual reader module -----')
    # Close visual reader module
    visreader.close(iCub)

    print('Finished Visual Perception test\n')

    return mean_time, std_time


#########################################################
if __name__ == "__main__":
    perf_test_count = 1000
    folder = "./results/visual"
    Path(folder).mkdir(parents=True, exist_ok=True)

    if len(sys.argv) > 1:
        if sys.argv[1] == "yarp":
            speed_test_yarp_manual(perf_test_count)
        elif sys.argv[1] == "int_manual":
            speed_test_interface_manual(perf_test_count)
        elif sys.argv[1] == "int_auto":
            speed_test_interface_grpc(perf_test_count)
        elif sys.argv[1] == "all":
            yarp_mean, yarp_std = speed_test_yarp_manual(perf_test_count)
            ann.clear()
            intman_mean, intman_std = speed_test_interface_manual(perf_test_count)
            ann.clear()
            intauto_mean, intauto_std = speed_test_interface_grpc(perf_test_count)
            print("Results Performance Test")
            print("YARP: \nMean: {:2.2f} \nSTD:  {:2.2f}".format(yarp_mean, yarp_std))
            print("Interface_manual: \nMean: {:2.2f} \nSTD:  {:2.2f}".format(intman_mean, intman_std))
            print("Interface_auto: \nMean: {:2.2f} \nSTD:  {:2.2f}".format(intauto_mean, intauto_std))

            with open(folder + "/all.txt", "w") as f:
                f.write("Parameter:\n")
                f.write("Count: " + str(perf_test_count) + "\n\n")
                f.write("Results Performance Test")
                f.write("YARP: \nMean: {:2.2f} \nSTD:  {:2.2f}".format(yarp_mean, yarp_std))
                f.write("Interface_manual: \nMean: {:2.2f} \nSTD:  {:2.2f}".format(intman_mean, intman_std))
                f.write("Interface_auto: \nMean: {:2.2f} \nSTD:  {:2.2f}".format(intauto_mean, intauto_std))

        else:
            print("No correct option given! yarp, int_manual, int_auto, all")
    else:
        print("No correct option given! yarp, int_manual, int_auto, all")
