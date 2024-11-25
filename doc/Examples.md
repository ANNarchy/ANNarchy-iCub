# Basic Python Examples {#Examples}

## Main Module Handling
The first steps are equal for all interface modules. These are the instantiation of the main wrapper (ANNiCub_wrapper class), that is needed exactly once.
```Python
    import ANN_iCub_Interface as ann_icub
    import ANN_iCub_Interface.iCub as icub_int

    # Interface main wrapper, is needed once
    iCub = icub_int.iCub_Interface.ANNiCub_wrapper()

```
After creating this instance the respective modules can be created. For this two alternatives are currently possible and can also be combined.
The first option is the instanciation on the individual module level, that is described in the respective module sections. The second opportunity is to create multiple modules at once based on a configuration given in a XML-config file. This config-file is further explained in the Manual->Configuration section.

```Python
    # Interface initialization from XML-file
    ret_val, robot_dict = ann_icub.init_robot_from_file(iCub, "./data/demo_robot.xml")
    if not ret_val:
        sys.exit("Interface initialization failed!")
```
The inidivual instance can then be acquired from the wrapper:

```Python
    # Joint Reader
    rarm_jreader = iCub.get_jreader_by_part("PART_KEY") # or
    rarm_jreader = iCub.get_jreader_by_name("JR_name")

    # Joint Writer
    rarm_jwriter = iCub.get_jwriter_by_part("PART_KEY") # or
    rarm_jwriter = iCub.get_jwriter_by_name("JW_name")

    # Skin Reader
    rarm_sreader = iCub.get_skinreader_by_name("SR_name")

    # Visual Reader
    vreader = iCub.get_vis_reader_by_name("VR_name")

    # Kinematic Reader
    kinread = iCub.get_kin_reader_by_name("KR_name")

    # Kinematic Writer
    kinwrite = iCub.get_kin_writer_by_name("KW_name")

```


## Joint Reader
In case the module is handled indiviually, the first step is the creation and initialization of the Joint Reader module:
```Python
    # Add joint reader instances
    jreader = Joint_Reader.PyJointReader()

    # Init interface instances
    if not jreader.init(iCub, "name_reader", iCub_Const.PART_KEY_HEAD, 0.5, 15, ini_path=params.INTERFACE_INI_PATH):
        sys.exit("Initialization failed!")
```

The joint angles can be read in two different formats (explicit degree values or gaussian population code) and from single, multiple or all joints at the same time.
For the explicit values the following set of methods:
```Python
    joint_angle = jreader.read_double_one(joint=0) # angle only for joint 0; shape: single values
    joint_angles = jreader.read_double_multiple(joints=[0,1,3]) # angles for joints 0,1,3; shape [#joint_selection]
    joint_angles = jreader.read_double_all() # angles for all joints; shape [#joints_robot_part]
```

For population-coded values the following set of methods:
```Python
    joint_angle_coded = jreader.read_pop_one(joint=0) # angle only for joint 0; shape: [pop size defined by n_pop or degr_per_neuron]
    joint_angles_coded = jreader.read_pop_multiple(joints=[0,1,3]) # angles for joints 0,1,3; shape [#joint_selection, pop size defined by n_pop or degr_per_neuron]
    joint_angles_coded = jreader.read_pop_all() # angles for all joints; shape [#joints_robot_part, pop size defined by n_pop or degr_per_neuron]
```

For information about the configuration several getter methods are provided:
```Python
    jreader.get_joint_count() # number of joints controlled by the robot part
    jreader.get_joints_deg_res() # resolution of the population code -> one neuron represents XX.YY°; shape [#joints_robot_part]
    jreader.get_neurons_per_joint() # size of the population representing the full joint range in population code; shape [#joints_robot_part]

```


## Joint Writer
In case the module is handled indiviually, the first step is the creation and initialization of the Joint Writer module:
```Python
    # Add joint writer instances
    jwriter = Joint_Writer.PyJointWriter()

    # Init interface instances
    if not jwriter.init(iCub, "name_writer", iCub_Const.PART_KEY_HEAD, 0.5, 15, ini_path=params.INTERFACE_INI_PATH):
        sys.exit("Initialization failed!")
```

To configure the motion properties like acceleration use the specific setter methods:
```Python
    # For all methods the joint selection (parameter "joint") is either single specific joint (joint id: e.g. 0) or set the same value for all joints with id: -1 
    jwriter.set_joint_controlmode(control_mode, joint) # control_mode: "position"/"velocity", default "position"
    jwriter.set_joint_acceleration(acc, joint) # acc: joint acceleration
    jwriter.set_joint_velocity(speed, joint) # speed: joint velocity
```

The Joint Writer follows the same schema as the Joint Reader, providing methods to control the robot joints either with explicit degree values or population-coded values.
For the explicit values the following set of methods:
```Python
    # general parameter: joint_angles in degree or velocity; mode: "abs"/"rel"/"vel" -> absolute/relative/velocity; blocking True/False -> wait for motion execution; timeout -> stop waiting for motion
    jwriter.write_double_one(joint_angle, joint, mode, blocking, timeout) # joint -> selected joint e.g. 0
    jwriter.write_double_multiple(joint_angles, joints, mode, blocking, timeout) # joint selection, e.g. [1,2,4]
    jwriter.write_double_all(joint_angles, mode, blocking, timeout) 

```

For population-coded values the following set of methods:
```Python
    # general parameter: joint_angles in population code; mode: "abs"/"rel" -> absolute/relative; blocking True/False -> wait for motion execution; timeout -> stop waiting for motion
    jwriter.write_pop_one(joint_angle, joint, mode, blocking, timeout) # joint_angle shape: [pop_size]; joint -> selected joint e.g. 0
    jwriter.write_pop_multiple(joint_angles, joints, mode, blocking, timeout) # joint_angles shape: [#joint_selection, pop_size] # joint selection, e.g. [1,2,4]
    jwriter.write_pop_all(joint_angles, mode, blocking, timeout) # joint_angles shape: [#joints_robot_part, pop_size] 

```

For information about the configuration several getter methods are provided:
```Python
    jwriter.get_joint_count() # number of joints controlled by the robot part
    jwriter.get_joints_deg_res() # resolution of the population code -> one neuron represents XX.YY°; shape [#joints_robot_part]
    jwriter.get_neurons_per_joint() # size of the population representing the full joint range in population code; shape [#joints_robot_part]
    jwriter.get_joint_limits() # return joint working range for all joints controlled by the writer; shape [#joints_robot_part, 2]; format: [joint, 0: max/1: min]
    jwriter.get_joint_limits_max() # return the joints maximum possible values for each joint in the robot part; shape [#joints_robot_part]
    jwriter.get_joint_limits_min() # return the joints minimum possible values for each joint in the robot part; shape [#joints_robot_part]

```


## Visual Reader
In case the module is handled indiviually, the first step is the creation and initialization of the Visual Reader module:
```Python
    # Add visual reader instances
    visreader = Visual_Reader.PyVisualReader()

    # Init interface instances
    if not visreader.init(iCub, "name_reader", 'r', ini_path=params.INTERFACE_INI_PATH):
        sys.exit("Initialization failed!")
```

For the image retrieval from the robot currently two methods exists:
First Method: The images from the iCub are preprocessed (normalization [0., 1.] and either RGB or grayscale images) and dependent on the configuration the left, right or both images are retrieved. For the images of both eyes only one reader module is necessary.
```Python
    # grayscale/RGB images (dependent on INI-file parameter); preprocessed -> range [0., 1.]
    imgs = visreader.read_robot_eyes()
    imgs = test_imgs.reshape(2, 240, 320) # both eye images are retrieved
    
    imgright = imgs[0] # right eye image
    imgleft = imgs[1] # left eye image
```

Second Method: The raw images are retrieved from the iCub. The images are in RGB-colors and in the value range is [0, 255]. For the images of both eyes only two reader modules are necessary.
```Python
    # RGB images; no preprocessing -> range [0, 255]
    imgright = np.array(visreader_r.retrieve_robot_eye()).reshape(240, 320, 3)
    imgleft = np.array(visreader_l.retrieve_robot_eye()).reshape(240, 320, 3)
```


## Skin Reader
In case the module is handled indiviually, the first step is the creation and initialization of the Skin Reader module:
```Python
    # Add skin reader instance
    sreader = Skin_Reader.PySkinReader()

    # Init interface instances
    if not sreader.init(iCub, "skin_right", "r", True, ini_path=params.INTERFACE_INI_PATH):
        sys.exit("Initialization failed!")
```

At this point the skin reader only handles the skin/tactile sensors at the iCub arms.
To read the data from the sensors two the skin reader offers two different ways:
The first option is to directly receive the sensor data from the different arm sections:
```Python
    # Read skin sensor data -> skin section specific
    print("Data arm:") # upper arm
    print(sreader.read_skin_arm())

    print("Data forearm:")
    print(sreader.read_skin_forearm())

    print("Data hand:")
    print(sreader.read_skin_hand())
```

In the second option the data is buffered inside the reader module and can be collected per part after the data acquisition: 
```Python
    # Read skin sensor data -> buffered
    for i in range(10):
        # read tactile data
        sreader.read_tactile()

    # print tactile data
    print("Data arm:") # upper arm
    print(sreader.get_tactile_arm())

    print("Data forearm:")
    print(sreader.get_tactile_forearm())

    print("Data hand:")
    print(sreader.get_tactile_hand())
```

To get information about the sensor count and therefore the vector size of the different data arrays the following getter-methods are provided:
```Python
    sreader.get_tactile_arm_size()
    sreader.get_tactile_forearm_size()
    sreader.get_tactile_hand_size()
```


## Kinematic Reader
In case the module is handled indiviually, the first step is the creation and initialization of the Kinematic Reader module:
```Python
    # Add kinematic reader instance
    kinreader = Kinematic_Reader.PyKinematicReader()

    # Init kinematic reader
    if not kinreader.init(iCub, "name_fkin", part=iCub_const.PART_KEY_RIGHT_ARM, version=2, ini_path=params.INTERFACE_INI_PATH, offline_mode=params.offline):
        sys.exit("Initialization failed")
```

To get information about the current state of the kinematic chain several methods exists:
```Python
    print("DOF:", kinreader.get_DOF()) # complete degree of freedom (DOF) of the chain
    print("Active DOF:", kinreader.get_DOF_links()) # active links of the chain
    print("Blocked links:", kinreader.get_blocked_links()) # blocked links of the chain
    print("Current angles:", np.rad2deg(kinreader.get_jointangles())) # current joint angles of the active part of the kinematic chain
```

The forward kinematic is by default in an online mode, directly receiving the joint angles from the robot. But if the reader is configured to work in offline mode, no connection to the robot is established. Then the state of the kinematic chain need to be handled manually. This means the static links should be blocked and the joint angles of the active part has to be set in radians. Since all angles are initialized with zero, blocked links may need to be set once before blocking them.

```Python
    # Perform forward kinematic
    if params.offline:
        kinreader.block_links([0, 1, 2]) # block torso links
        joint_angles = np.deg2rad(np.array([15., 16., 0., 70., -90., 0., 0.]))
        kinreader.set_jointangles(joint_angles)
```

Finally the forward kinematic can be performed, either for the end-effector (hand for the arms) or for a specific joint in the kinematic chain. The position is given in the robot reference frame.
```Python
    # print end-effector position
    end_eff_pos = kinreader.get_handposition()
    print("End-Effector", end_eff_pos)  # (robot reference frame)
    print("End-Effector", iTransform.transform_position(end_eff_pos, params.Transfermat_robot2world))  # (simulator reference frame)

    # print position for specific joint of the kinematic chain
    joint3_pos = kinreader.get_jointposition(3)
    print("Joint 3", joint3_pos)    # (robot reference frame)
    print("Joint 3", iTransform.transform_position(joint3_pos, params.Transfermat_robot2world))    # (simulator reference frame)
```


## Kinematic Writer
In case the module is handled indiviually, the first step is the creation and initialization of the Kinematic Reader module:
```Python
    # Add kinematic writer instance
    kinwriter = Kinematic_Writer.PyKinematicWriter()

    # Init kinematic writer
    if not kinwriter.init(iCub, "invkin", part=iCub_Const.PART_KEY_RIGHT_ARM, version=2, ini_path=params.INTERFACE_INI_PATH, offline_mode=params.offline):
        sys.exit("Initialization failed")
```

To get information about the current state of the kinematic chain several methods exists:
```Python
    print("DOF:", kinwriter.get_DOF()) # complete degree of freedom (DOF) of the chain
    print("Active DOF:", kinwriter.get_DOF_links()) # active links of the chain
    print("Blocked links:", kinwriter.get_blocked_links()) # blocked links of the chain
    print("Current angles:", np.rad2deg(kinwriter.get_jointangles())) # current joint angles of the active part of the kinematic chain
```

The inverse kinematic is by default in an online mode, directly receiving the joint angles from the robot. But if the writer is configured to work in offline mode, no connection to the robot is established. Then the state of the kinematic chain need to be handled manually. This means the static links should be blocked and the joint angles of the active part has to be set in radians. Since all angles are initialized with zero, blocked links may need to be set once before blocking them.
Finally the inverse kinematic can be performed depended on online or offline mode:
```Python
    if params.offline:
        # block links and set starting angles manually
        kinwriter.block_links(blocked_joints)
        kinwriter.set_jointangles(joint_angles)
        # perform inverse kinematics for given target
        joint_angles = kinwriter.solve_InvKin(target_position)
    else:
        # define blocked/static links; current angles are retrieved from the robot and perform inverse kinematics for given target
        joint_angles = kinwriter.solve_InvKin(target_position, blocked_joints)
    print("Estimated joint angles:", np.rad2deg(joint_angles))
```


## Final Wrap-up
To clean up at the end, each module is equipped with a close-method. These can be called for all in one from the main wrapper with the clear method to clean up all initialized modules.

```Python

    # Either close module seperately or
    module.close(iCub)

    # Close all interface instances in one step
    print('----- Close interface instances -----')
    iCub.clear()
```