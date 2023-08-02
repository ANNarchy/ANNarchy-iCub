"""
Created on 2023-07-31 17:41:44

@author: Torsten Fietzek

example for joint forward kinematic

"""

import sys

import ANNarchy as ann
import example_parameter as params
import iCub_Python_Lib.iCub_transformation_matrices as iTransform
import matplotlib.pyplot as plt
import numpy as np

import ANN_iCub_Interface.Vocabs as iCub_const
from ANN_iCub_Interface import __ann_compile_args__, __ann_extra_libs__
from ANN_iCub_Interface.ANNarchy_iCub_Populations import KinematicForward
from ANN_iCub_Interface.iCub import Joint_Reader, Joint_Writer, Kinematic_Reader, iCub_Interface


######################################################################
# Example implementation using the ANNarchy-iCub-Interface
def forward_kin_ANN_iCub_Interface():
    print("Example for iCub forward kinematic.")

    ######################################################################
    # Add interface instances

    # Interface main wrapper, is needed once
    iCub = iCub_Interface.ANNiCub_wrapper()

    # Add kinematic reader instance
    kinreader = Kinematic_Reader.PyKinematicReader()

    # Init kinematic reader
    print('Init kinematic reader')
    if not kinreader.init(iCub, "fkin", part=iCub_const.PART_KEY_RIGHT_ARM, version=2, ini_path=params.INTERFACE_INI_PATH, offline_mode=params.offline):
        sys.exit("Initialization failed")

    ######################################################################
    # Perform forward kinematic

    if params.offline:
        kinreader.block_links([0, 1, 2])
        joint_angles = np.deg2rad(np.array([15., 16., 0., 70., -90., 0., 0.]))
        kinreader.set_jointangles(joint_angles)

    print("DOF:", kinreader.get_DOF())

    # print end-effector position
    end_eff_pos = kinreader.get_handposition()
    print("End-Effector", end_eff_pos)  # (robot reference frame)
    print("End-Effector", iTransform.transform_position(end_eff_pos, params.Transfermat_robot2world))  # (simulator reference frame)

    # print position for specific joint of the kinematic chain
    joint3_pos = kinreader.get_jointposition(3)
    print("Joint 3", joint3_pos)    # (robot reference frame)
    print("Joint 3", iTransform.transform_position(joint3_pos, params.Transfermat_robot2world))    # (simulator reference frame)

    # Close kinematic reader module
    kinreader.close(iCub)

    ######################################################################
    # Close interface instances
    print('----- Close interface instances -----')
    iCub.clear()


######################################################################
# Example implementation using the ANNarchy-iCub-Interface with gRPC and ANNarchy
def forward_kin_ANN_iCub_Interface_grpc():
    print("Example for iCub forward kinematic with direct connection to ANNarchy.")

    ######################################################################
    # Set up ANNarchy network

    # Create ANNarchy kinematic input population
    pop_kin = KinematicForward(geometry=(3,), ip_address=params.ip_address)

    mon_kin = ann.Monitor(pop_kin, ["r"])

    print("Compile ANNarchy network.")
    ann.compile(directory='./annarchy/annarchy_forward_kin', compiler_flags=__ann_compile_args__, extra_libs=__ann_extra_libs__)

    print("Populations")
    for pop in ann.populations():
        print(pop.name, ':', pop.geometry)
        try:
            print(pop.ip_address, pop.port)
            # connect ANNarchy populations to gRPC-socket
            pop.connect()
        except Exception:
            pass

    ######################################################################
    # Set up ANNarchy-iCub-Interface instances

    # Interface main wrapper, is needed once
    iCub = iCub_Interface.ANNiCub_wrapper()

    # Kinematic Reader with connection to ANNarchy
    kinreader = Kinematic_Reader.PyKinematicReader()
    if not kinreader.init_grpc(iCub, "fkin", part=iCub_const.PART_KEY_RIGHT_ARM, version=2, ini_path=params.INTERFACE_INI_PATH, ip_address=params.ip_address, port=pop_kin.port):
        sys.exit("Initialization failed!")

    # Joint Writer for motion arm motion
    writer = Joint_Writer.PyJointWriter()
    if not writer.init(iCub, "write_arm", iCub_const.PART_KEY_RIGHT_ARM, n_pop=10, ini_path=params.INTERFACE_INI_PATH):
        sys.exit("Initialization failed!")

    # Joint Reader to read out reset position
    joint_reader = Joint_Reader.PyJointReader()
    if not joint_reader.init(iCub, "name", iCub_const.PART_KEY_RIGHT_ARM, sigma=1., n_pop=10, ini_path=params.INTERFACE_INI_PATH):
        sys.exit("Initialization failed!")

    ######################################################################
    # Move the arm and record the hand position

    # Save reset position
    start_pos_head = joint_reader.read_double_all()

    for i in range(params.steps_kin):
        if i % 10 == 0:
            print("Step:", i)
            print("Current hand position", pop_kin.r)

        ann.step()

        # Move iCub arm
        writer.write_double_multiple([0.5, -1.5, np.sin(np.deg2rad(i))-3.], [1, 2, 3], mode="rel")

    ######################################################################
    # Retrieve data from ANNarchy and plot the hand trajectory

    data_kin = mon_kin.get("r")

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_title("Hand trajectory in robot ref. frame")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    ax.plot(data_kin[:, 0], data_kin[:, 1], data_kin[:, 2])
    plt.show()

    ######################################################################
    # Clean-up

    # Return to reset position
    print("Reset position")
    writer.write_double_all(start_pos_head, mode="abs")

    # Clean-up all interface instances
    iCub.clear()


if __name__ == '__main__':
    if params.use_grpc:
        forward_kin_ANN_iCub_Interface_grpc()
    else:
        forward_kin_ANN_iCub_Interface()
