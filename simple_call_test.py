import iCubCPP # requires iCubCPP in the present directory

ann_wrapper = iCubCPP.iCubANN_wrapper()

## dublicate check
ann_wrapper.add_joint_reader("J_Reader")
ann_wrapper.add_joint_reader("J_Reader")
ann_wrapper.add_joint_reader("J_Reader1")
ann_wrapper.add_joint_reader("J_Reader2")
ann_wrapper.add_joint_reader("J_Reader3")

ann_wrapper.add_joint_writer("J_Writer")
ann_wrapper.add_joint_writer("J_Writer")
ann_wrapper.add_joint_writer("J_Writer1")
ann_wrapper.add_joint_writer("J_Writer2")

ann_wrapper.add_skin_reader("S_Reader")
ann_wrapper.add_skin_reader("S_Reader")

ann_wrapper.add_visual_reader()
ann_wrapper.add_visual_reader()

print('finish adding')

## init joint reader
ann_wrapper.jointR_init("J_Reader", ann_wrapper.PART_KEY_HEAD, 0.5, 15)
ann_wrapper.jointR_init("J_Reader", ann_wrapper.PART_KEY_HEAD, 0.5, 15) ## double initialization
ann_wrapper.jointR_init("J_Reader1", ann_wrapper.PART_KEY_RIGHT_ARM, -0.5, 15)   ## negative sigma
ann_wrapper.jointR_init("J_Reader2", 'false_part_key', 0.5, 15) ## false part key
ann_wrapper.jointR_init("J_Reader3", ann_wrapper.PART_KEY_LEFT_ARM, 0.5, -15) ## negative population size
ann_wrapper.jointR_init("NO_NAME", ann_wrapper.PART_KEY_LEFT_ARM, 0.5, 15) ## not existent name


print('finish JReader init')

## init joint writer
ann_wrapper.jointW_init("J_Writer", ann_wrapper.PART_KEY_HEAD, 15)
ann_wrapper.jointW_init("J_Writer", ann_wrapper.PART_KEY_HEAD, 15) ## double initialization
ann_wrapper.jointW_init("J_Writer1", 'false_part_key', 15) ## false part key
ann_wrapper.jointW_init("J_Writer2", ann_wrapper.PART_KEY_LEFT_ARM, -15) ## negative population size
ann_wrapper.jointW_init("NO_NAME", ann_wrapper.PART_KEY_LEFT_ARM, 15) ## not existent name


print('finish JWriter init')

## init skin reader
ann_wrapper.skinR_init("S_Reader", "r")
ann_wrapper.skinR_init("S_Reader", "r")

print('finish SReader init')

## init joint writer
ann_wrapper.visualR_init('r', 75, 48, 320, 240) ## invalid field of view width
ann_wrapper.visualR_init('r', 60, 56, 320, 240) ## invalid field of view height
ann_wrapper.visualR_init('t', 60, 48, 320, 240) ## invalid eye character
ann_wrapper.visualR_init('r', 60, 48, 400, 300) ## output size above input size
ann_wrapper.visualR_init('r') ## use of default values 


print('finish VReader init')


print('finish')

