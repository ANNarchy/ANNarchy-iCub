
import iCub_ANN_Interface
from iCub_ANN_Interface.iCub import iCub_Interface, Visual_Reader
import iCub_ANN_Interface.Vocabs as iCub_Constants
from iCub_ANN_Interface.ANNarchy_iCub_Populations import *

from ANNarchy import *

pop_vis = VisionPopulation( geometry = (320,240) )

#pop_jctrl = JointControl(geometry = (6,))

#pop_jread = JointReadout(geometry = (6,))

#pop_sread = SkinPopulation(geometry = (48,))
compile(
    compiler_flags="-I/home/toto/Schreibtisch/Interface_ANNarchy_iCub/",
    extra_libs="-lprotobuf -lgrpc++ -lgrpc++_reflection",
    add_sources=iCub_ANN_Interface.__path__[0]+"/grpc/*.cc"
)

# fancy other stuff ...
for pop in populations():
    print(pop.ip_address, pop.port)
    print(pop.name, ':', pop.geometry)

    pop.connect()

# prepare iCub Interface
iCub = iCub_Interface.iCubANN_wrapper()

visreader = Visual_Reader.PyVisualReader()
if not visreader.init_grpc(iCub, 'r', ip_address="0.0.0.0", port=50000):
    exit(0)
visreader.close(iCub)

# do something!
#simulate()






