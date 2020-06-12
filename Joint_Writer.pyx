# distutils: language = c++
# cython: language_level = 3

"""
   Copyright (C) 2020 Torsten Follak; Helge Ülo Dinkelbach

   Joint_Writer.pyx is part of the iCub ANNarchy interface

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   The iCub ANNarchy interface is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this headers. If not, see <http://www.gnu.org/licenses/>.
 """


    ### Access to joint writer member functions
    # initialize the joint writer with given parameters
    def jointW_init(self, name, part, n_pop, degr_per_neuron=0.0, speed=10.0):
        """
            Calls bool iCubANN::JointWInit(std::string name, std::string part, int pop_size, double deg_per_neuron, double speed)

            function:
                Initialize the joint writer with given parameters

            params:
                std::string name        -- name of the selected joint writer
                std::string part        -- string representing the robot part, has to match iCub part naming
                                            {left_(arm/leg), right_(arm/leg), head, torso}
                int pop_size            -- number of neurons per population, encoding each one joint angle;
                                            only works if parameter "deg_per_neuron" is not set
                double deg_per_neuron   -- degree per neuron in the populations, encoding the joints angles;
                                            if set: population size depends on joint working range
                double speed            -- velocity for the joint movements

            return:
                bool                    -- return True, if successful
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')
        cdef string key = part.encode('UTF-8')

        # call the interface
        return my_interface.JointWInit(s, key, n_pop, degr_per_neuron, speed)

    # close joint reader with cleanup
    def jointW_close(self, name):
        """
            Calls iCubANN::JointWClose(std::string name)

            function:
                Close joint reader with cleanup

            params:
                std::string name        -- name of the selected joint writer
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')

        # call the interface
        my_interface.JointWClose(s)

    # return number of controlled joints
    def jointW_get_joint_count(self, name):
        """
            Calls std::vector<double> iCubANN::JointWGetJointCount(std::string name)

            function:
                Return number of controlled joints

            params:
                std::string name        -- name of the selected joint writer

            return:
                int                     -- return number of joints, being controlled by the writer
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')

        # call the interface
        return my_interface.JointWGetJointCount(s)

    # get the resolution in degree of the populations encoding the joint angles
    def jointW_get_joints_deg_res(self, name):
        """
            Calls std::vector<double> iCubANN::JointWGetJointsDegRes(std::string name)

            function:
                Return the resolution in degree of the populations encoding the joint angles

            params:
                std::string name        -- name of the selected joint writer

            return:
                std::vector<double>     -- return vector, containing the resolution for every joints population codimg in degree
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')

        # call the interface
        return np.array(my_interface.JointWGetJointsDegRes(s))

    # get the size of the populations encoding the joint angles
    def jointW_get_neurons_per_joint(self, name):
        """
            Calls std::vector<int> iCubANN::JointWGetNeuronsPerJoint(std::string name)

            function:
                Return the size of the populations encoding the joint angles

            params:
                std::string name        -- name of the selected joint writer

            return:
                std::vector<int>        -- return vector, containing the population size for every joint
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')

        # call the interface
        return np.array(my_interface.JointWGetNeuronsPerJoint(s))

    # set joint velocity
    def jointW_set_joint_velocity(self, name, speed, joint=(-1)):
        """
            Calls bool iCubANN::JointWSetJointVelocity(std::string name, double speed, int joint)

            function:
                Set iCub joint velocity

            params:
                std::string name    -- name of the selected joint writer
                double speed        -- velocity value to be set
                int joint           -- joint number of the robot part, default -1 for all joints

            return:
                bool                -- return True, if successful
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')
        # call the interface
        return my_interface.JointWSetJointVelocity(s, speed, joint)

    # write all joints with double values
    def jointW_write_double_all(self, name, position, mode, blocking=True):
        """
            Calls bool iCubANN::JointWWriteDoubleAll(std::string name, std::vector<double> position, bool blocking, std::string mode)

            function:
                Write all joints with double values

            params:
                std::string name                -- name of the selected joint writer
                std::vector<double> position    -- joint angles to write to the robot joints
                bool blocking                   -- if True, function waits for end of motion; default True
                std::string mode                -- string to select the motion mode: possible are 'abs' for absolute joint angle positions and 'rel' for relative joint angles

            return:
                bool                            -- return True, if successful
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')
        cdef string s1 = mode.encode('UTF-8')

        cdef bint block = blocking.__int__()

        # call the interface
        return my_interface.JointWWriteDoubleAll(s,  position, block, s1)

    # write all joints with double values
    def jointW_write_double_multiple(self, name, position, joints, mode, blocking=True):
        """
            Calls bool JointWWriteDoubleMultiple(std::string name, std::vector<double> position, std::vector<int> joint_selection, bool blocking, std::string mode);

            function:
                Write all joints with double values

            params:
                std::string name                -- name of the selected joint writer
                std::vector<double> position    -- joint angles to write to the robot joints
                std::vector<int> joints         -- Joint indizes of the joints, which should be moved (head: [3, 4, 5] -> all eye movements)
                bool blocking                   -- if True, function waits for end of motion; default True
                std::string mode                -- string to select the motion mode: possible are 'abs' for absolute joint angle positions and 'rel' for relative joint angles

            return:
                bool                            -- return True, if successful
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')
        cdef string s1 = mode.encode('UTF-8')

        cdef bint block = blocking.__int__()

        # call the interface
        return my_interface.JointWWriteDoubleMultiple(s,  position,  joints, block, s1)


    # write one joint with double value
    def jointW_write_double_one(self, name, position, joint, mode, blocking=True):
        """
            Calls bool iCubANN::JointWWriteDouble(std::string name, double position, int joint, bool blocking, std::string mode)

            function:
                Write one joint with double value

            params:
                std::string name    -- name of the selected joint writer
                double position     -- joint angle to write to the robot joint
                int joint           -- joint number of the robot part
                bool blocking       -- if True, function waits for end of motion; default True
                std::string mode    -- string to select the motion mode: possible are 'abs' for absolute joint angle positions and 'rel' for relative joint angles

            return:
                bool                -- return True, if successful
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')
        cdef string s1 = mode.encode('UTF-8')

        cdef bint block = blocking.__int__()

        # call the interface
        return my_interface.JointWWriteDoubleOne(s, position, joint, block, s1)

    # write all joints with joint angles encoded in populations vectors
    def jointW_write_pop_all(self, name, position_pops, mode, blocking=True):
        """
            Calls bool iCubANN::JointWWritePopAll(std::string name, std::vector<std::vector<double>> position_pops, bool blocking, std::string mode)

            function:
                Write all joints with joint angles encoded in populations vectors

            params:
                std::string name                    -- name of the selected joint writer
                std::vector<std::vector<double>>    -- populations encoding every joint angle for writing them to the associated robot part
                bool blocking                       -- if True, function waits for end of motion; default True
                std::string mode                -- string to select the motion mode: possible are 'abs' for absolute joint angle positions and 'rel' for relative joint angles

            return:
                bool                                -- return True, if successful
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')
        cdef string s1 = mode.encode('UTF-8')

        cdef bint block = blocking.__int__()

        # call the interface
        return my_interface.JointWWritePopAll(s,  position_pops, block, s1)

    # write multiple joints with joint angles encoded in populations vectors
    def jointW_write_pop_multiple(self, name, position_pops, joints, mode, blocking=True):
        """
            Calls bool JointWWritePopMultiple(std::string name, std::vector<std::vector<double>> position_pops, std::vector<int> joint_selection, bool blocking, std::string mode);

            function:
                Write all joints with joint angles encoded in populations vectors

            params:
                std::string name                    -- name of the selected joint writer
                std::vector<std::vector<double>>    -- populations encoding every joint angle for writing them to the associated robot part
                std::vector<int> joints             -- Joint indizes of the joints, which should be moved (head: [3, 4, 5] -> all eye movements)
                bool blocking                       -- if True, function waits for end of motion; default True
                std::string mode                    -- string to select the motion mode: possible are 'abs' for absolute joint angle positions and 'rel' for relative joint angles

            return:
                bool                                -- return True, if successful
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')
        cdef string s1 = mode.encode('UTF-8')

        cdef bint block = blocking.__int__()

        # call the interface
        return my_interface.JointWWritePopMultiple(s, position_pops, joints, block, s1)

    # write one joint with the joint angle encoded in a population vector
    def jointW_write_pop_one(self, name, position_pop, joint, mode, blocking=True):
        """
            Calls bool iCubANN::JointWWritePopOne(std::string name, std::vector<double> position_pop, int joint, bool blocking, std::string mode)

            function:
                Write one joint with the joint angle encoded in a population vector

            params:
                std::string name        -- name of the selected joint writer
                std::vector<double>     -- population encoded joint angle for writing to the robot joint
                int joint               -- joint number of the robot part
                bool blocking           -- if True, function waits for end of motion; default True
                std::string mode                -- string to select the motion mode: possible are 'abs' for absolute joint angle positions and 'rel' for relative joint angles

            return:
                bool                    -- return True, if successful
        """
        # we need to transform py-string to c++ compatible string
        cdef string s = name.encode('UTF-8')
        cdef string s1 = mode.encode('UTF-8')

        cdef bint block = blocking.__int__()

        # call the interface
        return my_interface.JointWWritePopOne(s,  position_pop, joint, block, s1)

    ### end access to joint writer member functions