## ANNarchy iCub Interface
This program is an interface between the Neurosimulator ANNarchy and the iCub robot (tested with the iCub simulator and partly with gazebo). It is written in C++ with a Cython wrapping to Python.


## Interface Module level description
Possible actions are the reading and writing of joint angles, get the current state or move the robot joints. Further, the camera images and the tactile sensors data can be received.

The interface consists of different parts. Clustering the different tasks of the interface:

1. ANNarchy_iCub_Populations
    - In the ANNarchy_iCub_Populations submodule the specific input/output ANNarchy populations are defined. This can only be used with gRPC to receive/send the data from/to the iCub modules.

2. iCub
    - This submodule consists on the one hand of the core modules to communicate with the iCub, which are the sensor reader (Skin, Camera, Joint) and the joint writer. On the other hand a more abstract Wrapper is given, which gives the opportunity to initialize the interface module with a given XML-file. The core modules are described in more detail in the following:
        1. *JointReader:*<br>
            This module handles the joint reading. The iCub robot is divided in multiple robot parts, which are the head, right arm, left arm, torso right leg and left leg.<br>
            Before the first usage of a joint reader instance, it has to be initialized with some specifications like the robot part. Then the joint angles can be received in two ways. As a double value or in a population code for one, multiple or all joint/s of the associated iCub part.

        2. *JointWriter:*<br>
            The joint writer has a similar structure to the joint reader. They also has to be initialized before usage.<br>
            For the writing of the joint angles the same ways are possible like for the reading. The joint angle can be written as double value or as population code for one, multiple or all joint/s of the associated part.

        3. *VisualReader:*<br>
            This module handles the receiving of the camera images.<br>
            This reader can be initilized for the right ('r') or left ('l') eye, limiting the visual data to be monocular. The grayscaled image is returned as an 1D-vector with a normalization from 0.0 (black) to 1.0 (white).<br>
            In the binocular mode ('b') the images of both cameras images are received and seperately added as 1D-vectors to the image buffer.

        4. *SkinReader:*<br>
            This module handles the tactile data from the iCub's artificial skin. The robot is at several parts equipped with skin modules, reacting to pressure.<br>
            The sensor data for the arms can be read out with this module. The skin of the iCub arm is seperated in three modules, being the arm, forearm and hand.<br>
            The tactile data is returned as a vector with doubles in a range of 0.0 to 1.0. Where 0. is no pressure and 1.0 is the maximum sensor response.

        5. *KinematicReader:*<br>
            This module handles the iCub forward kinematic to receive the cartesian coordinates for specific joints or endeffectors like the hand.

        6. *KinematicWriter:*<br>
            This module handles the iCub inverse kinematics.


3. Sync
    - The Sync module provide two classes MasterClock and ClockInterface. Thereby, the MasterClock is the main synchronization handler and for the use exactly one instance of it is needed to create. To synchronize the ANNarchy and iCub simulations, for each side one derived class of the ClockInterface ahs to be created. This class provide two abstract functions, which has to be impleemnted. The first is the update method and the second is sync_input. These method are executed once for update step. The timing can be individually be set and is dependent on the usecase.<br>
    At this time this synchronization mechanism should only be used with the iCub in simulation.

4. Vocabs
    - The Vocabs module provide several useful constants like the iCub part strings or a mapping from the joint names to the joint indices in the respective part.


## Folder structure

- Interface_ANNarchy_iCub -> Main folder containing the whole interface
    - Interface_ANN_iCub
        - ANNarchy_iCub_Populations -> ANNarchy population source files for the iCub input/output populations
        - grpc-> gRPC communication source files
        - iCub -> Contains the Cython files (pyx, pxd) for wrapping the C++ code for the use in Python (iCub interaction modules)
        - Sync -> Classes used for synchronized execution of iCub interaction, ANNarchy simulation and further modules
        - include -> This folder contains the C++ header files for the interface modules.
            - INI_Reader -> The INI-Reader is an external module, which is used to handle ini-files.
        - src -> This folder contains the C++ source files for the interface modules.
    - data -> Folder capsulate the data files used by the interface.
        - sensor_positions -> This folder caontains the files from the iCub simulator installation with the position data for the tactile sensors.
        - interface_param.ini -> ini-file with several parameters for the interface
    - doc -> This folder contains the doxygen files for generating the documentaion
    - Testfiles -> files for interface testing
    - Examples -> Interface implementation examples


## Installation
Make sure YARP is insalled before installing the interface. An installation guide for YARP/iCub can be found in [iCub_simulator_tools](https://ai.informatik.tu-chemnitz.de/gogs/iCub_TUC/iCub_simulator_tools.git) or direct in the github [superbuild repository](https://github.com/robotology/robotology-superbuild) of the YARP/iCub universe.

Then the interface can be installed with pip by executing the following line in a terminal in the interface directory.

```bash
pip3 install . --use-feature=in-tree-build
```

In case of missing/false include directories the make_config.py file has to be modified.
The interface is build in a default configuration. In this case the gRPC communication with ANNarchy is disabled. To enable this part, set the use_grpc parameter in make_config.py to True. This part depends on the gRPC package and a protobuf compiler.
The system packages should only be used at recent Linux versions. Recommended is the [installation from the repository](https://grpc.io/docs/languages/cpp/quickstart/#install-grpc) with cmake/bazel.


## Generic Python Examples
Take a look in the testfiles for a specific implementation. More examples will follow.

### Non gRPC version

```Python
from ANN_iCub_Interface.iCub import Joint_Reader, Joint_Writer, iCub_Interface, Visual_Reader, Skin_Reader, Kinematic_Reader
import ANN_iCub_Interface.Vocabs as iCub_Constants


iCub = iCub_Interface.ANNiCub_wrapper()
...
# add necessary instances
jreader = Joint_Reader.PyJointReader()
jwriter = Joint_Writer.PyJointWriter()
sreader = Skin_Reader.PySkinReader()
visreader = Visual_Reader.PyVisualReader()
kinreader = Kinematic_Reader.PyKinematicReader()
...

# init modules (necessary for all modules before usage)
jreader.init(iCub, name , ...)
jwriter.init(iCub, name , ...)
sreader.init(iCub, name , ...)
visreader.init(iCub, name, ...)
kinreader.(iCub, name, ...)
...

# use interface modules
jreader.method_name(...)
jwriter.method_name(...)
sreader.method_name(...)
visreader.method_name(...)
kinreader.method_name(...)
...
...

# Close modules
jreader.close(iCub)
jwriter.close(iCub)
sreader.close(iCub)
visreader.close(iCub)
kinreader.close(iCub)
```

### gRPC version

```Python
from ANN_iCub_Interface import __root_path__ as interface_root
from ANN_iCub_Interface.iCub import Joint_Reader, Joint_Writer, iCub_Interface, Visual_Reader, Skin_Reader, Kinematic_Reader
from ANN_iCub_Interface.ANNarchy_Populations import JointReadout, JointControl, SkinPopulation, VisionPopulation, KinematicPopulation
import ANN_iCub_Interface.Vocabs as iCub_Constants

# Create ANNarchy populations e.g. VisionPopulation
pop_vis = VisionPopulation( geometry = (240,320) )
...

# Create the rest of ANNarchy network
...

# Compile ANNarchy network
ann_interface_root = interface_root + "/"
compile(directory='results/annarchy_vreader', compiler_flags="-I"+ann_interface_root+" -Wl,-rpath,"+ann_interface_root+"/ANN_iCub_Interface/grpc/", extra_libs="-lprotobuf -lgrpc++ -lgrpc++_reflection -L"+ann_interface_root+"ANN_iCub_Interface/grpc/ -liCub_ANN_grpc")

# Connect ANNarchy interface populations to gRPC service
pop_vis.connect()
...

# Instanciate main iCub wrapper
iCub = iCub_Interface.ANNiCub_wrapper()

# Add necessary module instances
visreader = Visual_Reader.PyVisualReader()
...

# Init modules (necessary for all modules before usage)
visreader.init_grpc(iCub, "name", 'l', ip_address="0.0.0.0", port=pop_vis.port)
...

# use interface modules
visreader.method_name(...)
...
...

# Close modules
visreader.close(iCub)
```

## useful links
Wiki for the iCub robot:<br>
http://wiki.icub.org/wiki/Manual

YARP website:<br>
http://www.yarp.it/git-master/index.html

git repository with helpful documents and scripts for the work with iCub:<br>
https://ai.informatik.tu-chemnitz.de/gogs/iCub_TUC/iCub_simulator_tools.git


## Authors
Torsten Fietzek (<torsten.fietzek@informatik.tu-chemnitz.de>)<br>
Helge Ülo Dinkelbach (<helge.dinkelbach@gmail.com>)<br>


## Dependencies
Python  >= 3.5<br>
YARP    >= 3.2<br>
OpenCV  >= 3.4<br>
numpy  <br>
(Optional) <br>
gRPC >= <br>