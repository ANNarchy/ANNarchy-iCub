"""
Created on Mon Apr 28 2020

@author: Torsten Fietzek

joint position control example

"""

######################################################################
########################## Import modules  ###########################
######################################################################

import os
import sys
import subprocess
import time
from pathlib import Path
from timeit import default_timer as timer

import ANNarchy as ann
import numpy as np
import yarp

home_arm_pos = np.load("./data/test_pos_home.npy")
pos_perf_test_all = np.load("./data/pos_perf_test_all.npy")


# position control with yarp commands
def speed_test_yarp_manual(testcount, joint, speed):
    print("\n----- Python YARP performance test -----")
    print("Speed:", speed)

    import yarp

    ROBOT_PREFIX = "icubSim"
    CLIENT_PREFIX = "client"

    ######################################################################
    ######################## Init ANNarchy network #######################

    print('----- Init ANNarchy network -----')
    neuron = ann.Neuron(
        parameters=
            """
                baseline = 0.
            """,
        equations=
            """
                r = baseline
            """
    )

    joint_ctrl_pop_all = ann.Population(geometry=(7,), neuron=neuron)
    joint_ctrl_pop_single = ann.Population(geometry=(1,), neuron=neuron)
    ann.compile()

    ######################################################################
    ######################### Init YARP network ##########################
    yarp.Network.init()
    if not yarp.Network.checkNetwork():
        sys.exit('[ERROR] Please try running yarp server')

    ######################################################################
    ################ Init motor control for the right_arm ################
    print('----- Init right_arm motor control -----')

    props = yarp.Property()
    props.put("device", "remote_controlboard")
    props.put("local", "/" + CLIENT_PREFIX + "/right_arm")
    props.put("remote", "/" + ROBOT_PREFIX + "/right_arm")

    # create remote driver
    Driver_right_arm = yarp.PolyDriver(props)

    if not Driver_right_arm:
        sys.exit("Motor initialization failed!")

    # query motor control interfaces
    iPos_right_arm = Driver_right_arm.viewIPositionControl()
    iEnc_right_arm = Driver_right_arm.viewIEncoders()

    # set joint speed
    speed_y = yarp.Vector(pos_perf_test_all.shape[0])
    for i in range(pos_perf_test_all.shape[0]):
        speed_y.set(i, speed)
    iPos_right_arm.setRefSpeeds(speed_y.data())

    # retrieve number of joints
    jnts_right_arm = iPos_right_arm.getAxes()

    home_pos = yarp.Vector(jnts_right_arm)
    read = iEnc_right_arm.getEncoders(home_pos.data())
    while not read:
        time.sleep(0.01)
        read = iEnc_right_arm.getEncoders(home_pos.data())

    home_arm_pos_Y = yarp.Vector(home_arm_pos.shape[0])
    for i in range(jnts_right_arm):
        home_arm_pos_Y.set(i, home_arm_pos[i])

    pos_perf_test_all_Y = yarp.Vector(pos_perf_test_all.shape[0])
    for i in range(pos_perf_test_all.shape[0]):
        pos_perf_test_all_Y.set(i, pos_perf_test_all[i])


    ######################################################################
    ################ Move the right arm to start position ################
    print('----- Move arm to start position -----')
    motion = not (iPos_right_arm.positionMove(home_arm_pos_Y.data()))
    yarp.delay(0.01)
    # for blocking while moving the joints
    while not motion:
        motion = iPos_right_arm.checkMotionDone()


    ######################################################################
    ###################### Performance test full arm #####################
    print('----- Start performance test full arm -----')
    duration_full = np.zeros((testcount,))
    pos_perf_Y = yarp.Vector(pos_perf_test_all.shape[0])
    for i in range(7, pos_perf_test_all.shape[0]):
        pos_perf_Y.set(i, pos_perf_test_all[i])

    print("Simulate")
    for i in range(testcount):
        motion = not (iPos_right_arm.positionMove(home_arm_pos_Y.data()))
        yarp.delay(0.01)
        # for blocking while moving the joints
        while not motion:
            motion = iPos_right_arm.checkMotionDone()
        joint_ctrl_pop_all.baseline = pos_perf_test_all[0:7]
        ann.simulate(1)

        start = timer()
        r_ann = joint_ctrl_pop_all.r
        for j in range(r_ann.shape[0]):
            pos_perf_Y.set(j, r_ann[j])
        motion = not (iPos_right_arm.positionMove(pos_perf_Y.data()))
        while not motion:
            motion = iPos_right_arm.checkMotionDone()
        duration_full[i] = timer() - start
    print("Simulated")

    mean_time_full = round(np.mean(duration_full)*1000, 2)
    std_time_full = round(np.std(duration_full)*1000, 2)
    print("Mean", mean_time_full)
    print("STD", std_time_full)


    ######################################################################
    #################### Performance test single joint ###################
    print('----- Start performance test single joint -----')
    duration_single = np.zeros((testcount,))

    print("Simulate")
    for i in range(testcount):
        motion = not (iPos_right_arm.positionMove(home_arm_pos_Y.data()))
        yarp.delay(0.01)
        # for blocking while moving the joints
        while not motion:
            motion = iPos_right_arm.checkMotionDone()
        joint_ctrl_pop_single.baseline = pos_perf_test_all[joint]
        ann.simulate(1)

        start = timer()
        motion = not (iPos_right_arm.positionMove(joint, joint_ctrl_pop_single.r[0]))
        while not motion:
            motion = iPos_right_arm.checkMotionDone()
        duration_single[i] = timer() - start
    print("Simulated")

    mean_time_single = round(np.mean(duration_single)*1000, 2)
    std_time_single = round(np.std(duration_single)*1000, 2)
    print("Mean", mean_time_full)
    print("STD", std_time_full)


    ######################################################################
    ################### Close network and motor cotrol ###################
    print('----- Close control devices and opened ports -----')
    Driver_right_arm.close()
    yarp.Network.fini()
    ann.clear()

    return (mean_time_full, mean_time_single), (std_time_full, std_time_single)

# position control with ANNarchy-iCub-Interface -> manual transfer
def speed_test_interface_manual(testcount, joint, speed):
    print("\n----- Interface with manual transport performance test -----")
    print("Speed:", speed)

    import ANN_iCub_Interface.iCub as iCub_mod
    import ANN_iCub_Interface.Vocabs as iCub_const

    ######################################################################
    ######################## Init ANNarchy network #######################

    print('----- Init ANNarchy network -----')
    neuron = ann.Neuron(
        parameters=
            """
                baseline = 0.
            """,
        equations=
            """
                r = baseline
            """
    )

    joint_ctrl_pop_all = ann.Population(geometry=(7,), neuron=neuron)
    joint_ctrl_pop_single = ann.Population(geometry=(1,), neuron=neuron)
    ann.compile()

    ######################################################################
    ######################### Init iCub Interface ########################
    print('----- Init ANNarchy-iCub-Interface -----')

    # top module
    iCub = iCub_mod.iCub_Interface.ANNiCub_wrapper()

    # Reader/Writer instances
    reader = iCub_mod.Joint_Reader.PyJointReader()
    writer = iCub_mod.Joint_Writer.PyJointWriter()

    # initialization
    init = True
    init = init & reader.init(iCub, "read_right_arm", iCub_const.PART_KEY_RIGHT_ARM, 0.5, 15, ini_path="./data")
    init = init & writer.init(iCub, "write_right_arm", iCub_const.PART_KEY_RIGHT_ARM, 0.5, 15, speed=speed, ini_path="./data")

    if not init:
        sys.exit("interface initialization failed!")

    home_pos = reader.read_double_all()

    ######################################################################
    ###################### Performance test full arm #####################
    print('----- Start performance test full arm -----')
    duration_full = np.zeros((testcount,))

    print("Simulate")
    for i in range(testcount):
        writer.write_double_all(home_arm_pos, mode="abs", blocking=True)
        joint_ctrl_pop_all.baseline = pos_perf_test_all[0:7]
        ann.simulate(1)

        start = timer()
        writer.write_double_multiple(joint_ctrl_pop_all.r, np.arange(0, 7), mode="abs", blocking=True)
        duration_full[i] = timer() - start
    print("Simulated")

    mean_time_full = round(np.mean(duration_full)*1000, 2)
    std_time_full = round(np.std(duration_full)*1000, 2)
    print("Mean", mean_time_full)
    print("STD", std_time_full)


    ######################################################################
    #################### Performance test single joint ###################
    print('----- Start performance test single joint -----')
    duration_single = np.zeros((testcount,))

    print("Simulate")
    for i in range(testcount):
        writer.write_double_all(home_arm_pos, mode="abs", blocking=True)
        joint_ctrl_pop_single.baseline = pos_perf_test_all[joint]
        ann.simulate(1)

        start = timer()
        writer.write_double_one(joint_ctrl_pop_single.r, joint, mode="abs", blocking=True)
        duration_single[i] = timer() - start
    print("Simulated")

    mean_time_single = round(np.mean(duration_single)*1000, 2)
    std_time_single = round(np.std(duration_single)*1000, 2)
    print("Mean", mean_time_full)
    print("STD", std_time_full)

    ######################################################################
    ################### Close network and motor cotrol ###################
    print('----- Clear Interface -----')
    iCub.clear()
    ann.clear()

    return (mean_time_full, mean_time_single), (std_time_full, std_time_single)

# position control with ANNarchy-iCub-Interface -> gRPC-based transfer
def speed_test_interface_grpc(testcount, joint, speed):
    print("\n----- Interface with gRPC transport performance test -----")
    print("Speed:", speed)
    # ANNarchy iCub interface
    import ANN_iCub_Interface.Vocabs as iCub_const
    from ANN_iCub_Interface import __root_path__ as ann_interface_root
    from ANN_iCub_Interface.ANNarchy_iCub_Populations import JointControl
    from ANN_iCub_Interface.iCub import (Joint_Reader, Joint_Writer,
                                         iCub_Interface)

    ######################################################################
    ######################## Init ANNarchy network #######################

    print('----- Init ANNarchy network -----')
    neuron = ann.Neuron(
        parameters=
            """
                baseline = 0.
            """,
        equations=
            """
                r = baseline
            """
    )

    joint_ctrl_pop_all = JointControl(geometry=(7,), neuron=neuron, ip_address="0.0.0.0", port=50005)
    joint_ctrl_pop_single = JointControl(geometry=(1,), neuron=neuron, ip_address="0.0.0.0", port=50006)

    # Compile network
    # gRPC paths, only needed for local gRPC installation
    grpc_cpp_plugin = subprocess.check_output(["which", "grpc_cpp_plugin"]).strip().decode(sys.stdout.encoding)
    grpc_path = str(Path(grpc_cpp_plugin).resolve().parents[1]) + "/"
    grpc_include_path = grpc_path + "/include"
    grpc_lib_path = grpc_path + "/lib"
    compiler_flags = "-march=native -O2" + " -I"+ann_interface_root+" -Wl,-rpath,"+ann_interface_root+"/ANN_iCub_Interface/grpc/ -I" + grpc_include_path
    extra_libs = "-lprotobuf -lgrpc++ -lgrpc++_reflection -L"+ann_interface_root+"/ANN_iCub_Interface/grpc/ -liCub_ANN_grpc -L" + grpc_lib_path
    ann.compile(directory='annarchy_jwriter', compiler_flags=compiler_flags, extra_libs=extra_libs)

    for pop in ann.populations():
        try:
            pop.connect()
        except:
            pass


    ######################################################################
    ######################### Init iCub Interface ########################
    print('----- Init ANNarchy-iCub-Interface -----')

    # top module
    iCub = iCub_Interface.ANNiCub_wrapper()

    # Reader/Writer instances
    reader = Joint_Reader.PyJointReader()
    writer = Joint_Writer.PyJointWriter()

    # initialization
    init = True
    init = init & reader.init(iCub, "read_right_arm", iCub_const.PART_KEY_RIGHT_ARM, 0.5, 15, ini_path="./data")
    init = init & writer.init_grpc(iCub, "write_right_arm", iCub_const.PART_KEY_RIGHT_ARM, 15, joints=np.arange(0, 7), mode="abs", blocking=True, degr_per_neuron=0.5, speed=speed, ini_path="./data", port=joint_ctrl_pop_all.port)

    if not init:
        sys.exit("interface initialization failed!")

    home_pos = reader.read_double_all()

    ######################################################################
    ###################### Performance test full arm #####################
    print('----- Start performance test full arm -----')
    duration_full = np.zeros((testcount,))

    print("Simulate")
    for i in range(testcount):
        writer.write_double_all(home_arm_pos, mode="abs", blocking=True)
        joint_ctrl_pop_all.baseline = pos_perf_test_all[0:7]
        ann.simulate(1)

        start = timer()
        writer.retrieve_ANNarchy_input_multi()
        writer.write_ANNarchy_input_multi()
        duration_full[i] = timer() - start
    print("Simulated")

    mean_time_full = round(np.mean(duration_full)*1000, 2)
    std_time_full = round(np.std(duration_full)*1000, 2)
    print("Mean", mean_time_full)
    print("STD", std_time_full)

    ######################################################################
    ######################### Init iCub Interface ########################
    print('----- Reinit ANNarchy-iCub-Interface Jwriter for single joint conection -----')

    # initialization
    writer.close(iCub)
    init = writer.init_grpc(iCub, "write_right_arm", iCub_const.PART_KEY_RIGHT_ARM, 15, joints=[3,], mode="abs", blocking=True, degr_per_neuron=0.5, speed=speed, ini_path="./data", port=joint_ctrl_pop_single.port)

    if not init:
        sys.exit("interface initialization failed!")

    ######################################################################
    #################### Performance test single joint ###################
    print('----- Start performance test single joint -----')
    duration_single = np.zeros((testcount,))

    print("Simulate")
    for i in range(testcount):
        writer.write_double_all(home_arm_pos, mode="abs", blocking=True)
        joint_ctrl_pop_single.baseline = pos_perf_test_all[joint]
        ann.simulate(1)

        start = timer()
        writer.retrieve_ANNarchy_input_single()
        writer.write_ANNarchy_input_single()
        duration_single[i] = timer() - start
    print("Simulated")

    mean_time_single = round(np.mean(duration_single)*1000, 2)
    std_time_single = round(np.std(duration_single)*1000, 2)
    print("Mean", mean_time_full)
    print("STD", std_time_full)

    ######################################################################
    ################### Close network and motor cotrol ###################
    print('----- Clear Interface -----')
    iCub.clear()
    ann.clear()

    return (mean_time_full, mean_time_single), (std_time_full, std_time_single)


#########################################################
if __name__ == "__main__":
    perf_test_count = 5
    joint_sel = 3
    speed = 100
    folder = "./results/motion"
    Path(folder).mkdir(parents=True, exist_ok=True)

    if len(sys.argv) > 1:
        if sys.argv[1] == "yarp":
            if len(sys.argv) == 3:
                speed = float(sys.argv[2])
            speed_test_yarp_manual(perf_test_count, joint_sel, speed)
        elif sys.argv[1] == "int_manual":
            if len(sys.argv) == 3:
                speed = float(sys.argv[2])
            speed_test_interface_manual(perf_test_count, joint_sel, speed)
        elif sys.argv[1] == "int_auto":
            if len(sys.argv) == 3:
                speed = float(sys.argv[2])
            speed_test_interface_grpc(perf_test_count, joint_sel, speed)
        elif sys.argv[1] == "all":
            if len(sys.argv) == 3:
                speed = float(sys.argv[2])
            yarp_mean, yarp_std = speed_test_yarp_manual(perf_test_count, joint_sel, speed)
            ann.clear()
            intman_mean, intman_std = speed_test_interface_manual(perf_test_count, joint_sel, speed)
            ann.clear()
            intauto_mean, intauto_std = speed_test_interface_grpc(perf_test_count, joint_sel, speed)
            print("Results Performance Test")
            print("YARP:")
            print("All Joints: \nMean: {:2.2f} \nSTD:  {:2.2f}".format(yarp_mean[0], yarp_std[0]))
            print("Single Joint: \nMean: {:2.2f} \nSTD:  {:2.2f}".format(yarp_mean[1], yarp_std[1]))

            print("\nInterface_manual:")
            print("All Joints: \nMean: {:2.2f} \nSTD:  {:2.2f}".format(intman_mean[0], intman_std[0]))
            print("Single Joint: \nMean: {:2.2f} \nSTD:  {:2.2f}".format(intman_mean[1], intman_std[1]))

            print("\nInterface_auto:")
            print("All Joints: \nMean: {:2.2f} \nSTD:  {:2.2f}".format(intauto_mean[0], intauto_std[0]))
            print("Single Joint: \nMean: {:2.2f} \nSTD:  {:2.2f}".format(intauto_mean[1], intauto_std[1]))

            with open(folder + "/all_speed_" + str(speed) + ".txt", "w") as f:
                f.write("Parameter:\n")
                f.write("Count: " + str(perf_test_count) + "\n")
                f.write("joint_select: " + str(joint_sel) + "\n")
                f.write("Speed: " + str(speed) + "\n\n")

                f.write("Results Performance Test\n")
                f.write("YARP:\n")
                f.write("All Joints: \nMean: {:2.2f} \nSTD:  {:2.2f}\n".format(yarp_mean[0], yarp_std[0]))
                f.write("Single Joint: \nMean: {:2.2f} \nSTD:  {:2.2f}\n".format(yarp_mean[1], yarp_std[1]))

                f.write("\nInterface_manual:\n")
                f.write("All Joints: \nMean: {:2.2f} \nSTD:  {:2.2f}\n".format(intman_mean[0], intman_std[0]))
                f.write("Single Joint: \nMean: {:2.2f} \nSTD:  {:2.2f}\n".format(intman_mean[1], intman_std[1]))

                f.write("\nInterface_auto:\n")
                f.write("All Joints: \nMean: {:2.2f} \nSTD:  {:2.2f}\n".format(intauto_mean[0], intauto_std[0]))
                f.write("Single Joint: \nMean: {:2.2f} \nSTD:  {:2.2f}\n".format(intauto_mean[1], intauto_std[1]))

        else:
            print("No correct option given! yarp, int_manual, int_auto, all")
    else:
        print("No correct option given! yarp, int_manual, int_auto, all")
