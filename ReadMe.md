## iCub ANNarchy Interface
This program is an interface between the Neurosimulator ANNarchy and the iCub robot (tested with the iCub simulator and partly with gazebo). It is written in C++ with a Cython wrapping to Python.


## Interface description
Possible actions are the reading and writing of joint angles, get the current state or move the robot joints. Further, the camera images and the tactile sensors data can be received.

The interface has a modular structure with one main class and several subclasses.
The main class is the "iCubANN" class, handling the subclass instances. The subclasses representing the different modules are JointReader, JointWriter, VisualReader and SkinReader with the following functionalities:

1. *JointReader:*<br>
    This module handles the joint reading. The iCub robot is divided in multiple robot parts, which are the head, right arm, left arm, torso right leg and left leg.<br>
    For each part a seperate joint reader instance is needed. Therefore, one has to add as many instances as needed to the parts_writer map of the iCubANN class with the "AddJointReader" method.<br>
    Before the first usage of a joint reader instance, it has to be initialized with some specifications like the robot part. Then the joint angles can be received in two ways. As a double value or in a population code for one, multiple or all joint/s of the associated iCub part.

2. *JointWriter:*<br>
    The joint writer has a similar structure to the joint reader. Like there for each iCub part a separate instance has to be added to the parts_reader map of the iCub_ANN class. They also has to be initialized before usage.<br>
    For the writing of the joint angles the same ways are possible like for the reading. The joint angle can be written as double value or as population code for one, multiple or all joint/s of the associated part.

3. *VisualReader:*<br>
    This module handles the receiving of the camera images. At this time only one visual reader instance is possible due to YARP limitations for the used YARP RFModule (run only one Module).<br>
    This reader can be initilized for the right ('r') or left ('l') eye, limiting the visual data to be monocular. The grayscaled image is returned as an 1D-vector with a normalization from 0.0 (black) to 1.0 (white).<br>
    In the binocular mode ('b') the images of both cameras images are received and seperately added as 1D-vectors to the image buffer.

4. *SkinReader:*<br>
    This module handles the tactile data from the iCub's artificial skin. The robot is at several parts equipped with skin modules, reacting to pressure.<br>
    The sensor data for the arms can be read out with this module. The skin of the iCub arm is seperated in three modules, being the arm, forearm and hand.<br>
    The tactile data is returned as a vector with doubles in a range of 0.0 to 1.0. Where 0. is no pressure and 1.0 is the maximum sensor response.


## Folder structure
- Interface_ANNarchy_iCub -> Main folder containing the whole interface
    - Cython_ext -> Contains the Cython files (pyx, pxd) for wrapping the C++ code for the use in Python 
    - data -> Folder capsulate the data files used by the interface.
        - sensor_positions -> This folder caontains the files from the iCub simulator installation with the position data for the tactile sensors.
        - interface_param.ini -> ini-file with several parameters for the interface
        - joint_limits_sim.ini -> In the ini file the simulated robot joint limitations of the iCub are given.
        - joint_limits_real.ini -> In the ini file the real robot joint limitations of the iCub are given.<br>
                            !!! This should be checked before the usage with the real robot, to avoid damage. !!!
    - doc -> This folder contains the doxygen generated documentation for the interface
    - include -> This folder contains the C++ header files for the interface modules.
        - INI_Reader -> The INI-Reader is an external module, which is used to handle ini-files.
    - src -> This folder contains the C++ source files for the interface modules.
    - Testfiles -> files for interface testing


## Preparation
To use the interface in Python the source code has to be compiled. For compilation execute the make.py script. This generates the nessecary Makefile and starts the build process. In case of missing/false include directories the make_config file has to be modified.
The resulting .so files are saved in the build folder. 

For use in Python the build folder could be added to the Pythonpath-variable, therefore add the following line to the .bashrc in the home-directory:
```
export PYTHONPATH=${PYTHONPATH}:/path/to/repo/Interface_ANNarchy_iCub/build
```

Otherwise the library path has to be added to the import path inside your user python script module above `import iCub_Interface`. This is done with the sys module:
```Python
import sys
sys.path.append("path/to/so/files")
import iCub_Interface
...
```

## Generic Python Example

```Python
import iCub_Interface

iCub = iCub_Interface.iCubANN_wrapper()
...
# add nessacary instances
iCub.add_joint_reader(jreader_name)
iCub.add_joint_writer(jwriter_name)
iCub.add_skin_reader(sreader_name)
iCub.add_visual_reader()

# use interface modules
iCub.parts_reader[jreader_name].method_name(...)
iCub.parts_writer[jwriter_name].method_name(...)
iCub.tactile_reader[sreader_name].method_name(...)
iCub.visual_input.method_name(...)
...
del iCub
```

## useful links
Wiki for the iCub robot:<br>
http://wiki.icub.org/wiki/Manual

YARP website:<br>
http://www.yarp.it/index.html

git repository with scripts to control the iCub simulator:<br>
https://ai.informatik.tu-chemnitz.de/gogs/torsten/iCub_simulator_tools.git


## Authors
Torsten Follak (<torsten.follak@informatik.tu-chemnitz.de>)<br>
Helge Ülo Dinkelbach<br>


## Dependencies
Python  >= 3.5<br>
YARP    >= 3.2<br>
OpenCV  >= 3.4<br>
