
import iCub_ANN_Interface
from iCub_ANN_Interface.iCub import iCub_Interface, Visual_Reader
import iCub_ANN_Interface.Vocabs as iCub_Constants
from iCub_ANN_Interface.ANNarchy_iCub_Populations import *
import numpy as np
from ANNarchy import *

import iCub_Python_Lib.plot_image_processing as plot

pop_vis = VisionPopulation( geometry = (240,320) )

#pop_jctrl = JointControl(geometry = (6,))

#pop_jread = JointReadout(geometry = (6,))

#pop_sread = SkinPopulation(geometry = (48,))

ann_interface_root = iCub_ANN_Interface.__root_path__ + "/"
compile(
    compiler_flags="-I"+ann_interface_root+" -Wl,-rpath,"+ann_interface_root+"/iCub_ANN_Interface/grpc/",
    extra_libs="-lprotobuf -lgrpc++ -lgrpc++_reflection -L"+ann_interface_root+"iCub_ANN_Interface/grpc/ -liCub_ANN_grpc",
)

# fancy other stuff ...
for pop in populations():
    print(pop.ip_address, pop.port)
    print(pop.name, ':', pop.geometry)

    pop.connect()

# prepare iCub Interface
iCub = iCub_Interface.iCubANN_wrapper()

visreader = Visual_Reader.PyVisualReader()
if not visreader.init_grpc(iCub, 'l', ip_address="0.0.0.0", port=pop.port):
    print("Init failed")
    exit(0)
print("Simulate")

# do something!
simulate(1)
print("Simulated")
plot.show_image_matplot(pop_vis.r, "pop_vis", "x", "y")
print(np.amax(pop_vis.r))

visreader.close(iCub)

