
import matplotlib.pyplot as plt
import numpy as np
import ANNarchy as ann

import ANN_iCub_Interface as ann_icub
import ANN_iCub_Interface.ANNarchy_iCub_Populations as icub_pop
from ANN_iCub_Interface.iCub import iCub_Interface

import iCub_Python_Lib.plot_image_processing as plot
import supplementary.auxilary_methods as aux



# prepare iCub Interface
iCub = iCub_Interface.ANNiCub_wrapper()
ann_icub.init_robot_from_file(iCub, "../data/default_robot.xml")

joints_head = [3, 4, 5]
popsize_head = 10

joints_rarm = [0, 1, 2]
popsize_rarm = 10

pop_jctrl_head = icub_pop.JointControl(geometry = (len(joints_head), popsize_head), port=50005)
pop_jread_head = icub_pop.JointReadout(geometry = (len(joints_head), popsize_head), joints=joints_head, encoded=True, port=50000)

pop_jctrl_rarm = icub_pop.JointControl(geometry = (len(joints_rarm), popsize_rarm), port=50006)
pop_jread_rarm = icub_pop.JointReadout(geometry = (len(joints_rarm), popsize_rarm), joints=joints_rarm, encoded=True, port=50001)

pop_sread = icub_pop.SkinPopulation(geometry = (380,), skin_section="arm", port=50015)

pop_vis = icub_pop.VisionPopulation( geometry = (240,320), port=50010)


ann_interface_root = ann_icub.__root_path__ + "/"
ann.compile(compiler_flags=ann_icub.__ann_compile_args__, extra_libs=ann_icub.__ann_extra_libs__,)

# fancy other stuff ...
for pop in ann.populations():
    print(pop.ip_address, pop.port)
    print(pop.name, ':', pop.geometry)

    pop.connect()


ann.simulate(1)
print("Simulated")

plot.show_image_matplot(pop_vis.r, "VIS", "x", "y")

ann_icub.save_robot_to_file(iCub, "./results/test_robot.xml")

iCub.clear()

ann_icub.init_robot_from_file(iCub, "./results/test_robot.xml")