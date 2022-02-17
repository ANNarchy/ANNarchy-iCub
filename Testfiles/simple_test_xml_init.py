
import ANN_iCub_Interface
import ANN_iCub_Interface.Vocabs as iCub_Constants
import matplotlib.pyplot as plt
import numpy as np
from ANNarchy import *
from ANN_iCub_Interface.ANNarchy_iCub_Populations import *
from ANN_iCub_Interface.iCub import (Joint_Reader, Joint_Writer, Skin_Reader,
                                     Visual_Reader, iCub_Interface)

import iCub_Python_Lib.plot_image_processing as plot
import supplementary.auxilary_methods as aux

# prepare iCub Interface
iCub = iCub_Interface.ANNiCub_wrapper()
iCub.init_robot_from_file("../data/default_robot.xml")

joints_head = [3, 4, 5]
popsize_head = 10

joints_rarm = [0, 1, 2]
popsize_rarm = 10

pop_jctrl_head = JointControl(geometry = (len(joints_head), popsize_head), port=50005)
pop_jread_head = JointReadout(geometry = (len(joints_head), popsize_head), joints=joints_head, encoded=True, port=50000)

pop_jctrl_rarm = JointControl(geometry = (len(joints_rarm), popsize_rarm), port=50006)
pop_jread_rarm = JointReadout(geometry = (len(joints_rarm), popsize_rarm), joints=joints_rarm, encoded=True, port=50001)

pop_sread = SkinPopulation(geometry = (380,), skin_section="arm", port=50015)

pop_vis = VisionPopulation( geometry = (240,320), port=50010)


ann_interface_root = ANN_iCub_Interface.__root_path__ + "/"
compile(
    compiler_flags="-I"+ann_interface_root+" -Wl,-rpath,"+ann_interface_root+"/ANN_iCub_Interface/grpc/",
    extra_libs="-lprotobuf -lgrpc++ -lgrpc++_reflection -L"+ann_interface_root+"ANN_iCub_Interface/grpc/ -liCub_ANN_grpc",
)

# fancy other stuff ...
for pop in populations():
    print(pop.ip_address, pop.port)
    print(pop.name, ':', pop.geometry)

    pop.connect()



simulate(1)
print("Simulated")

plot.show_image_matplot(pop_vis.r, "VIS", "x", "y")