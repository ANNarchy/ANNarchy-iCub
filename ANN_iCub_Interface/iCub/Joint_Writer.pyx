# distutils: language = c++
# cython: language_level = 3
# cython: binding=True
# cython: embedsignature=True

"""
   Copyright (C) 2019-2023 Torsten Fietzek; Helge Ülo Dinkelbach

   Joint_Writer.pyx is part of the ANNarchy iCub interface

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   The ANNarchy iCub interface is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this headers. If not, see <http://www.gnu.org/licenses/>.
 """

import numpy as np

from libcpp.string cimport string
from libcpp.memory cimport make_shared
from cython.operator cimport dereference as deref

from .Joint_Writer cimport JointWriter
from .iCub_Interface cimport ANNiCub_wrapper


cdef class PyJointWriter:
    """Wrapper class for Joint Writer module."""

    # constructor method
    def __cinit__(self):
        print("Initialize iCub Interface: Joint Writer.")
        self._cpp_joint_writer = make_shared[JointWriter]()

    # destructor method
    def __dealloc__(self):
        print("Close iCub Interface: Joint Writer.")
        self._cpp_joint_writer.reset()

    '''
    # Access to joint writer member functions
    '''

    # initialize the joint writer with given parameters
    def init(self, ANNiCub_wrapper iCub, str name, str part, unsigned int n_pop, double degr_per_neuron=0.0, double speed=10.0, str ini_path="../data/"):
        """Initialize the joint writer with given parameters.

        Parameters
        ----------
        iCub : ANNiCub_wrapper
            main interface wrapper
        name : str
            name for the joint writer module
        part : str
            string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso}
        n_pop : unsigned int
            number of neurons per population, encoding each one joint angle;
            only works if parameter "deg_per_neuron" is not set
        degr_per_neuron : double
            degree per neuron in the populationencoding the joints angles;
            if set: population size depends on joint working range. (Default value = 0.0)
        speed : double
            velocity for the joint movements. (Default value = 10.0)
        ini_path : str
            Path to the "interface_param.ini"-file. (Default value = "../data/")

        Returns
        -------
        bool
            return True/False, indicating success/failure
        """
        # we need to transform py-string to c++ compatible string
        cdef string key = part.encode('UTF-8')
        cdef string path = ini_path.encode('UTF-8')

        self._part = part
        # preregister module for some prechecks e.g. part already in use
        if iCub.register_jwriter(name, self):
            retval = deref(self._cpp_joint_writer).Init(key, n_pop, degr_per_neuron, speed, path)
            if not retval:
                iCub.unregister_jwriter(self)
            return retval
        else:
            return False

    # Initialize the joint writer with given parameters for use with gRPC
    def init_grpc(self, ANNiCub_wrapper iCub, str name, str part, unsigned int n_pop, joints, str mode, blocking=True, double degr_per_neuron=0.0,
                  double speed=10.0, str ini_path="../data/", str ip_address="0.0.0.0", unsigned int port=50010):
        """Initialize the joint writer with given parameters, including the gRPC based connection.

        Parameters
        ----------
        iCub : ANNiCub_wrapper
            main interface wrapper
        name : str
            name for the joint writer module
        part : str
            string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso}
        n_pop : unsigned int
            number of neurons per population, encoding each one joint angle;
            only works if parameter "deg_per_neuron" is not set
        joints : list (vector[int]
            joint selection for grpc -> empty vector for all joints
        mode : str
            mode for writing joints:
            - 'abs' for absolute joint angle positions
            - 'rel' for relative joint angles
            - 'vel' for velocity values -> DO NOT USE AS BLOCKING MOTION!!!
        blocking : bool
            if True, complete motion before continuation. (Default value = True)
        degr_per_neuron : double
            degree per neuron in the populationencoding the joints angles;
            if set: population size depends on joint working range. (Default value = 0.0)
        speed : double
            velocity for the joint movements. (Default value = 10.0)
        ini_path : str
            Path to the "interface_param.ini"-file. (Default value = "../data/")
        ip_address : str
            gRPC server ip address. (Default value = "0.0.0.0")
        port : unsigned int
            gRPC server port. (Default value = 50010)

        Returns
        -------
        bool
            return True/False, indicating success/failure
        """
        self._part = part
        # preregister module for some prechecks e.g. part already in use
        if iCub.register_jwriter(name, self):
            retval = deref(self._cpp_joint_writer).InitGRPC(part.encode('UTF-8'), n_pop, joints, mode.encode('UTF-8'), blocking.__int__(), degr_per_neuron,
                                                            speed, ini_path.encode('UTF-8'), ip_address.encode('UTF-8'), port)
            if not retval:
                iCub.unregister_jwriter(self)
            return retval
        else:
            return False

    # close joint writer with cleanup
    def close(self, ANNiCub_wrapper iCub):
        """Close joint writer with cleanup

        Parameters
        ----------
        iCub : ANNiCub_wrapper
            main interface wrapper

        Returns
        -------

        """
        iCub.unregister_jwriter(self)
        self._part = ""
        deref(self._cpp_joint_writer).Close()

    # return number of controlled joints
    def get_joint_count(self):
        """Return number of controlled joints

        Parameters
        ----------

        Returns
        -------
        type
            int: return number of joints being controlled by the joint writer
        """
        return deref(self._cpp_joint_writer).GetJointCount()

    # get the resolution in degree of the populations encoding the joint angles
    def get_joints_deg_res(self):
        """Return the resolution in degree of the populations encoding the joint angles

        Parameters
        ----------

        Returns
        -------
        type
            NDarray (vetor[double]): return vector, containing the resolution for every joints population codimg in degree
        """
        return np.array(deref(self._cpp_joint_writer).GetJointsDegRes())

    # get the size of the populations encoding the joint angles
    def get_neurons_per_joint(self):
        """Return the size of the populations encoding the joint angles

        Parameters
        ----------

        Returns
        -------
        type
            NDarray (vector[int]): return vector, containing the population size for every joint
        """
        return np.array(deref(self._cpp_joint_writer).GetNeuronsPerJoint())

    # Return the limits of joint angles in degree.
    def get_joint_limits(self):
        """Return the limits of joint angles in degree

        Parameters
        ----------

        Returns
        -------
        type
            NDarray (vector[vector[double]]): return array, containing the limits of joint angles in degree (joint, (max, min))
        """
        return np.array(deref(self._cpp_joint_writer).GetJointLimits())

    # Return the upper limits of joint angles in degree.
    def get_joint_limits_max(self):
        """Return the upper limits of joint angles in degree

        Parameters
        ----------

        Returns
        -------
        type
            NDarray (vector[double]): return vector, containing the upper limits of joint angles in degree (joint, max)
        """
        return np.array(deref(self._cpp_joint_writer).GetJointLimitsMax())

    # Return the lower limits of joint angles in degree.
    def get_joint_limits_min(self):
        """Return the lower limits of joint angles in degree

        Parameters
        ----------

        Returns
        -------
        type
            NDarray (vector[double]): return vector, containing the lower limits of joint angles in degree (joint, min)
        """
        return np.array(deref(self._cpp_joint_writer).GetJointLimitsMin())

    # set joint velocity
    def set_joint_velocity(self, double speed, int joint=-1):
        """Set joint velocity.

        Parameters
        ----------
        speed : double
            velocity value to be set
        joint : int
            joint number of the robot part or -1 for all joints. (Default value = -1)

        Returns
        -------
        bool
            return True/False, indicating success/failure
        """
        return deref(self._cpp_joint_writer).SetJointVelocity(speed, joint)

    # set joint acceleration
    def set_joint_acceleration(self, double acc, int joint=-1):
        """Set joint acceleration.

        Parameters
        ----------
        acc : double
            acceleration value to be set
        joint : int
            joint number of the robot part or -1 for all joints. (Default value = -1)

        Returns
        -------
        bool
            return True/False, indicating success/failure
        """
        return deref(self._cpp_joint_writer).SetJointAcceleration(acc, joint)

    # Set the control mode for the respective joint/Joints -> e.g. position or velocity
    def set_joint_controlmode(self, str control_mode, int joint=-1):
        """Set joint control mode

        Parameters
        ----------
        control_mode : str
            control mode for the joint. currently implemented are: "velocity" and "position"
        joint : int
            joint number of the robot part or -1 for all joints. (Default value = -1)

        Returns
        -------
        bool
            return True/False, indicating success/failure
        """
        # we need to transform py-string to c++ compatible string
        cdef string s1 = control_mode.encode('UTF-8')
        return deref(self._cpp_joint_writer).SetJointControlMode(s1, joint)

    # write all joints with double values
    def write_double_all(self, position, str mode, blocking=True, timeout=0):
        """Move all joints to the given positiion (joint angles/velocities).

        Parameters
        ----------
        position : list/NDarray (vector[double]
            joint angles/velocities to write to the robot joints
        mode : str
            string to select the motion mode:
            - 'abs' for absolute joint angle positions
            - 'rel' for relative joint angles
            - 'vel' for velocity values -> DO NOT USE AS BLOCKING MOTION!!!
        blocking : bool
            if True, complete motion before continuation. (Default value = True)

        Returns
        -------
        bool
            return True/False, indicating success/failure
        """
        # we need to transform py-string to c++ compatible string
        cdef string s1 = mode.encode('UTF-8')
        # we need to transform py-bool to c++ compatible boolean
        cdef bint block = blocking.__int__()
        return deref(self._cpp_joint_writer).WriteDoubleAll(position, s1, block, timeout)

    # write all joints with double values
    def write_double_multiple(self, position, joints, str mode, blocking=True, timeout=0):
        """Move multiple joints to the given positiion (joint angles/velocities).

        Parameters
        ----------
        position : list/NDarray (vector[double]
            joint angles/velocities to write to the robot joints
        joints : list/NDarray (vector[int]
            joint indizes of the joints, which should be moved (e.g. head: [3, 4, 5] -> all eye movements)
        mode : str
            string to select the motion mode:
            - 'abs' for absolute joint angle positions
            - 'rel' for relative joint angles
            - 'vel' for velocity values -> DO NOT USE AS BLOCKING MOTION!!!
        blocking : bool
            if True, complete motion before continuation. (Default value = True)

        Returns
        -------
        bool
            return True/False, indicating success/failure
        """
        # we need to transform py-string to c++ compatible string
        cdef string s1 = mode.encode('UTF-8')
        # we need to transform py-bool to c++ compatible boolean
        cdef bint block = blocking.__int__()
        return deref(self._cpp_joint_writer).WriteDoubleMultiple(position, joints, s1, block, timeout)

    # write one joint with double value
    def write_double_one(self, double position, int joint, str mode, blocking=True, timeout=0):
        """Move single joint to the given positiion (joint angle/velocity).

        Parameters
        ----------
        position : double
            joint angle/velocity to write to the robot joint
        joint : int
            joint number of the robot part
        mode : str
            string to select the motion mode:
            - 'abs' for absolute joint angle positions
            - 'rel' for relative joint angles
            - 'vel' for velocity values -> DO NOT USE AS BLOCKING MOTION!!!
        blocking : bool
            if True, complete motion before continuation. (Default value = True)

        Returns
        -------
        bool
            return True/False, indicating success/failure
        """
        # we need to transform py-string to c++ compatible string
        cdef string s1 = mode.encode('UTF-8')
        # we need to transform py-bool to c++ compatible boolean
        cdef bint block = blocking.__int__()
        return deref(self._cpp_joint_writer).WriteDoubleOne(position, joint, s1, block, timeout)

    # write all joints with joint angles encoded in populations vectors
    def write_pop_all(self, position_pops, str mode, blocking=True, timeout=0):
        """Move all joints to the joint angles/velocities encoded in the given vector of populations.

        Parameters
        ----------
        position_pops : NDarray (vector[vector[double]]
            vector of populations, each encoding the angle/velocity for a single joint
        mode : str
            string to select the motion mode:
            - 'abs' for absolute joint angle positions
            - 'rel' for relative joint angles
            - 'vel' for velocity values -> DO NOT USE AS BLOCKING MOTION!!!
        blocking : bool
            if True, complete motion before continuation. (Default value = True)

        Returns
        -------
        bool
            return True/False, indicating success/failure
        """
        # we need to transform py-string to c++ compatible string
        cdef string s1 = mode.encode('UTF-8')
        # we need to transform py-bool to c++ compatible boolean
        cdef bint block = blocking.__int__()
        return deref(self._cpp_joint_writer).WritePopAll(position_pops, s1, block, timeout)

    # write multiple joints with joint angles encoded in populations vectors
    def write_pop_multiple(self, position_pops, joints, str mode, blocking=True, timeout=0):
        """Move multiple joints to the joint angles/velocities encoded in the given vector of populations.

        Parameters
        ----------
        position_pops : NDarray (vector[vector[double]]
            vector of populations, each encoding the angle/velocity for a single joint
        joints : list/NDarray (vector[int]
            Joint indizes of the joints, which should be moved (head: [3, 4, 5] -> all eye movements)
        mode : str
            string to select the motion mode:
            - 'abs' for absolute joint angle positions
            - 'rel' for relative joint angles
            - 'vel' for velocity values -> DO NOT USE AS BLOCKING MOTION!!!
        blocking : bool
            if True, complete motion before continuation. (Default value = True)

        Returns
        -------
        bool
            return True/False, indicating success/failure
        """
        # we need to transform py-string to c++ compatible string
        cdef string s1 = mode.encode('UTF-8')
        # we need to transform py-bool to c++ compatible boolean
        cdef bint block = blocking.__int__()
        return deref(self._cpp_joint_writer).WritePopMultiple(position_pops, joints, s1, block, timeout)

    # write one joint with the joint angle encoded in a population vector
    def write_pop_one(self, position_pop, int joint, str mode, blocking=True, timeout=0):
        """Move a single joint to the joint angle/velocity encoded in the given population.

        Parameters
        ----------
        position_pop : NDarray (vector[double]
            population encoding the joint angle/velocity
        joint : int
            joint number of the robot part
        mode : str
            string to select the motion mode:
            - 'abs' for absolute joint angle positions
            - 'rel' for relative joint angles
            - 'vel' for velocity values -> DO NOT USE AS BLOCKING MOTION!!!
        blocking : bool
            if True, complete motion before continuation. (Default value = True)

        Returns
        -------
        bool
            return True/False, indicating success/failure
        """
        # we need to transform py-string to c++ compatible string
        cdef string s1 = mode.encode('UTF-8')
        # we need to transform py-bool to c++ compatible boolean
        cdef bint block = blocking.__int__()
        return deref(self._cpp_joint_writer).WritePopOne(position_pop, joint, s1, block, timeout)

    '''
    # gRPC related methods
    '''

    # retrieve single joint angle from specialized gRPC-connected ANNarchy-JointControl-Population
    def retrieve_ANNarchy_input_single(self):
        """Retrieve single joint angle from specialized gRPC-connected ANNarchy-JointControl-Population."""
        deref(self._cpp_joint_writer).Retrieve_ANNarchy_Input_SJ()

    # write single joint with retrieved joint angle
    def write_ANNarchy_input_single(self):
        """Write single joint with retrieved joint angle."""
        deref(self._cpp_joint_writer).Write_ANNarchy_Input_SJ()

    # retrieve single population encoded joint angle from specialized gRPC-connected ANNarchy-JointControl-Population
    def retrieve_ANNarchy_input_single_enc(self):
        """Retrieve single population encoded joint angle from specialized gRPC-connected ANNarchy-JointControl-Population."""
        deref(self._cpp_joint_writer).Retrieve_ANNarchy_Input_SJ_enc()

    # write single joint with retrieved population encoded joint angle
    def write_ANNarchy_input_single_enc(self):
        """Write single joint with retrieved population encoded joint angle."""
        deref(self._cpp_joint_writer).Write_ANNarchy_Input_SJ_enc()

    # retrieve multiple joint angles from specialized gRPC-connected ANNarchy-JointControl-Population
    def retrieve_ANNarchy_input_multi(self):
        """Retrieve multiple joint angles from specialized gRPC-connected ANNarchy-JointControl-Population."""
        deref(self._cpp_joint_writer).Retrieve_ANNarchy_Input_MJ()

    # write multiple joints with retrieved joint angles
    def write_ANNarchy_input_multi(self):
        """Write multiple joints with retrieved joint angles."""
        deref(self._cpp_joint_writer).Write_ANNarchy_Input_MJ()

    # retrieve multiple population encoded joint angles from specialized gRPC-connected ANNarchy-JointControl-Population
    def retrieve_ANNarchy_input_multi_enc(self):
        """Retrieve multiple population encoded joint angles from specialized gRPC-connected ANNarchy-JointControl-Population."""
        deref(self._cpp_joint_writer).Retrieve_ANNarchy_Input_MJ_enc()

    # write multiple joints with retrieved population encoded joint angles
    def write_ANNarchy_input_multi_enc(self):
        """Write multiple joints with retrieved population encoded joint angles."""
        deref(self._cpp_joint_writer).Write_ANNarchy_Input_MJ_enc()

    # retrieve all joint angles from specialized gRPC-connected ANNarchy-JointControl-Population
    def retrieve_ANNarchy_input_all(self):
        """Retrieve all joint angles from specialized gRPC-connected ANNarchy-JointControl-Population."""
        deref(self._cpp_joint_writer).Retrieve_ANNarchy_Input_AJ()

    # write all joints with retrieved joint angles
    def write_ANNarchy_input_all(self):
        """Write all joints with retrieved joint angles."""
        deref(self._cpp_joint_writer).Write_ANNarchy_Input_AJ()

    # retrieve all population encoded joint angles from specialized gRPC-connected ANNarchy-JointControl-Population
    def retrieve_ANNarchy_input_all_enc(self):
        """Retrieve all population encoded joint angles from specialized gRPC-connected ANNarchy-JointControl-Population."""
        deref(self._cpp_joint_writer).Retrieve_ANNarchy_Input_AJ_enc()

    # write all joints with retrieved population encoded joint angles
    def write_ANNarchy_input_all_enc(self):
        """Write all joints with retrieved population encoded joint angles."""
        deref(self._cpp_joint_writer).Write_ANNarchy_Input_AJ_enc()

    '''
    # Helper methods for debugging purposes
    '''

    # decode position with internal method
    def decode(self, position_pop, int joint):
        return deref(self._cpp_joint_writer).Decode_ext(position_pop, joint)
