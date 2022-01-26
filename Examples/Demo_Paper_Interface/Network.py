"""
 *  Copyright (C) 2021 Torsten Fietzek
 *
 *  Network.py is part of the iCub ANNarchy interface
 *
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  The iCub ANNarchy interface is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this headers. If not, see <http://www.gnu.org/licenses/>.
"""

import os
import subprocess
from pathlib import Path

import numpy as np
import ANNarchy as ann
import iCub_ANN_Interface.ANNarchy_iCub_Populations as iCub_pop
from iCub_ANN_Interface import __root_path__ as ann_interface_root

ann.setup(dt=1)

# def create_network(joints, params):
# ## Interface Populations
# # Visual input populations
# vis_pop_right = iCub_pop.VisionPopulation(geometry=(240, 320), port=50000, name="vis_right")
# vis_pop_left = iCub_pop.VisionPopulation(geometry=(240, 320), port=50001, name="vis_left")

compute_neuron = ann.Neuron(
    parameters="""
            step = 0.
            lower = 0.
            upper = 0.
        """,
    equations="""
        dsupp = if sum(skin) > 0.: sum(skin) + 0.4*supp
                else: -1.
        supp = clip(supp + dsupp, 0., 1.): init = 0.
        r = if sum(skin) > 0.: sum(prop) + supp * step
            else: clip(r + step, lower, upper)
    """
    )

joint_ctrl_neuron = ann.Neuron(
    equations="""
        r = sum(exc)
    """
    )

# Proprioception of joint angles
pop_joint_read = iCub_pop.JointReadout(geometry=(4,), joints=[0, 1, 2, 3], name="rarm_read")
pop_compute = ann.Population(geometry=(4,), neuron=compute_neuron, name="cumpute")

# Joint control command population
pop_joint_write = iCub_pop.JointControl(geometry=(4,), neuron=joint_ctrl_neuron, name="rarm_ctrl")

# skin_read = iCub_pop.SkinPopulation(geometry=params['tr_rarm'], skin_section="forearm", name="r_arm_tactile")
pop_sread_forearm = iCub_pop.SkinPopulation(geometry = (240,), skin_section="forearm", name="r_arm_tactile")

read_compute = ann.Projection(pop_joint_read, pop_compute, "prop")
read_compute.connect_one_to_one()

skin_compute = ann.Projection(pop_sread_forearm, pop_compute, "skin")
skin_compute.connect_all_to_all(0.00001)

compute_write = ann.Projection(pop_compute, pop_joint_write, "exc")
compute_write.connect_one_to_one()

monitors = {}
monitors['m_compute'] = ann.Monitor(pop_compute, 'r', start=False)
monitors['m_prop'] = ann.Monitor(pop_joint_read, 'r', start=False)
monitors['m_skin'] = ann.Monitor(pop_sread_forearm, 'r', start=False)

# Compile network
# gRPC paths, only needed for local gRPC installation
# grpc_cpp_plugin = subprocess.check_output(["which", "grpc_cpp_plugin"]).strip().decode(sys.stdout.encoding)
# grpc_path = str(Path(grpc_cpp_plugin).resolve().parents[1]) + "/"
# grpc_include_path = grpc_path + "/include"
# grpc_lib_path = grpc_path + "/lib"
compiler_flags = "-march=native -O2" + " -I"+ann_interface_root+" -Wl,-rpath,"+ann_interface_root+"/iCub_ANN_Interface/grpc/"
extra_libs = "-lprotobuf -lgrpc++ -lgrpc++_reflection -L"+ann_interface_root+"/iCub_ANN_Interface/grpc/ -liCub_ANN_grpc"
ann.compile(directory='annarchy_iCub_paper_demo', clean=False, compiler_flags=compiler_flags, extra_libs=extra_libs)

# Connect input populations to gRPC service
for pop in ann.populations():
    try:
        print(pop.name, ':', pop.geometry)
        print(pop.ip_address, pop.port)
        pop.connect()
    except:
        pass