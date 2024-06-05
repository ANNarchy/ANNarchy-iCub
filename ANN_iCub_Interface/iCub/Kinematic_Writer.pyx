# distutils: language = c++
# cython: language_level = 3
# cython: binding=True
# cython: embedsignature=True

"""
   Copyright (C) 2022 Torsten Fietzek; Helge Ülo Dinkelbach

   Kinematic_Writer.pyx is part of the iCub ANNarchy interface

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

from libcpp.memory cimport make_shared
from cython.operator cimport dereference as deref

from .Kinematic_Writer cimport KinematicWriter
from .iCub_Interface cimport ANNiCub_wrapper
from .Module_Base_Class cimport PyModuleBase

import numpy as np

cdef class PyKinematicWriter(PyModuleBase):

    # init method
    def __cinit__(self):
        print("Initialize iCub Interface: Kinematic Writer.")
        self._cpp_kin_writer = make_shared[KinematicWriter]()

    # close method
    def __dealloc__(self):
        print("Close iCub Interface: Kinematic Writer.")
        self._cpp_kin_writer.reset()


    # register kinematic writer module
    def _register(self, name: str, ANNiCub_wrapper iCub):
        """Register Kinematic Writer module at the main wrapper.
            -> For internal use only.

        Parameters
        ----------
        name : str
            name given to the Kinematic Writer
        iCub : ANNiCub_wrapper
            main interface wrapper

        Returns
        -------
        bool
            True/False on Success/Failure
        """
        if deref(self._cpp_kin_writer).getRegister():
            print("[Interface iCub] Kinematic Writer module is already registered!")
            return False
        else:
            if name in iCub._kinematic_writer:
                print("[Interface iCub] Kinematic Writer module name is already used!")
                return False
            iCub._kinematic_writer[name] = self
            self._name = name
            deref(self._cpp_kin_writer).setRegister(1)
            return True

    # unregister kinematic writer module
    def _unregister(self, ANNiCub_wrapper iCub):
        """Unregister Kinematic Writer module at the main wrapper.
            -> For internal use only.

        Parameters
        ----------
        iCub : ANNiCub_wrapper
            main interface wrapper

        Returns
        -------
        bool
            True/False on Success/Failure
        """
        if deref(self._cpp_kin_writer).getRegister():
            deref(self._cpp_kin_writer).setRegister(0)
            iCub._kinematic_writer.pop(self._name, None)
            self._name = ""
            return True
        else:
            print("[Interface iCub] Kinematic Writer module is not yet registered!")
            return False

    def _get_parameter(self):
        return deref(self._cpp_kin_writer).getParameter()


    '''
    # Access to Kinematic writer member functions
    '''

    # init kinematic writer with given parameters
    def init(self, iCub, str name, str part, float version, str ini_path = "../data/", offline_mode=False, active_torso=True):
        """Initialize the Kinematic Writer with given parameters.

        Parameters
        ----------
        iCub : ANNiCub_wrapper
            main interface wrapper
        name : str
            individual name for the kinematic reader
        part : str
            string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso}
        version : float
            version of the robot hardware
        ini_path : str
            path to the interface ini-file. (Default value = "../data/")

        Returns
        -------
        bool
            return True/False, indicating success/failure
        """
        self._part = part
        # preregister module for some prechecks e.g. name already in use
        if self._register(name, iCub):
            retval = deref(self._cpp_kin_writer).Init(part.encode('UTF-8'), version, ini_path.encode('UTF-8'), offline_mode, active_torso)
            if not retval:
                self._unregister(iCub)
            return retval
        else:
            return False

    # init kinematic writer with given parameters, including the gRPC based connection
    def init_grpc(self, iCub, str name, str part, float version, str ini_path = "../data/", str ip_address = "0.0.0.0", unsigned int port = 50025, offline_mode=False, active_torso=True):
        """Initialize the Kinematic Writer with given parameters, including the gRPC based connection.

        Parameters
        ----------
        iCub : ANNiCub_wrapper
            main interface wrapper
        name : str
            individual name for the kinematic reader
        part : str
            string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso}
        version : float
            version of the robot hardware
        ini_path : str
            path to the interface ini-file. (Default value = "../data/")
        ip_address : str
            gRPC server ip address. (Default value = "0.0.0.0")
        port : unsigned int
            gRPC server port. (Default value = 50025)

        Returns
        -------
        bool
            return True/False, indicating success/failure

        """
        self._part = part
        # preregister module for some prechecks e.g. eye already in use
        if self._register(name, iCub):
            retval = deref(self._cpp_kin_writer).InitGRPC(part.encode('UTF-8'), version, ini_path.encode('UTF-8'), ip_address.encode('UTF-8'), port, offline_mode, active_torso)
            if not retval:
                self._unregister(iCub)
            return retval
        else:
            return False

    # close module
    def close(self, iCub):
        """Close the module.

        Parameters
        ----------
        iCub : ANNiCub_wrapper
            main interface wrapper

        Returns
        -------

        """
        self._unregister(iCub)
        self._part = ""
        deref(self._cpp_kin_writer).Close()

    # solve inverse kinematics for given position
    def solve_InvKin(self, position, blocked_links=[]):
        """Compute the joint configuration for a given 3D End-Effector position (Inverse Kinematics).

        Parameters
        ----------
        position : list
            target cartesian position for the end-effector/hand
        blocked_links : list
            links of the kinematic chain, which should be blocked for inverse kinematic, IGNORED in offline mode -> use setter for block links and joint angles

        Returns
        -------
        NDarray
            active joint positions (in radians)
        """
        return np.array(deref(self._cpp_kin_writer).SolveInvKin(position, blocked_links))

    # return DOF of kinematic chain
    def get_DOF(self):
        """Return the DOF of the kinematic chain.

        Parameters
        ----------

        Returns
        -------
        type
            int: DOF of the kinematic chain
        """
        return deref(self._cpp_kin_writer).GetDOF()

    # Get current joint angles
    def get_jointangles(self):
        """Get current joint angles of active kinematic chain -> radians.

        Parameters
        ----------

        Returns
        -------
        NDarray
            joint angles in radians
        """
        return np.array(deref(self._cpp_kin_writer).GetJointAngles())

    # Set joint angles for inverse kinematic in offline mode
    def set_jointangles(self, joint_angles):
        """Set joint angles for forward kinematic in offline mode.

        Parameters
        ----------
        joint_angles : list/NDarray
            joint angles

        Returns
        -------
        NDarray
            actual set joint angles in radians -> evaluted constraints
        """
        return np.array(deref(self._cpp_kin_writer).SetJointAngles(joint_angles))

    # Get blocked links
    def get_blocked_links(self):
        """Get blocked links.

        Parameters
        ----------

        Returns
        -------
        NDarray
            vector containing the blocked links
        """
        return np.array(deref(self._cpp_kin_writer).GetBlockedLinks())

    # Block links
    def block_links(self, blocked_joints):
        """Block specific set of joints in the kinematic chain.

        Parameters
        ----------
        blocked_joints : list
            joints that should be blocked

        Returns
        -------

        """
        deref(self._cpp_kin_writer).BlockLinks(blocked_joints)

    # Get joints being part of active kinematic chain
    def get_DOF_links(self):
        """Get joints being part of active kinematic chain.

        Parameters
        ----------

        Returns
        -------
        NDarray
            vector with the active joints
        """
        return np.array(deref(self._cpp_kin_writer).GetDOFLinks())

    # Release links of kinematic chain
    def release_links(self, release_joints):
        """Release links of kinematic chain

        Parameters
        ----------
        release_joints : list
            joints that should be released

        Returns
        -------

        """
        deref(self._cpp_kin_writer).ReleaseLinks(release_joints)