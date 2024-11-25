## Installation

### Dependencies
At first install the YARP and iCub related software before installing the interface. An installation guide for YARP/iCub can be found in the github [superbuild repository](https://github.com/robotology/robotology-superbuild).

For the use with ANNarchy, install ANNarchy following the [installation guide](https://annarchy.github.io/Installation.html) in the documentation.


### Default Installation
Then the interface can be installed with pip by executing the following line in a terminal in the interface directory.

```bash
pip3 install .
```
In case of missing/false include directories the directories for YARP and/or OpenCV need to be modified in build_config.toml (yarp_prefix/cv_include).<br>

Otherwise it could also be in installed with pip and the github link:
```bash
pip3 install git+https://github.com/ANNarchy/ANNarchy-iCub.git # for specific branch add "@branchname" without spaces
```


### Enable Low-Level gRPC communication (optional)
The interface is build in a default configuration. In this case the gRPC communication with ANNarchy is disabled. To enable this part, set the use_grpc parameter in build_config.toml to True. This part depends on the gRPC package and the protobuf compiler.
The system packages are recommended especially for recent Linux versions (>Ubuntu 18.XX). Install the following apt packages: protobuf-compiler-grpc, libgrpc++-dev
```bash
    sudo apt install protobuf-compiler-grpc libgrpc++-dev
```
For the source installation of gRPC ([installation from the repository](https://grpc.io/docs/languages/cpp/quickstart/#install-grpc) with cmake or bazel) you need to take care of other packages, using protobuf like gazebo to handle the needed versions. Since this can lead to a lot of trouble, the use of the system packages is recommended.


### Update
First checkout the current changes for the repository. If there are changes in the c++-core it could be necessary to set the rebuild_cython flag in build_config.toml to True, to make sure the changes are processed correctly.

When installed directly from github simply reinstall the interface with the upgrade flag:
```bash
pip3 install --upgrade git+https://github.com/ANNarchy/ANNarchy-iCub.git # for specific branch add "@branchname" without spaces
```