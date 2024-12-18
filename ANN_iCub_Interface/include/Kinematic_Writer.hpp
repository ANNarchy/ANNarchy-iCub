/*
 *  Copyright (C) 2022 Torsten Fietzek
 *
 *  Kinematic_Writer.hpp is part of the ANNarchy iCub interface
 *
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  The ANNarchy iCub interface is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this headers. If not, see <http://www.gnu.org/licenses/>.
 */

#pragma once

#include <iCub/iKin/iKinIpOpt.h>    // iCub inverse Kinematics
#include <yarp/dev/all.h>
#include <yarp/sig/all.h>

#include <deque>
#include <map>
#include <string>
#include <string_view>
#include <thread>
#include <vector>

#include "Module_Base_Class.hpp"
#ifdef _USE_GRPC
#include "ProvideInputServer.h"
#endif

/**
 * \brief  Read-out of the joint angles of the iCub robot
 */
class KinematicWriter : public Mod_BaseClass {
 public:
    // Constructor
    KinematicWriter() = default;
    // Destructor
    ~KinematicWriter();

    /*** public methods for the user ***/

    /**
     * \brief Initialize the kinematic writer with given parameters
     * \param[in] part A string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso}.
     * \param[in] version iCub hardware version
     * \param[in] ini_path Path to the "interface_param.ini"-file.
     * \param[in] offline_mode flag if limits are retrieved from running iCub -> if true no running iCub is necessary
     * \param[in] active_torso if torso is used, include it in kinematic chain
     * \return True, if the initializatiion was successful. False if an error occured. Additionally, an error message is written to the error stream (cerr).\n
     *          Typical errors:
     *              - arguments not valid: e.g. part string not correct or ini file not in given path \n
     *              - YARP-Server not running
     */
    bool Init(std::string part, float version, std::string ini_path, bool offline_mode, bool active_torso);

    /**
     * \brief Initialize the kinematic writer with given parameters
     * \param[in] part A string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso}.
     * \param[in] version iCub hardware version
     * \param[in] ini_path Path to the "interface_param.ini"-file.
     * \param[in] ip_address gRPC server ip address -> has to match ip address of the JointReadOut-Population
     * \param[in] port gRPC server port -> has to match port of the JointReadOut-Population
     * \param[in] offline_mode flag if limits are retrieved from running iCub -> if true no running iCub is necessary
     * \return True, if the initializatiion was successful. False if an error occured. Additionally, an error message is written to the error stream (cerr).\n
     *          Typical errors:
     *              - arguments not valid: e.g. part string not correct or ini file not in given path \n
     *              - YARP-Server not running
     */
    bool InitGRPC(std::string part, float version, std::string ini_path, std::string ip_address, unsigned int port, bool offline_mode, bool active_torso);

    bool InitConf(std::string robot_prefix, std::string client_prefix, std::string part, float version, bool offline_mode);

    /**
     * \brief  Close kinematic writer with cleanup
     */
    void Close() override;

    /**
     * \brief Set blocked links. Chain DOF reduced by number of blocked links.
     * \param[in] joints links to block in kinematic chain
     */
    void BlockLinks(std::vector<int> joints);

    /**
     * \brief Get blocked links
     * \return blocked links
     */
    std::vector<int> GetBlockedLinks();

    /**
     * \brief  Return number of controlled joints
     * \return Number of joints, being controlled by the writer
     */
    int GetDOF();

    /**
     * \brief Get joints being part of active kinematic chain
     * \return links of active kinematic chain
     */
    std::vector<int> GetDOFLinks();

    /**
     * \brief Get joint angles
     * \return return joint angles of free links -> radians
     */
    std::vector<double> GetJointAngles();

    /**
     * \brief Set released links of kinematic chain. Chain DOF increased by number of released links.
     * \param[in] joints
     */
    void ReleaseLinks(std::vector<int> joints);

    /**
     * \brief Set joint angles for inverse kinematic in offline mode
     * \param[in] joint_angles joint angles to set for inverse kinematic (in radians)
     * \return return the actual joint angles set for the free links -> radians
     */
    std::vector<double> SetJointAngles(std::vector<double> joint_angles);

    /**
     * \brief Compute the joint configuration for a given 3D End-Effector position (Inverse Kinematics)
     * \param[in] position target 3D End-Effector position
     * \param[in] blocked_links links of the kinematic chain, that should be blocked for computation
     * \return joint angle configuration for given position (free joints)
     */
    std::vector<double> SolveInvKin(std::vector<double> position, std::vector<int> blocked_links);

    // test method for inverse kinematic
    void testinvKin();

    /*** gRPC functions ***/
#ifdef _USE_GRPC
    std::vector<double> provideData(int value);
#endif

 private:
    /*** configuration variables ***/
    std::vector<std::string_view> key_map{"right_arm", "left_arm"};    // valid iCub part keys
    // std::vector<std::string> key_map{"head", "torso", "right_arm", "left_arm", "right_leg", "left_leg"};    // valid iCub part keys

    /*** parameter ***/
    int joint_arm;        // number of joints arm
    int joint_torso;      // number of joints torso
    bool active_torso;    // flag indicating if torso is included for online computation
    bool offlinemode;     // flag for offline mode
    bool angles_set;      // flag to check that angles are set at least once in offline mode
    double deg2rad = M_PI / 180.;

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
    iCub::iKin::iKinIpOptMin* slv;

    /** grpc communication **/
#ifdef _USE_GRPC
    std::string _ip_address = "";    // gRPC server ip address
    unsigned int _port = -1;         // gRPC server port
    ServerInstance* kin_source;      // gRPC server instance
    std::thread server_thread;       // thread for running the gRPC server in parallel
#endif

    /*** auxilary functions ***/
    // check if iCub part key is valid
    bool CheckPartKey(std::string_view key);
    // read joint angles from robot
    std::vector<double> ReadDoubleAll(yarp::dev::IEncoders* iencoder, unsigned int joint_count);
};
