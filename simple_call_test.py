import iCubCPP # requires iCubCPP in the present directory

ann_wrapper = iCubCPP.iCubANN_wrapper()

## dublicate check
ann_wrapper.add_joint_reader("xxx")
ann_wrapper.add_joint_reader("xxx")

ann_wrapper.add_joint_writer("xxx")
ann_wrapper.add_joint_writer("xxx")

ann_wrapper.add_skin_reader("xxx")
ann_wrapper.add_skin_reader("xxx")

ann_wrapper.add_visual_reader()
ann_wrapper.add_visual_reader()


## init joint reader
ann_wrapper.jointR_init("xxx", ann_wrapper.PART_KEY_HEAD, 0.5, 15)

## init joint writer
ann_wrapper.jointW_init("xxx", ann_wrapper.PART_KEY_HEAD, 15)

## init joint writer
ann_wrapper.skinR_init("xxx", "r")

## init joint writer
ann_wrapper.visualR_init('r', 60, 48, 320, 240)

print('finish')

