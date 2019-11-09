# distutils: language = c++
# cython: language_level = 3

from libcpp.string cimport string
from libcpp.vector cimport vector
from libcpp cimport bool as bool_t
from libc.stdlib cimport malloc, free
import sys



cdef extern from "Interface_iCub.h":

    cdef struct iCub_ANN:
       
        #TODO: we need to add here all function declarators we need to access
        
        # add Reader/Writer
        void AddJointReader(string)
        void AddJointWriter(string)
        void AddSkinReader(string)
        void AddVisualReader()

        # Access to joint reader member functions
        # initialize the joint reader with given parameters
        bint jointR_init(string, string, double, int, double)
        # get the size of the populations encoding the joint angles
        vector[int] jointR_get_neurons_per_joint(string)
        # get the resolution in degree of the populations encoding the joint angles
        vector[double] jointR_get_joints_deg_res(string)
        # close joint reader with cleanup
        void jointR_close(string)
        # read one joint and return joint angle directly as double value
        double jointR_read_double(string , int)
        # read one joint and return the joint angle encoded in a vector
        vector[double] jointR_read_one(string, int)
        # read all joints and return the joint angles encoded in vectors
        vector[vector[double]] jointR_read_all(string)

        # Access to joint writer member functions
        # initialize the joint writer with given parameters
        bint jointW_init(string, string, int, double)
        # get the size of the populations encoding the joint angles
        vector[int] jointW_get_neurons_per_joint(string)
        # get the resolution in degree of the populations encoding the joint angles
        vector[double] jointW_get_joints_deg_res(string)
        # close joint reader with cleanup
        void jointW_close(string)
        # write one joint as double value
        bint jointW_write_double(string, double, int, bool)
        # write one joint with the joint angle encoded in a population
        bint jointW_write_one(string, vector[double], int, bool)
        # write all joints with joint angles encoded in populations
        bint jointW_write_all(string, vector[vector[double]], bool)

        # Access to skin reader member functions
        # init skin reader with given parameters
        bint skinR_init(string, char)
        # read sensor data
        void skinR_read_tactile(string)
        # return tactile data for hand skin
        vector[double] skinR_get_tactile_hand(string)
        # return tactile data for forearm skin
        vector[double] skinR_get_tactile_forearm(string)
        # return tactile data for upper arm skin
        vector[double] skinR_get_tactile_arm(string)
        # return the taxel positions given by the ini files
        vector[vector[double]] skinR_get_taxel_pos(string, string)
        # close and clean skin reader
        void skinR_close(string)

        # Access to visual reader member functions
        # init Visual reader with given parameters for image resolution, field of view and eye selection
        bint visualR_init(char, double, double, int, int)
        # start reading images from the iCub with YARP-RFModule
        void visualR_start(int, char**)
        # stop reading images from the iCub, by terminating the RFModule
        void visualR_stop()
        # read image vector from the image buffer and remove it from the buffer
        vector[double] visualR_read_fromBuf()


    # Instances:
    iCub_ANN my_interface # defined in Interface_iCub.cpp

cdef class iCubANN_wrapper:

    PART_KEY_HEAD = "head";            # part key for iCub head; can be used for joint reader/writer initialization
    PART_KEY_TORSO = "torso";          # part key for iCub torso; can be used for joint reader/writer initialization
    PART_KEY_RIGHT_ARM = "right_arm";  # part key for iCub right arm; can be used for joint reader/writer initialization
    PART_KEY_LEFT_ARM = "left_arm";    # part key for iCub left arm; can be used for joint reader/writer initialization
    PART_KEY_RIGHT_LEG = "right_leg";  # part key for iCub right leg; can be used for joint reader/writer initialization
    PART_KEY_LEFT_LEG = "left_leg";    # part key for iCub left leg; can be used for joint reader/writer initialization

    # numbers for head joints
    JOINT_NUM_NECK_PITCH = 0
    JOINT_NUM_NECK_ROLL = 1
    JOINT_NUM_NECK_YAW = 2
    JOINT_NUM_EYES_TILT = 3
    JOINT_NUM_EYES_VERSION  = 4
    JOINT_NUM_EYES_VERGENCE  = 5

    # numbers for arm joints (left/right identical)
    JOINT_NUM_SHOULDER_PITCH = 0
    JOINT_NUM_SHOULDER_ROLL = 1
    JOINT_NUM_SHOULDER_YAW = 2
    JOINT_NUM_ELBOW = 3
    JOINT_NUM_WRIST_PROSUP = 4
    JOINT_NUM_WRIST_PITCH = 5
    JOINT_NUM_WRIST_YAW = 6
    JOINT_NUM_HAND_FINGER = 7
    JOINT_NUM_THUMB_OPPOSE = 8
    JOINT_NUM_THUMB_PROXIMAL = 9
    JOINT_NUM_THUMB_DISTAL = 10
    JOINT_NUM_INDEX_PROXIMAL = 11
    JOINT_NUM_INDEX_DISTAL = 12
    JOINT_NUM_MIDDLE_PROXIMAL = 13
    JOINT_NUM_MIDDLE_DISTAL = 14
    JOINT_NUM_PINKY = 15

    # numbers for leg joints (left/right identical)
    JOINT_NUM_HIP_PITCH = 0
    JOINT_NUM_HIP_ROLL = 1
    JOINT_NUM_HIP_YAW = 2
    JOINT_NUM_KNEE = 3
    JOINT_NUM_ANKLE_PITCH = 4
    JOINT_NUM_ANKLE_ROLL = 5

    # numbers for torso joints
    JOINT_NUM_TORSO_YAW = 0
    JOINT_NUM_TORSO_ROLL = 1
    JOINT_NUM_TORSO_PITCH = 2

    def __cinit__(self):
        print("Initialize iCub Interface.")
        #my_interface.init() - we need a special init?

    ### add Reader/Writer
    def add_jointReader(self, name):
        """
            Calls iCub_ANN::add_jointReader(std::string name)

            params: std::string name        -- name for the added joint reader in the map, can be freely selected
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')

        # call the interface
        my_interface.add_jointReader(s)

    def add_jointWriter(self, name):
        """
            Calls iCub_ANN::add_jointWriter(std::string name)

            params: std::string name        -- name for the added joint writer in the map, can be freely selected
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')

        # call the interface
        my_interface.add_jointWriter(s)

    def add_skinReader(self, name):
        """
            Calls iCub_ANN::add_skinReader(std::string name)

            params: std::string name        -- name for the added skin reader in the map, can be freely selected
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')

        # call the interface
        my_interface.add_skinReader(s)

    def add_visualReader(self):
        """
            Calls iCub_ANN::add_visualReader()

            params: std::string name        -- name for the added visual reader in the map, can be freely selected
        """
        # call the interface
        my_interface.add_visualReader()

    ### end add Reader/Writer


    ### Access to visual reader member functions
    # init Visual reader with given parameters for image resolution, field of view and eye selection
    def visualR_init(self, eye, fov_width, fov_height, img_width, img_height):
        """
            Calls bool iCub_ANN::visualR_init(char eye, double fov_width, double fov_height, int img_width, int img_height)

            params: char eye            -- characteer representing the selected eye (l/L; r/R)
                    double fov_width    -- output field of view width in degree [0, 60] (input fov width: 60°)
                    double fov_height   -- output field of view height in degree [0, 48] (input fov height: 48°)
                    int img_width       -- output image width in pixel (input width: 320px)
                    int img_height      -- output image height in pixel (input height: 240px)

            return: bool                -- return True, if successful
        """

        # call the interface
        return my_interface.visualR_init(eye, fov_width, fov_height, img_width, img_height)

    # start reading images from the iCub with a YARP-RFModule
    def visualR_start(self):
        """
            Calls void iCub_ANN::visualR_start(int argc, char *argv[])
        """
        argv = sys.argv
        # Declare char**
        cdef char** c_argv
        argc = len(argv)
        # Allocate memory
        c_argv = <char**>malloc(argc * sizeof(char*))
        # Check if allocation went fine
        if c_argv is NULL:
            raise MemoryError()
        # Convert str to char* and store it into our char**
        for i in range(argc):
            argv[i] = argv[i].encode()
            c_argv[i] = argv[i]
        # call the interface
        my_interface.visualR_start(argc, c_argv)
        # Let him go
        free(c_argv)

    # stop reading images from the iCub, by terminating the RFModule
    def visualR_stop(self):
        """
            Calls void iCub_ANN::visualR_stop()
        """

        # call the interface
        my_interface.visualR_stop()

    # return image vector from the image buffer and remove it from the buffer
    def visualR_read_fromBuf(self):
        """
            Calls std::vector<double> iCub_ANN::visualR_read_fromBuf()

            return: std::vector<double>     -- image (1D-vector) from the image buffer
        """

        # call the interface
        return my_interface.visualR_read_fromBuf()

    ### end access to visual reader member functions


    ### Access to joint reader member functions
    # initialize the joint reader with given parameters
    def jointR_init(self, name, part, sigma, n_pop, degr_per_neuron=0.0):
        """
            Calls bool iCub_ANN::jointR_init(std::string name, std::string part, double sigma, int pop_n, double deg_per_neuron)
        
            params: std::string name        -- name of the selected joint reader
                    std::string part        -- string representing the robot part, has to match iCub part naming
                                                {left_(arm/leg), right_(arm/leg), head, torso}
                    sigma                   -- sigma for the joints angles populations coding
                    int pop_size            -- number of neurons per population, encoding each one joint angle;
                                                only works if parameter "deg_per_neuron" is not set
                    double deg_per_neuron   -- degree per neuron in the populations, encoding the joints angles;
                                                if set: population size depends on joint working range

            return: bool                    -- return True, if successful
        """
        # we need to transform py-string to c++ compatible string
        cdef string c_name = name.encode('UTF-8')
        cdef string key = part.encode('UTF-8')

        return my_interface.jointR_init(c_name, key, sigma, n_pop, degr_per_neuron)

    # get the size of the populations encoding the joint angles
    def jointR_get_neurons_per_joint(self, name):
        """
            Calls std::vector<int> iCub_ANN:: jointR_get_neurons_per_joint(std::string name)

            params: std::string name        -- name of the selected joint reader

            return: std::vector<int>        -- return vector, containing the population size for every joint
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')

        # call the interface
        return my_interface.jointR_get_neurons_per_joint(s)

    # get the resolution in degree of the populations encoding the joint angles
    def jointR_get_joints_deg_res(self, name):
        """
            Calls std::vector<double> iCub_ANN::jointR_get_joints_deg_res(std::string name)

            params: std::string name        -- name of the selected joint reader

            return: std::vector<double>     -- return vector, containing the resolution for every joints population codimg in degree
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')

        # call the interface
        return my_interface.jointR_get_joints_deg_res(s)

    # close joint reader with cleanup
    def jointR_close(self, name):
        """
            Calls iCub_ANN::jointR_close(std::string name)

            params: std::string name    -- name of the selected joint reader
                    int joint           -- joint number of the robot part

            return: double              -- joint angle read from the robot
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')

        # call the interface
        my_interface.jointR_close(s)

    # read one joint and return joint angle directly as double value
    def jointR_read_double(self, name, joint):
        """
            Calls double iCub_ANN::jointR_read_double(std::string name, int joint)

            params: std::string name        -- name of the selected joint reader
                    int joint               -- joint number of the robot part

            return: std::vector<double>     -- population vector encoding the joint angle
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')

        # call the interface
        return my_interface.jointR_read_double(s, joint)

    # read one joint and return the joint angle encoded in a vector (population coding)
    def jointR_read_one(self, name, joint):
        """
            Calls std::vector<double> iCub_ANN::jointR_read_one(std::string name, int joint)

            params: std::string name                    -- name of the selected joint reader

            return: std::vector<std::vector<double>>    -- population vectors encoding every joint angle from associated robot part
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')

        # call the interface
        return my_interface.jointR_read_one(s, joint)

    # read all joints and return the joint angles encoded in vectors (population coding)
    def jointR_read_all(self, name):
        """
            Calls std::vector<std::vector<double>> iCub_ANN::jointR_read_all(std::string name)

            params: std::string name        -- name of the selected joint reader
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')

        # call the interface
        return my_interface.jointR_read_all(s)

    ### end access to joint reader member functions


    ### Access to joint writer member functions
    # initialize the joint writer with given parameters
    def jointW_init(self, name, part, n_pop, degr_per_neuron=0.0):
        """
            Calls bool iCub_ANN::jointW_init(std::string name, std::string part, int pop_size, double deg_per_neuron)

            params: std::string name        -- name of the selected joint writer
                    std::string part        -- string representing the robot part, has to match iCub part naming
                                                {left_(arm/leg), right_(arm/leg), head, torso}
                    int pop_size            -- number of neurons per population, encoding each one joint angle;
                                                only works if parameter "deg_per_neuron" is not set
                    double deg_per_neuron   -- degree per neuron in the populations, encoding the joints angles;
                                                if set: population size depends on joint working range

            return: bool                    -- return True, if successful
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')
        cdef string key = part.encode('UTF-8')
        
        # call the interface
        return my_interface.jointW_init(s, key, n_pop, degr_per_neuron)

    # get the size of the populations encoding the joint angles
    def jointW_get_neurons_per_joint(self, name):
        """
            Calls std::vector<int> iCub_ANN::jointW_get_neurons_per_joint(std::string name)

            params: std::string name        -- name of the selected joint writer

            return: std::vector<int>        -- return vector, containing the population size for every joint
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')

        # call the interface
        return my_interface.jointW_get_neurons_per_joint(s)

    # get the resolution in degree of the populations encoding the joint angles
    def jointW_get_joints_deg_res(self, name):
        """
            Calls std::vector<double> iCub_ANN::jointW_get_joints_deg_res(std::string name)

            params: std::string name        -- name of the selected joint writer

            return: std::vector<double>     -- return vector, containing the resolution for every joints population codimg in degree
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')

        # call the interface
        return my_interface.jointW_get_joints_deg_res(s)

    # write one joint as double value
    def jointW_write_double(self, name, position, joint, blocking):
        """
            Calls bool iCub_ANN::jointW_write_double(std::string name, double position, int joint, bool blocking)

            params: std::string name    -- name of the selected joint writer
                    double position     -- joint angle to write to the robot joint
                    int joint           -- joint number of the robot part
                    bool blocking       -- if True, function waits for end of movement

            return: bool                -- return True, if successful
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')

        cdef bint block = blocking.__int__()

        # call the interface
        return my_interface.jointW_write_double(s, position, joint, block)

    # write one joint with the joint angle encoded in a population vector
    def jointW_write_one(self, name, position_pop, joint, blocking):
        """
            Calls bool iCub_ANN::jointW_write_one(std::string name, std::vector<double> position_pop, int joint, bool blocking)

            params: std::string name        -- name of the selected joint writer
                    std::vector<double>     -- population encoded joint angle for writing to the robot joint
                    int joint               -- joint number of the robot part
                    bool blocking           -- if True, function waits for end of movement

            return: bool                    -- return True, if successful
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')

        cdef bint block = blocking.__int__()

        # call the interface
        return my_interface.jointW_write_one(s, position_pop, joint, block)

    # write all joints with joint angles encoded in populations vectors
    def jointW_write_all(self, name, position_pops, blocking):
        """
            Calls bool iCub_ANN::jointW_write_all(std::string name, std::vector<std::vector<double>> position_pops, bool blocking)

            params: std::string name                    -- name of the selected joint writer
                    std::vector<std::vector<double>>    -- populations encoding every joint angle for writing them to the associated robot part
                    bool blocking                       -- if True, function waits for end of movement

            return: bool                                -- return True, if successful
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')

        cdef bint block = blocking.__int__()

        # call the interface
        return my_interface.jointW_write_all(s, position_pops, block)

    # close joint reader with cleanup
    def jointW_close(self, name):
        """
            Calls iCub_ANN::jointR_close(std::string name)
        
            params: std::string name        -- name of the selected joint writer
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')

        # call the interface
        my_interface.jointW_close(s)
    ### end access to joint writer member functions

    ### Access to skin reader member functions
    # init skin reader with given parameters
    def skinR_init(self, name, arm):
        """
            Calls bool iCub_ANN::skinR_init(std::string name, char arm)

            params: std::string name        -- name of the selected skin reader
                    char arm                -- string representing the robot part, has to match iCub part naming

            return: bool                    -- return True, if successful
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')

        # call the interface
        return my_interface.skinR_init(s, arm)

    # read sensor data
    def skinR_read_tactile(self, name):
        """
            Calls void iCub_ANN::skinR_read_tactile(std::string name)

            params: std::string name        -- name of the selected skin reader
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')

        # call the interface
        my_interface.skinR_read_tactile(s)

    # return tactile data for hand skin
    def skinR_get_tactile_hand(self, name):
        """
            Calls  std::vector<double> iCub_ANN::skinR_get_tactile_hand(std::string name)

            params: std::string name        -- name of the selected skin reader
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')

        # call the interface
        return my_interface.skinR_get_tactile_hand(s)

    # return tactile data for forearm skin
    def skinR_get_tactile_forearm(self, name):
        """
            Calls  std::vector<double> iCub_ANN::skinR_get_tactile_forearm(std::string name)

            params: std::string name        -- name of the selected skin reader
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')

        # call the interface
        return my_interface.skinR_get_tactile_forearm(s)

    # return tactile data for upper arm skin
    def skinR_get_tactile_arm(self, name):
        """
            Calls  std::vector<double> iCub_ANN::skinR_get_tactile_arm(std::string name)

            params: std::string name        -- name of the selected skin reader
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')

        # call the interface
        return my_interface.skinR_get_tactile_arm(s)

    # return the taxel positions given by the ini files
    def skinR_get_taxel_pos(self, name, skin_part):
        """
            Calls  std::vector<std::vector<double>> iCub_ANN::skinR_get_taxel_pos(std::string name, std::string skin_part)

            params: std::string name                    -- name of the selected skin reader
                    std::string skin_part               -- skin part to load the data for ("arm", "forearm", "hand")

            return: std::vector<std::vector<double>>    -- Vector containing taxel positions -> reference frame depending on skin part
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')
        cdef string s1 = skin_part.encode('UTF-8')

        # call the interface
        return my_interface.skinR_get_taxel_pos(s, s1)

    # close and clean skin reader
    def skinR_close(self, name):
        """
            Calls void iCub_ANN::skinR_close(std::string name)

            params: std::string name        -- name of the selected skin reader
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')

        # call the interface
        my_interface.skinR_close(s)

    ### end access to skin reader member functions

