import iCub_ANN_Interface

from ANNarchy import *
from iCub_ANN_Interface.ANNarchy_iCub_Populations import *

pop_vis = VisionPopulation( geometry = (320,240) )

#pop_jctrl = JointControl(geometry = (6,))

#pop_jread = JointReadout(geometry = (6,))

#pop_sread = SkinPopulation(geometry = (48,))
compile(compiler_flags="-I/home/hdin/Dokumente/git_repos/Interface_ANNarchy_iCub/ -lprotobuf -lgrpc++ -lgrpc++_reflection")

# fancy other stuff ...
for pop in populations():
    print(pop.ip_address, pop.port)
    print(pop.name, ':', pop.geometry)

    pop.connect()

# do something!
#simulate()






