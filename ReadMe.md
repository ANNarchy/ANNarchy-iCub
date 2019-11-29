This program is an interface between the Neurosimulator ANNarchy and the iCub robot (tested with the iCub simulator). It is written in C++ with an Cython wrapping to Python.


## Interface description
Possible actions are the reading and writing of joint angles get the current sate or move the robot joints. Further, the cameras and the tactile sensors data can be received.

The interface has a modular structure with a main struct and several subclasses.
The main struct is the "iCubANN" struct, handling the subclass instances. The subcalss and also the different mudles are JointReader, JointWriter, VisualReader and SkinReader with the following functionalities:

JointReader:
    This module handles the joint reading. The iCub robot is divided in multiple robot parts, which are the head, right arm, left arm, torso right leg and left leg. For each of this part a seperate joint reader instance is needed. Therefore, one has to add as much as one need to the iCubANN struct with the "AddJointReader" method. Before the first usage of the joint reader, it must be initialized with some specifications like the robot part. Then the joint angles can be received in two ways, directly as a double value for a single joint or in a population code for one joint or for all joints of the associated iCub part. 

JointWriter:
    The joint writer has a similar structure to the joint reader. Like there for each iCub part a separate instance has to be added to the iCubANN struct. They must also be initialized before usage. For the writing of the joint angles the same ways are possible like for the reading. The joint angle can be written as a double for one joint or as a population code for one joint or for all joints of the associated part. 

VisualReader:
    This module handles the receiving of the camera images. At this time only one visual reader instance is possible due to YARP limitations for the used YARP RFModule (run only one Module). This reader can be initilized for the right or left eye, limiting the visual data to be monocular. The grayscaled image is returned as an onedimensional vector with a normalization from 0.0 (black) to 1.0 (white).

SkinReader:
    This module handles the tactile data from the iCub's artificial skin. The robot is at several parts equipped with skin modules, reacting to pressure. The sensor data for the arm can be read out with this module. The skin of the iCubs arm is seperated in three modules, being the arm, forearm and hand. The tactile data is returned as a vector with doubles in a range of 0.0 to 1.0. Here 0. iss no pressure and 1.0 is the maximum sensor response.


## Folder structure
Interface_ANNarchy_iCub -> Main folder containing the whole interface
    - include -> This folder contains the header files for the interface modules.
        - INI_Reader -> The INI-Reader is an external module, which is used to handle ini-files.
    - src -> This folder contains the source files for the interface modules.
    - data -> Folder capsulate the data files used by the interface.
        - sensor_positions -> This folder caontains the files from the iCub simulator installation with the position data for the tactile sensors.
        joint_limits.ini -> In the ini file the joint limitations for the iCub are given. 
                            !!! This should be checked before the usage with the real robot, to avoid damage. !!!

    iCubCPP.pyx -> This is the Cython file to wrap the C++ code for the usage in Python.


## useful links
Wiki for the iCub robot:
http://wiki.icub.org/wiki/Manual

YARP website:
http://www.yarp.it/index.html

git repository with scripts to control the iCub simulator:
https://ai.informatik.tu-chemnitz.de/gogs/torsten/iCub_simulator_tools.git


## Authors
Torsten Follak

## Dependencies
Python  >= 3.5
YARP    >= 3.2
OpenCV  >= 3.4