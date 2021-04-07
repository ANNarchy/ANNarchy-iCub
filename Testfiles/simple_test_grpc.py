
import iCub_ANN_Interface
import iCub_ANN_Interface.Vocabs as iCub_Constants
import matplotlib.pyplot as plt
import numpy as np
from ANNarchy import *
from iCub_ANN_Interface.ANNarchy_iCub_Populations import *
from iCub_ANN_Interface.iCub import (Joint_Reader, Joint_Writer, Visual_Reader,
                                     iCub_Interface)

import iCub_Python_Lib.plot_image_processing as plot
import supplementary.auxilary_methods as aux

# pop_vis = VisionPopulation( geometry = (240,320) )

pop_jctrl = JointControl(geometry = (30,))
# joint = [3, 4, 5]
# popsize = 60
# pop_jread = JointReadout(geometry = (3, popsize), joints=joint, encoded=True)

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

# visreader = Visual_Reader.PyVisualReader()
# if not visreader.init_grpc(iCub, 'l', ip_address="0.0.0.0", port=pop_vis.port):
#     print("Init failed")
#     exit(0)
# print("Simulate")

# jointreader = Joint_Reader.PyJointReader()
# if not jointreader.init_grpc(iCub, "name", iCub_Constants.PART_KEY_HEAD, 1., popsize, ip_address="0.0.0.0", port=pop_jread.port):
#     print("Init failed")
#     exit(0)
# print("Resolution", jointreader.get_joints_deg_res())

jointwriter = Joint_Writer.PyJointWriter()
if not jointwriter.init_grpc(iCub, "name", iCub_Constants.PART_KEY_HEAD, 30, port=pop_jctrl.port):
    print("Init failed")
    exit(0)
pop_jctrl.r = aux.encode(iCub_Constants.PART_KEY_HEAD, 2, 30, 20., 2.5)
# do something!
simulate(1)
print("Simulated")
# plot.show_image_matplot(pop_vis.r, "pop_vis", "x", "y")
# print(np.amax(pop_vis.r))

# print("Joint:", pop_jread.joints, "Value:", pop_jread.r)
# for j in joint:
#     activity = pop_jread.r[j-np.amin(joint)]
#     plt.subplot(1,2, 1)
#     plt.plot(activity)
#     plt.subplot(1,2, 2)
#     plt.plot(jointreader.read_pop_one(j))
#     plt.show()
#     print("Joint " + str(j) + " decoded:", jointwriter.decode(activity, j))
#     print("Read double:", jointreader.read_double_one(j))

# visreader.close(iCub)
# jointreader.close(iCub)
# jointwriter.retrieve_ANNarchy_input()
# jointwriter.write_ANNarchy_input(2, "abs")

jointwriter.retrieve_ANNarchy_input_enc()
jointwriter.write_ANNarchy_input_enc(2, "abs")

jointwriter.close(iCub)
