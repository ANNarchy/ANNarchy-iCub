import iCubCPP # requires iCubCPP in the present directory
import numpy as np

ann_wrapper = iCubCPP.iCubANN_wrapper()

## dublicate check
ann_wrapper.add_joint_reader("J_Reader")
ann_wrapper.add_joint_reader("J_Reader")
ann_wrapper.add_joint_reader("J_Reader1")
ann_wrapper.add_joint_reader("J_Reader2")
ann_wrapper.add_joint_reader("J_Reader3")
ann_wrapper.add_joint_reader("J_Reader4")

ann_wrapper.add_joint_writer("J_Writer")
ann_wrapper.add_joint_writer("J_Writer")
ann_wrapper.add_joint_writer("J_Writer1")
ann_wrapper.add_joint_writer("J_Writer2")

ann_wrapper.add_skin_reader("S_Reader")
ann_wrapper.add_skin_reader("S_Reader")
ann_wrapper.add_skin_reader("S_Reader1")

ann_wrapper.add_visual_reader()
ann_wrapper.add_visual_reader()

print('finish adding')
print('\n')


## init joint reader
ann_wrapper.jointR_init("J_Reader", ann_wrapper.PART_KEY_HEAD, 0.5, 15)
ann_wrapper.jointR_init("J_Reader", ann_wrapper.PART_KEY_HEAD, 0.5, 15) ## double initialization
ann_wrapper.jointR_init("J_Reader1", ann_wrapper.PART_KEY_RIGHT_ARM, -0.5, 15)   ## negative sigma
ann_wrapper.jointR_init("J_Reader1", ann_wrapper.PART_KEY_RIGHT_ARM, 0.5, 0, 2.0)   ## neuron resolution
ann_wrapper.jointR_init("J_Reader2", 'false_part_key', 0.5, 15) ## false part key
ann_wrapper.jointR_init("J_Reader3", ann_wrapper.PART_KEY_LEFT_ARM, 0.5, -15) ## negative population size
ann_wrapper.jointR_init("NO_NAME", ann_wrapper.PART_KEY_LEFT_ARM, 0.5, 15) ## not existent name
ann_wrapper.jointR_init("J_Reader4", ann_wrapper.PART_KEY_LEFT_ARM, 0.5, 0, 0.0) ## wrong population sizing


print('finish JReader init')
print('\n')

print(ann_wrapper.jointR_get_joints_deg_res("J_Reader"))
print(ann_wrapper.jointR_get_neurons_per_joint("J_Reader"))

print(ann_wrapper.jointR_get_joints_deg_res("J_Reader1"))
print(ann_wrapper.jointR_get_neurons_per_joint("J_Reader1"))

print('finish JReader resolutions')
print('\n')

print('readdouble')
print(ann_wrapper.jointR_read_double("J_Reader", 3))
print('readone')
test_read = ann_wrapper.jointR_read_one("J_Reader", 3)
print(test_read, type(test_read))
print('readall')
print(ann_wrapper.jointR_read_all("J_Reader"))

print('finish JReader reading joints')
print('\n')

print(ann_wrapper.jointR_close("J_Reader"))
print(ann_wrapper.jointR_close("J_Reader1"))

print('finish JReader close')
print('\n')

## init joint writer
ann_wrapper.jointW_init("J_Writer", ann_wrapper.PART_KEY_HEAD, 15)
ann_wrapper.jointW_init("J_Writer", ann_wrapper.PART_KEY_HEAD, 15) ## double initialization
ann_wrapper.jointW_init("J_Writer1", 'false_part_key', 15) ## false part key
ann_wrapper.jointW_init("J_Writer2", ann_wrapper.PART_KEY_LEFT_ARM, -15) ## negative population size
ann_wrapper.jointW_init("NO_NAME", ann_wrapper.PART_KEY_LEFT_ARM, 15) ## not existent name
ann_wrapper.jointW_init("J_Writer1", ann_wrapper.PART_KEY_RIGHT_ARM, 0, 2.0)

print('finish JWriter init')
print('\n')

print(ann_wrapper.jointW_get_joints_deg_res("J_Writer"))
print(ann_wrapper.jointW_get_neurons_per_joint("J_Writer"))

print(ann_wrapper.jointW_get_joints_deg_res("J_Writer1"))
print(ann_wrapper.jointW_get_neurons_per_joint("J_Writer1"))

print('finish JWriter resolutions')
print('\n')

print('writedouble')
print(ann_wrapper.jointW_write_double("J_Writer", 10.0, 3, True))
print('writeone')
print(ann_wrapper.jointW_write_one("J_Writer", test_read, 3, True))
print('writeall')
pop_all = np.array([test_read, test_read, test_read, test_read, test_read, test_read])
print(ann_wrapper.jointW_write_all("J_Writer", pop_all, True))

print('finish JWriter writing joints')
print('\n')

print(ann_wrapper.jointW_close("JWriter"))
print(ann_wrapper.jointW_close("JWriter1"))

print('finish JWriter close')
print('\n')

## init skin reader
ann_wrapper.skinR_init("S_Reader", "r")
ann_wrapper.skinR_init("S_Reader", "r")
ann_wrapper.skinR_init("NO_NAME", "r")
ann_wrapper.skinR_init("S_Reader1", "g")


print('finish SReader init')
print('\n')


print(ann_wrapper.skinR_close("SReader"))
print(ann_wrapper.skinR_close("SReader1"))

print('finish SReader close')
print('\n')

## init visual reader
ann_wrapper.visualR_init('r', 75, 48, 320, 240) ## invalid field of view width
ann_wrapper.visualR_init('r', 60, 56, 320, 240) ## invalid field of view height
ann_wrapper.visualR_init('t', 60, 48, 320, 240) ## invalid eye character
ann_wrapper.visualR_init('r', 60, 48, 400, 300) ## output size above input size
ann_wrapper.visualR_init('r') ## use of default values 

print('finish VReader init')
print('\n')

del ann_wrapper

print('finish')

