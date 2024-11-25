# Generic Python Examples {#Generic_Examples}
Take a look in the testfiles for a specific implementation. Further examples can be found in [iCub_simulator_tools->python_scripts](https://ai.informatik.tu-chemnitz.de/gogs/iCub_TUC/iCub_simulator_tools/src/master/python_scripts)<br>
More examples can be found in the [Examples](https://github.com/ANNarchy/ANNarchy-iCub/tree/master/Examples) folder. 
Basic examples presenting the usage of each part of the interface:
    - perception: example_visual_perception, example_tactile_perception
    - action: example_joint_position_control, example_forward_kinematics, example_inverse_kinematics

## Non-gRPC version
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
kinreader.init(iCub, name, ...)
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
# or iCub.clear() for clear all at once
```

## gRPC version
```Python
import ANNarchy as ann
from ANN_iCub_Interface import __ann_compile_args__, __ann_extra_libs__
from ANN_iCub_Interface.iCub import Joint_Reader, Joint_Writer, iCub_Interface, Visual_Reader, Skin_Reader, Kinematic_Reader
from ANN_iCub_Interface.ANNarchy_Populations import JointReadout, JointControl, SkinPopulation, VisionPopulation, KinematicPopulation
import ANN_iCub_Interface.Vocabs as iCub_Constants

# Create ANNarchy populations e.g. VisionPopulation
pop_vis = VisionPopulation(geometry = (240, 320))
...

# Create the rest of ANNarchy network
...

# Compile ANNarchy network
ann.compile(directory='annarchy', compiler_flags=__ann_compile_args__, extra_libs=__ann_extra_libs__)

# Connect ANNarchy interface populations to gRPC service
pop_vis.connect()
...

# Instantiate main iCub wrapper
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
