# ANNarchy iCub Interface
This program is an interface between the Neurosimulator ANNarchy and the iCub robot (tested with the iCub simulator and partly with gazebo). It is written in C++ with a Cython wrapping to Python.


## Interface Module level description
Possible actions are the reading and writing of joint angles, get the current state or move the robot joints. Further, the camera images and the tactile sensors data can be received.

The interface consists of different parts. Clustering the different tasks of the interface:

1. ANNarchy_iCub_Populations
    - In the ANNarchy_iCub_Populations submodule the specific input/output ANNarchy populations are defined. This can only be used with gRPC to receive/send the data from/to the iCub modules.

2. iCub
    - This submodule consists on the one hand of the core modules to communicate with the iCub, which are the sensor reader (Skin, Camera, Joint) and the joint writer. The core modules are described in more detail in the following:

        1. *iCubInterface:*<br>
            This is mangement module consists of an abstract main Wrapper and gives the opportunity to load/save the interface modules from/to a given XML-file. 

        2. *JointReader:*<br>
            This module handles the joint reading. The iCub robot is divided in multiple robot parts, which are the head, right arm, left arm, torso right leg and left leg.<br>
            Before the first usage of a joint reader instance, it has to be initialized with some specifications like the robot part. Then the joint angles can be received in two ways. As a double value or in a population code for one, multiple or all joint/s of the associated iCub part.

        3. *JointWriter:*<br>
            The joint writer has a similar structure to the joint reader. They also has to be initialized before usage.<br>
            For the writing of the joint angles the same ways are possible like for the reading. The joint angle can be written as double value or as population code for one, multiple or all joint/s of the associated part.

        4. *VisualReader:*<br>
            This module handles the receiving of the camera images.<br>
            This reader can be initilized for the right ('r') or left ('l') eye, limiting the visual data to be monocular. The grayscaled image is returned as an 1D-vector with a normalization from 0.0 (black) to 1.0 (white).<br>
            In the binocular mode ('b') the images of both cameras images are received and seperately added as 1D-vectors to the image buffer.

        5. *SkinReader:*<br>
            This module handles the tactile data from the iCub's artificial skin. The robot is at several parts equipped with skin modules, reacting to pressure.<br>
            The sensor data for the arms can be read out with this module. The skin of the iCub arm is seperated in three modules, being the arm, forearm and hand.<br>
            The tactile data is returned as a vector with doubles in a range of 0.0 to 1.0. Where 0. is no pressure and 1.0 is the maximum sensor response.

        6. *KinematicReader:*<br>
            This module handles the iCub forward kinematic to receive the cartesian coordinates for specific joints or end-effectors like the hand. This module could be used online, retrieving the joint angles from the running iCub or offline with given joint angles.

        7. *KinematicWriter:*<br>
            This module handles the iCub inverse kinematics.

3. Sync
    - The Sync module provide two classes MasterClock and ClockInterface. Thereby, the MasterClock is the main synchronization handler and for the use exactly one instance of it is needed to create. To synchronize the ANNarchy and iCub simulations, for each side one derived class of the ClockInterface has to be created. This class provide two abstract functions, which has to be impleemnted. The first is the update method and the second is sync_input. These method are executed once for update step. The timing can be individually be set and is dependent on the usecase.<br>
    At this time this synchronization mechanism should only be used with the iCub in simulation.

4. Vocabs
    - The Vocabs module provide several useful constants like the iCub part strings or a mapping from the joint names to the joint indices in the respective part.


## Installation
Make sure YARP is installed before installing the interface. An installation guide for YARP/iCub can be found in the github [superbuild repository](https://github.com/robotology/robotology-superbuild) of the YARP/iCub universe.

### Default Installation
Then the interface can be installed with pip by executing the following line in a terminal in the interface directory.

```bash
pip3 install .
```

In case of missing/false include directories the make_config.py file has to be modified.<br>

### Enable Low-Level gRPC communication
The interface is build in a default configuration. In this case the gRPC communication with ANNarchy is disabled. To enable this part, set the use_grpc parameter in make_config.py to True. This part depends on the gRPC package and the protobuf compiler.
The system packages are recommended especially for recent Linux versions (>Ubuntu 18.XX). Install the following apt packages: protobuf-compiler-grpc, libgrpc++-dev
```bash
    sudo apt install protobuf-compiler-grpc libgrpc++-dev
```
For the source installation of gRPC ([installation from the repository](https://grpc.io/docs/languages/cpp/quickstart/#install-grpc) with cmake or bazel) you need to take of other packages, using protobuf like gazebo to handle the needed versions. Since this can lead to a lot of trouble, the use of the system packages is recommended.


## useful links
Wiki for the iCub robot:<br>
<http://wiki.icub.org/wiki/Manual>

YARP website:<br>
<http://www.yarp.it/git-master/index.html>

git repository with helpful documents and scripts for the work with iCub:<br>
<https://ai.informatik.tu-chemnitz.de/gogs/iCub_TUC/iCub_simulator_tools.git>


## Authors
Torsten Fietzek (<torsten.fietzek@informatik.tu-chemnitz.de>)<br>
Helge Ülo Dinkelbach (<helge.dinkelbach@gmail.com>)<br>


## Publications
Fietzek, T., Dinkelbach, H. Ü., & Hamker, F. H. (2022). ANNarchy - iCub: An Interface for Easy Interaction between Neural Network Models and the iCub Robot. 2022 IEEE 9th International Conference on Computational Intelligence and Virtual Environments for Measurement Systems and Applications (CIVEMSA), 1–6. <https://doi.org/10.1109/CIVEMSA53371.2022.9853699>


## Dependencies
g++     >= 6.1
Python  >= 3.5<br>
YARP    >= 3.2<br>
OpenCV  >= 3.4<br>
numpy  <br>
(Optional) <br>
gRPC >= <br>
