/*
 *  Copyright (C) 2019-2022 Torsten Fietzek
 *
 *  KinematicReader.cpp is part of the ANNarchy iCub interface
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

#include "Kinematic_Reader.hpp"

#include <iCub/iKin/iKinFwd.h>    // iCub forward Kinematics
#include <math.h>
#include <yarp/dev/all.h>
#include <yarp/math/Math.h>
#include <yarp/os/all.h>
#include <yarp/sig/all.h>

#include <algorithm>
#include <iostream>
#include <map>
#include <string>
#include <thread>
#include <vector>

#include "INI_Reader/INIReader.h"
#include "Module_Base_Class.hpp"

#ifdef _USE_GRPC
#include "ProvideInputServer.h"
#endif

// Destructor
KinematicReader::~KinematicReader() { Close(); }

/*** public methods for the user ***/
bool KinematicReader::Init(std::string part, float version, std::string ini_path, bool offline_mode) {
    /*
        Initialize the Kinematic Reader with given parameters

        params: std::string part        -- string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso}

        return: bool                    -- return True, if successful
    */

    if (!this->dev_init) {
        if (!CheckPartKey(part)) {
            std::cerr << "[Kinematic Reader] " << part << " is an invalid iCub part key!" << std::endl;
            return false;
        }
        this->icub_part = part;

        if (version <= 0. || version >= 4.) {
            std::cerr << "[Kinematic Reader] " << version << " is an invalid version number!" << std::endl;
            return false;
        }

        // Check Yarp-network
        if (!yarp::os::Network::checkNetwork() && !offline_mode) {
            std::cerr << "[Kinematic Reader " << icub_part << "] YARP Network is not online. Check nameserver is running!" << std::endl;
            return false;
        }

#ifdef _USE_LOG_QUIET
        // set YARP loging level to warnings, if the respective environment variable is set
        auto yarp_quiet = GetEnvVar("YARP_QUIET");
        if (yarp_quiet == "on" || yarp_quiet == "1") {
            yarp::os::Log::setMinimumPrintLevel(yarp::os::Log::WarningType);
        }
#endif

        // read configuration data from ini file
        INIReader reader_gen(ini_path + "/interface_param.ini");
        if (reader_gen.ParseError() != 0) {
            std::cerr << "[Kinematic Reader " << icub_part << "] Error in parsing the ini-file! Please check the ini-path \"" << ini_path << "\" and the ini file content!" << std::endl;
            return false;
        }
        std::string robot_port_prefix = reader_gen.Get("general", "robot_port_prefix", "/icubSim");
        std::string client_port_prefix = reader_gen.Get("general", "client_port_prefix", "/client");

        if (part == "right_arm" || part == "left_arm") {
            std::string::size_type i = part.find("_arm");
            std::string descriptor = part.substr(0, i);

            descriptor.append("_v" + std::to_string(version).substr(0, 3));

            KinArm = new iCub::iKin::iCubArm(descriptor);
            if (!KinArm->isValid()) {
                std::cerr << "[Kinematic Reader " << icub_part << "] Unable to establish kinematic chain!" << std::endl;
                return false;
            }

            // add torso joints to the active part of the kinematic chain
            KinArm->releaseLink(0);
            KinArm->releaseLink(1);
            KinArm->releaseLink(2);

            active_torso = false;
            if (!offline_mode) {
                // setup iCub joint position control
                yarp::os::Property options_torso;
                options_torso.put("device", "remote_controlboard");
                options_torso.put("remote", (robot_port_prefix + "/torso").c_str());
                options_torso.put("local", (client_port_prefix + "/ANNarchy_Kin_read_" + std::to_string(std::time(NULL)) + "/torso").c_str());

                if (!driver_torso.open(options_torso)) {
                    std::cerr << "[Kinematic Reader torso] Unable to open " << options_torso.find("device").asString() << "!" << std::endl;
                    return false;
                } else {
                    if (!driver_torso.view(encoder_torso)) {
                        std::cerr << "[Kinematic Reader torso] Unable to open motor encoder interface!" << std::endl;
                        Close();
                        return false;
                    }

                    if (!driver_torso.view(limit_torso)) {
                        std::cerr << "[Kinematic Reader torso] Unable to open motor limit interface!" << std::endl;
                        Close();
                        return false;
                    }

                    encoder_torso->getAxes(&joint_torso);
                    limits.push_back(limit_torso);

                    active_torso = true;
                }

                // setup iCub joint position control
                yarp::os::Property options_arm;
                options_arm.put("device", "remote_controlboard");
                options_arm.put("remote", (robot_port_prefix + "/" + part).c_str());
                options_arm.put("local", (client_port_prefix + "/ANNarchy_Kin_read_" + std::to_string(std::time(NULL)) + "/" + part).c_str());

                if (!driver_arm.open(options_arm)) {
                    std::cerr << "[Kinematic Reader " << part << "] Unable to open " << options_arm.find("device").asString() << "!" << std::endl;
                    return false;
                }

                if (!driver_arm.view(encoder_arm)) {
                    std::cerr << "[Kinematic Reader " << part << "] Unable to open motor encoder interface!" << std::endl;
                    Close();
                    return false;
                }

                if (!driver_arm.view(limit_arm)) {
                    std::cerr << "[Kinematic Reader " << part << "] Unable to open motor limit interface!" << std::endl;
                    Close();
                    return false;
                }

                encoder_arm->getAxes(&joint_arm);
                limits.push_back(limit_arm);

                KinArm->alignJointsBounds(limits);
            } else {
                angles_set = false;
            }
        }

        this->type = "KinematicReader";
        offlinemode = offline_mode;
        init_param["part"] = part;
        init_param["version"] = std::to_string(version);
        init_param["ini_path"] = ini_path;
        init_param["offline_mode"] = std::to_string(offline_mode);
        this->dev_init = true;
        return true;
    } else {
        std::cerr << "[Kinematic Reader " << icub_part << "] Initialization aready done!" << std::endl;
        return false;
    }
}

#ifdef _USE_GRPC
bool KinematicReader::InitGRPC(std::string part, float version, std::string ini_path, std::string ip_address, unsigned int port, bool offline_mode) {
    /*
        Initialize the Kinematic Reader with given parameters

        params: std::string part        -- string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso}
                string ip_address       -- gRPC server ip address
                unsigned int port       -- gRPC server port

        return: bool                    -- return True, if successful
    */

    if (!this->dev_init) {
        if (this->Init(part, version, ini_path, offline_mode)) {
            this->_ip_address = ip_address;
            this->_port = port;
            this->kin_source = new ServerInstance(ip_address, port, this);
            this->server_thread = std::thread(&ServerInstance::wait, this->kin_source);
            this->dev_init_grpc = true;
            init_param["ip_address"] = ip_address;
            init_param["port"] = std::to_string(port);
            return true;
        } else {
            std::cerr << "[Kinematic Reader] Initialization failed!" << std::endl;
            return false;
        }
    } else {
        std::cerr << "[Kinematic Reader] Initialization already done!" << std::endl;
        return false;
    }
}
#else
bool KinematicReader::InitGRPC(std::string part, float version, std::string ini_path, std::string ip_address, unsigned int port, bool offline_mode) {
    /*
        Initialize the Kinematic Reader with given parameters

        params: std::string part        -- string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso}
                string ip_address       -- gRPC server ip address
                unsigned int port       -- gRPC server port

        return: bool                    -- return True, if successful
    */

    std::cerr << "[Kinematic Reader] gRPC is not included in the setup process!" << std::endl;
    return false;
}
#endif

void KinematicReader::Close() {
    /*
        Close Kinematic Reader with cleanup
    */

    if (driver_torso.isValid()) {
        driver_torso.close();
    }

    if (driver_arm.isValid()) {
        driver_arm.close();
    }

#ifdef _USE_GRPC
    if (dev_init_grpc) {
        kin_source->shutdown();
        server_thread.join();
        delete kin_source;
        dev_init_grpc = false;
    }
#endif

    this->dev_init = false;
}

// Block given links
void KinematicReader::BlockLinks(std::vector<int> joints) {
    if (CheckInit() && offlinemode) {
        for (auto it = joints.begin(); it != joints.end(); ++it) {
            KinArm->blockLink(*it);
        }
    }
}

// Get blocked links
std::vector<int> KinematicReader::GetBlockedLinks() {
    std::vector<int> blocked;
    if (CheckInit() && offlinemode) {
        for (unsigned int i = 0; i < KinArm->getN(); i++) {
            if (KinArm->isLinkBlocked(i)) {
                blocked.push_back(i);
            }
        }
    }
    return blocked;
}

std::vector<double> KinematicReader::GetCartesianPosition(unsigned int joint) {
    /*
        Return cartesian position the selected iCub arm/torso joint based on iCub joint angles (online)

        return: vector       -- return cartesian position the selected iCub arm/torso joint
    */

    std::vector<double> joint_angles, angles_arm;
    if (CheckInit()) {
        if (!offlinemode) {
            // read joint angles from robot
            angles_arm = ReadDoubleAll(encoder_arm, joint_arm);
            if (active_torso) {
                joint_angles = ReadDoubleAll(encoder_torso, joint_torso);
                joint_angles.insert(joint_angles.end(), angles_arm.begin(), angles_arm.begin() + 7);
            } else {
                joint_angles = angles_arm;
                for (unsigned int i = 0; i < 3; i++) {
                    KinArm->blockLink(i);
                }
            }
            double deg2rad1 = this->deg2rad;

            // set joint configuration for kinematic chain
            std::transform(joint_angles.begin(), joint_angles.end(), joint_angles.begin(), [deg2rad1](double& c) { return c * deg2rad1; });
            KinArm->setAng(yarp::sig::Vector(joint_angles.size(), joint_angles.data()));
        } else {
            if (!angles_set) {
                std::cerr << "[Kinematic Reader] Warning: The joint angles are not set yet!" << std::endl;
            }
        }
        // compute forward kinematics
        yarp::sig::Vector position = KinArm->Position(joint);
        return std::vector<double>(position.begin(), position.end());
    }
    return joint_angles;
}

int KinematicReader::GetDOF() {
    /*
        Return number of controlled joints

        return: int       -- return number of controlled joints
    */

    if (CheckInit()) {
        if (KinArm->isValid()) {
            return KinArm->getDOF();
        } else {
            return -1;
        }
    } else {
        return -1;
    }
}

// Get joints being part of active kinematic chain
std::vector<int> KinematicReader::GetDOFLinks() {
    std::vector<int> dof;
    if (CheckInit()) {
        for (unsigned int i = 0; i < KinArm->getN(); i++) {
            if (!KinArm->isLinkBlocked(i)) {
                dof.push_back(i);
            }
        }
    }
    return dof;
}

std::vector<double> KinematicReader::GetHandPosition() {
    /*
        Return cartesian position of the iCub Hand based on iCub joint angles (online)

        return: vector       -- return cartesian position of the iCub Hand
    */

    std::vector<double> joint_angles, angles_arm;
    if (CheckInit()) {
        if (!offlinemode) {
            // read joint angles from robot
            angles_arm = ReadDoubleAll(encoder_arm, joint_arm);
            joint_angles = ReadDoubleAll(encoder_torso, joint_torso);
            joint_angles.insert(joint_angles.end(), angles_arm.begin(), angles_arm.begin() + 7);
            double deg2rad1 = this->deg2rad;

            // set joint configuration for kinematic chain
            std::transform(joint_angles.begin(), joint_angles.end(), joint_angles.begin(), [deg2rad1](double& c) { return c * deg2rad1; });
            KinArm->setAng(yarp::sig::Vector(joint_angles.size(), joint_angles.data()));
        } else {
            if (!angles_set) {
                std::cerr << "[Kinematic Reader] Warning: The joint angles are not set yet!" << std::endl;
            }
        }
        yarp::sig::Vector position = KinArm->EndEffPosition();
        return std::vector<double>(position.begin(), position.end());
    }
    return joint_angles;
}

// Get joint angles in radians
std::vector<double> KinematicReader::GetJointAngles() {
    if (CheckInit()) {
        auto angles = KinArm->getAng();
        return std::vector<double>(angles.begin(), angles.end());
    } else {
        return std::vector<double>();
    }
}

// Set released links of kinematic chain
void KinematicReader::ReleaseLinks(std::vector<int> joints) {
    if (CheckInit() && offlinemode) {
        for (auto it = joints.begin(); it != joints.end(); ++it) {
            KinArm->releaseLink(*it);
        }
    }
}

// Set joint angles for forward kinematic in offline mode
std::vector<double> KinematicReader::SetJointAngles(std::vector<double> joint_angles) {
    std::vector<double> act_angles;
    if (CheckInit() && offlinemode) {
        yarp::sig::Vector angles = KinArm->setAng(yarp::sig::Vector(joint_angles.size(), joint_angles.data()));
        angles_set = true;
        act_angles.assign(angles.begin(), angles.end());
        return act_angles;
    }
    return act_angles;
}

/*** gRPC functions ***/
#ifdef _USE_GRPC
std::vector<double> KinematicReader::provideData(int value) { return std::vector<double>(); }
std::vector<double> KinematicReader::provideData() { return GetHandPosition(); }
#endif

/*** auxilary functions ***/
bool KinematicReader::CheckPartKey(std::string key) {
    /*
        Check if iCub part key is valid
    */

    bool inside = false;
    for (auto it = key_map.cbegin(); it != key_map.cend(); it++)
        if (key == *it) {
            inside = true;
            break;
        }
    return inside;
}

std::vector<double> KinematicReader::ReadDoubleAll(yarp::dev::IEncoders* iencoder, unsigned int joint_count) {
    /*
        Read all joints and return joint angles directly as double value

        return: std::vector<double>     -- joint angles read from the robot
    */

    std::vector<double> angles;
    angles.resize(joint_count);
    while (!iencoder->getEncoders(angles.data())) {
        yarp::os::Time::delay(0.001);
    }
    return angles;
}
