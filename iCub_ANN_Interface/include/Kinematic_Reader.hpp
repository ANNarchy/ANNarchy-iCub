/*
 *  Copyright (C) 2019-2021 Torsten Fietzek
 *
 *  Joint_Reader.hpp is part of the iCub ANNarchy interface
 *
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  The iCub ANNarchy interface is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this headers. If not, see <http://www.gnu.org/licenses/>.
 */

#pragma once

#include <iCub/iKin/iKinFwd.h>      // iCub forward Kinematics
#include <iCub/iKin/iKinIpOpt.h>    // iCub inverse Kinematics
#include <yarp/dev/all.h>
#include <yarp/sig/all.h>

#include <map>
#include <string>
#include <thread>
#include <vector>

#include "Module_Base_Class.hpp"
#ifdef _USE_GRPC
#include "ProvideInputServer.h"
#endif

/**
 * \brief  Read-out of the joint angles of the iCub robot
 */
class KinematicReader : public Mod_BaseClass {
 public:
    // Constructor
    KinematicReader() = default;
    // Destructor
    ~KinematicReader();

    /*** public methods for the user ***/

    /**
     * \brief Initialize the joint reader with given parameters
     * \param[in] part A string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso}.
     * \param[in] version
     * \param[in] ini_path Path to the "interface_param.ini"-file.
     * \return True, if the initializatiion was successful. False if an error occured. Additionally, an error message is written to the error stream (cerr).\n
     *          Typical errors:
     *              - arguments not valid: e.g. part string not correct or ini file not in given path \n
     *              - YARP-Server not running
     */
    bool Init(std::string part, float version, std::string ini_path);

    /**
     * \brief Initialize the joint reader with given parameters
     * \param[in] part A string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso}.
     * \param[in] version
     * \param[in] ini_path Path to the "interface_param.ini"-file.
     * \param[in] ip_address gRPC server ip address -> has to match ip address of the JointReadOut-Population
     * \param[in] port gRPC server port -> has to match port of the JointReadOut-Population
     * \return True, if the initializatiion was successful. False if an error occured. Additionally, an error message is written to the error stream (cerr).\n
     *          Typical errors:
     *              - arguments not valid: e.g. part string not correct or ini file not in given path \n
     *              - YARP-Server not running
     */
    bool InitGRPC(std::string part, float version, std::string ini_path, std::string ip_address, unsigned int port);

    /**
     * \brief  Close joint reader with cleanup
     */
    void Close() override;

    /**
     * \brief  Return number of controlled joints
     * \return Number of joints, being controlled by the reader
     */
    int GetDOF();

    /**
     * \brief Compute 3D link position for the robot joint configuration
     * \param[in] joint selected link of the selected iCub kinematic chain
     * \return 3D cartesian position of the selected link in robot reference frame
     */
    std::vector<double> GetCartesianPosition(unsigned int joint);

    /**
     * \brief Compute 3D End-Effector position for the robot joint configuration
     * \return 3D cartesian position of the end-effector in robot reference frame
     */
    std::vector<double> GetHandPosition();

    /**
     * \brief Compute the joint configuration for a given 3D End-Effector position (Inverse Kinematics)
     * \param[in] position target 3D End-Effector position
     * \param[in] blocked_links links of the kinematic chain, that should be blocked for inverse computation
     * \return joint angle configuration for given position (free joints)
     */
    std::vector<double> solveInvKin(std::vector<double> position, std::vector<int> blocked_links);

    // test method for inverse kinematic
    void testinvKin();

    /*** gRPC functions ***/
#ifdef _USE_GRPC
    std::vector<double> provideData(int value);
    std::vector<double> provideData();
#endif

 private:
    /*** configuration variables ***/
    std::vector<std::string> key_map{"right_arm", "left_arm"};    // valid iCub part keys
    // std::vector<std::string> key_map{"head", "torso", "right_arm", "left_arm", "right_leg", "left_leg"};    // valid iCub part keys

    /*** parameter ***/
    int joint_arm;      // number of joints arm
    int joint_torso;    // number of joints torso

    /*** yarp data structures ***/
    yarp::dev::PolyDriver driver_arm;        // yarp driver needed for reading joint encoders
    yarp::dev::IEncoders* encoder_arm;       // iCub joint encoder interface
    yarp::dev::IControlLimits* limit_arm;    // iCub joint limits interface

    yarp::dev::PolyDriver driver_torso;        // yarp driver needed for reading joint encoders
    yarp::dev::IEncoders* encoder_torso;       // iCub joint encoder interface
    yarp::dev::IControlLimits* limit_torso;    // iCub joint limits interface

    std::deque<yarp::dev::IControlLimits*> limits;    // joint limit interface

    /*** Kinematic Interfaces ***/
    iCub::iKin::iCubArm* KinArm;          // iCub Arm kinematic chain
    iCub::iKin::iCubTorso* KinTorso;      // iCub Torso kinematic chain
    iCub::iKin::iCubFinger* KinFinger;    // iCub Fingers kinematic chain

    iCub::iKin::iKinChain* KinChain;    // selected kinematic chain

    /** grpc communication **/
#ifdef _USE_GRPC
    std::string _ip_address = "";    // gRPC server ip address
    unsigned int _port = -1;         // gRPC server port
    ServerInstance* kin_source;      // gRPC server instance
    std::thread server_thread;       // thread for running the gRPC server in parallel
#endif

    /*** auxilary functions ***/
    // check if iCub part key is valid
    bool CheckPartKey(std::string key);
    // read joint angles from robot
    std::vector<double> ReadDoubleAll(yarp::dev::IEncoders* iencoder, unsigned int joint_count);
};
