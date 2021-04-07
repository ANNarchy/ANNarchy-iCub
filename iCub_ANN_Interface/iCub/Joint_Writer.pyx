# distutils: language = c++
# cython: language_level = 3
# cython: profile=True

"""
   Copyright (C) 2019-2021 Torsten Fietzek; Helge Ülo Dinkelbach

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

from libcpp.string cimport string
from libcpp.vector cimport vector
from libcpp.memory cimport shared_ptr, make_shared
from cython.operator cimport dereference as deref

from .Joint_Writer cimport JointWriter
from .iCub_Interface cimport iCubANN_wrapper

import numpy as np

cdef class PyJointWriter:

    # init method
    def __cinit__(self):
        print("Initialize iCub Interface: Joint Writer.")
        self.cpp_joint_writer = make_shared[JointWriter]()

    # close method
    def __dealloc__(self):
        print("Close iCub Interface: Joint Writer.")
        self.cpp_joint_writer.reset()

    ### Access to joint writer member functions
    # initialize the joint writer with given parameters
    def init(self, iCubANN_wrapper iCub, str name, str part, int n_pop, double degr_per_neuron=0.0, double speed=10.0, str ini_path = "../data/"):
        """
            Calls bool JointWriter::Init(std::string part, int pop_size, double deg_per_neuron, double speed)

            function:
                Initialize the joint writer with given parameters

            params:
                iCubANN_wrapper iCub    -- main interface wrapper  
                str name                -- name for the joint writer module  
                std::string part        -- string representing the robot part, has to match iCub part naming<br>
                                            {left_(arm/leg), right_(arm/leg), head, torso}<br>
                int pop_size            -- number of neurons per population, encoding each one joint angle;<br>
                                            only works if parameter "deg_per_neuron" is not set<br>
                double deg_per_neuron   -- degree per neuron in the populationencoding the joints angles;<br>
                                            if set: population size depends on joint working range<br>
                double speed            -- velocity for the joint movements<br>
                ini_path                -- Path to the "interface_param.ini"-file<br>

            return:
                bool                    -- return True, if successful
        """
        # we need to transform py-string to c++ compatible string
        cdef string key = part.encode('UTF-8')
        cdef string path = ini_path.encode('UTF-8')

        self.part = part
        # preregister module for some prechecks e.g. part already in use
        if iCub.register_jwriter(name, self):
            retval = deref(self.cpp_joint_writer).Init(key, n_pop, degr_per_neuron, speed, path)
            if not retval:
                iCub.unregister_jwriter(self)
            return retval
        else:
            return False


    # close joint writer with cleanup
    def close(self, iCubANN_wrapper iCub):
        """
            Calls JointWriter::Close()

            function:
                Close joint writer with cleanup

            params:
                iCubANN_wrapper iCub    -- main interface wrapper
        """

        iCub.unregister_jwriter(self)

        # call the interface
        deref(self.cpp_joint_writer).Close()
        self.part = ""

    # return number of controlled joints
    def get_joint_count(self):
        """
            Calls std::vector<double> JointWriter::GetJointCount()

            function:
                Return number of controlled joints

            return:
                int     -- return number of jointbeing controlled by the writer
        """

        # call the interface
        return deref(self.cpp_joint_writer).GetJointCount()

    # get the resolution in degree of the populations encoding the joint angles
    def get_joints_deg_res(self):
        """
            Calls std::vector<double> JointWriter::GetJointsDegRes()

            function:
                Return the resolution in degree of the populations encoding the joint angles

            return:
                std::vector<double>     -- return vector, containing the resolution for every joints population codimg in degree
        """

        # call the interface
        return np.array(deref(self.cpp_joint_writer).GetJointsDegRes())

    # get the size of the populations encoding the joint angles
    def get_neurons_per_joint(self):
        """
            Calls std::vector<int> JointWriter::GetNeuronsPerJoint()

            function:
                Return the size of the populations encoding the joint angles

            return:
                std::vector<int>        -- return vector, containing the population size for every joint
        """
        # we need to transform py-string to c++ compatible string

        # call the interface
        return np.array(deref(self.cpp_joint_writer).GetNeuronsPerJoint())

    # set joint velocity
    def set_joint_velocity(self, double speed, int joint=(-1)):
        """
            Calls bool JointWriter::SetJointVelocity(double speed, int joint)

            function:
                Set iCub joint velocity

            params:
                double speed        -- velocity value to be set
                int joint           -- joint number of the robot part, default -1 for all joints

            return:
                bool                -- return True, if successful
        """

        # call the interface
        return deref(self.cpp_joint_writer).SetJointVelocity(speed, joint)

    def set_joint_controlmode(self, str control_mode, int joint=(-1)):
        """
            Calls bool JointWriter::SetJointControlMode(string control_mode, int joint)

            function:
                Set iCub joint velocity

            params:
                string control_mode -- control mode: velocity/position
                int joint           -- joint number of the robot part, default -1 for all joints

            return:
                bool                -- return True, if successful
        """
        cdef string s1 = control_mode.encode('UTF-8')

        # call the interface
        return deref(self.cpp_joint_writer).SetJointControlMode(s1, joint)

    # write all joints with double values
    def write_double_all(self, position, str mode, blocking=True):
        """
            Calls bool JointWriter::WriteDoubleAll(std::vector<double> position, bool blocking, std::string mode)

            function:
                Write all joints with double values

            params:
                std::vector<double> position    -- joint angles to write to the robot joints
                bool blocking                   -- if True, function waits for end of motion; default True
                std::string mode                -- string to select the motion mode:
                                                    - 'abs' for absolute joint angle positions
                                                    - 'rel' for relative joint angles

            return:
                bool                            -- return True, if successful
        """

        # we need to transform py-string to c++ compatible string
        cdef string s1 = mode.encode('UTF-8')

        cdef bint block = blocking.__int__()

        # call the interface
        return deref(self.cpp_joint_writer).WriteDoubleAll(position, block, s1)

    # write all joints with double values
    def write_double_multiple(self, position, joints, str mode, blocking=True):
        """
            Calls bool JointWriter::WriteDoubleMultiple(std::vector<double> position, std::vector<int> joint_selection, bool blocking, std::string mode);

            function:
                Write all joints with double values

            params:
                std::vector<double> position    -- joint angles to write to the robot joints
                std::vector<int> joints         -- Joint indizes of the jointwhich should be moved (head: [3, 4, 5] -> all eye movements)
                bool blocking                   -- if True, function waits for end of motion; default True
                std::string mode                -- string to select the motion mode:
                                                    - 'abs' for absolute joint angle positions
                                                    - 'rel' for relative joint angles
            return:
                bool                            -- return True, if successful
        """
        # we need to transform py-string to c++ compatible string
        cdef string s1 = mode.encode('UTF-8')

        cdef bint block = blocking.__int__()

        # call the interface
        return deref(self.cpp_joint_writer).WriteDoubleMultiple(position, joints, block, s1)


    # write one joint with double value
    def write_double_one(self, position, int joint, str mode, blocking=True):
        """
            Calls bool JointWriter::WriteDouble(double position, int joint, bool blocking, std::string mode)

            function:
                Write one joint with double value

            params:
                double position     -- joint angle to write to the robot joint
                int joint           -- joint number of the robot part
                bool blocking       -- if True, function waits for end of motion; default True
                std::string mode    -- string to select the motion mode:
                                        - 'abs' for absolute joint angle position
                                        - 'rel' for relative joint angle
                                        - 'vel' for velocity values -> DO NOT USE AS BLOCKING MOTION!!!

            return:
                bool                -- return True, if successful
        """
        # we need to transform py-string to c++ compatible string
        cdef string s1 = mode.encode('UTF-8')

        cdef bint block = blocking.__int__()

        # call the interface
        return deref(self.cpp_joint_writer).WriteDoubleOne(position, joint, block, s1)

    # write all joints with joint angles encoded in populations vectors
    def write_pop_all(self, position_pops, str mode, blocking=True):
        """
            Calls bool JointWriter::WritePopAll(std::string std::vector<std::vector<double>> position_popbool blocking, std::string mode)

            function:
                Write all joints with joint angles encoded in populations vectors

            params:
                                std::vector<std::vector<double>>    -- populations encoding every joint angle for writing them to the associated robot part
                bool blocking                       -- if True, function waits for end of motion; default True
                std::string mode                -- string to select the motion mode: possible are 'abs' for absolute joint angle positions and 'rel' for relative joint angles

            return:
                bool                                -- return True, if successful
        """
        # we need to transform py-string to c++ compatible string
        cdef string s1 = mode.encode('UTF-8')

        cdef bint block = blocking.__int__()

        # call the interface
        return deref(self.cpp_joint_writer).WritePopAll(position_pops, block, s1)

    # write multiple joints with joint angles encoded in populations vectors
    def write_pop_multiple(self, position_pops, joints, str mode, blocking=True):
        """
            Calls bool WritePopMultiple(std::vector<std::vector<double>> position_pops, std::vector<int> joint_selection, bool blocking, std::string mode);

            function:
                Write all joints with joint angles encoded in populations vectors

            params:
                std::vector<std::vector<double>>    -- populations encoding every joint angle for writing them to the associated robot part
                std::vector<int> joints             -- Joint indizes of the jointwhich should be moved (head: [3, 4, 5] -> all eye movements)
                bool blocking                       -- if True, function waits for end of motion; default True
                std::string mode                    -- string to select the motion mode: possible are 'abs' for absolute joint angle positions and 'rel' for relative joint angles

            return:
                bool                                -- return True, if successful
        """
        # we need to transform py-string to c++ compatible string
        cdef string s1 = mode.encode('UTF-8')

        cdef bint block = blocking.__int__()

        # call the interface
        return deref(self.cpp_joint_writer).WritePopMultiple(position_pops, joints, block, s1)

    # write one joint with the joint angle encoded in a population vector
    def write_pop_one(self, position_pop, int joint, str mode, blocking=True):
        """
            Calls bool JointWriter::WritePopOne(std::vector<double> position_pop, int joint, bool blocking, std::string mode)

            function:
                Write one joint with the joint angle encoded in a population vector

            params:
                std::vector<double>     -- population encoded joint angle for writing to the robot joint
                int joint               -- joint number of the robot part
                bool blocking           -- if True, function waits for end of motion; default True
                std::string mode        -- string to select the motion mode: possible are 'abs' for absolute joint angle positions and 'rel' for relative joint angles

            return:
                bool                    -- return True, if successful
        """
        # we need to transform py-string to c++ compatible string
        cdef string s1 = mode.encode('UTF-8')

        cdef bint block = blocking.__int__()

        # call the interface
        return deref(self.cpp_joint_writer).WritePopOne(position_pop, joint, block, s1)

    # decode position with internal method
    def decode(self, position_pop, int joint):
        # call the interface
        return deref(self.cpp_joint_writer).Decode_ext(position_pop, joint)
    
    ### end access to joint writer member functions