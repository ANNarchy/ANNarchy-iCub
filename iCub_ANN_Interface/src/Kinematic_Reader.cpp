/*
 *  Copyright (C) 2019-2021 Torsten Fietzek
 *
 *  KinReader.cpp is part of the iCub ANNarchy interface
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

#include "Kinematic_Reader.hpp"

#include <iCub/iKin/iKinFwd.h>    // iCub forward Kinematics
#include <math.h>
#include <yarp/dev/all.h>
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
KinReader::~KinReader() { Close(); }

/*** public methods for the user ***/
bool KinReader::Init(std::string part, float version, std::string ini_path) {
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

        if (version <= 0. or version >= 4.) {
            std::cerr << "[Kinematic Reader] " << version << " is an invalid version number!" << std::endl;
            return false;
        }

        // Check Yarp-network
        if (!yarp::os::Network::checkNetwork()) {
            std::cerr << "[Kinematic Reader " << icub_part << "] YARP Network is not online. Check nameserver is running!" << std::endl;
            return false;
        }

        // set YARP loging level to warnings, if the respective environment variable is set
        auto yarp_quiet = GetEnvVar("YARP_QUIET");
        if (yarp_quiet == "on" or yarp_quiet == "1") {
            yarp::os::Log::setMinimumPrintLevel(yarp::os::Log::WarningType);
        }

        // read configuration data from ini file
        INIReader reader_gen(ini_path + "interface_param.ini");
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
            std::cout << "Descriptor: " << descriptor << std::endl;

            KinArm = new iCub::iKin::iCubArm(descriptor);
            if (!KinArm->isValid()) {
                std::cerr << "[Kinematic Reader " << icub_part << "] Unable to establish kinematic chain!" << std::endl;
                return false;
            }
            KinArm->releaseLink(0);
            KinArm->releaseLink(1);
            KinArm->releaseLink(2);

            // setup iCub joint position control
            yarp::os::Property options_torso;
            options_torso.put("device", "remote_controlboard");
            options_torso.put("remote", (robot_port_prefix + "/torso").c_str());
            options_torso.put("local", (client_port_prefix + "/ANNarchy_Kin_read/torso").c_str());

            if (!driver_torso.open(options_torso)) {
                std::cerr << "[Kinematic Reader torso] Unable to open " << options_torso.find("device").asString() << "!" << std::endl;
                return false;
            }

            if (!driver_torso.view(encoder_torso)) {
                std::cerr << "[Kinematic Reader torso] Unable to open motor encoder interface!" << std::endl;
                driver_torso.close();
                return false;
            }

            if (!driver_torso.view(limit_torso)) {
                std::cerr << "[Kinematic Reader torso] Unable to open motor limit interface!" << std::endl;
                driver_torso.close();
                return false;
            }

            encoder_torso->getAxes(&joint_torso);
            limits.push_back(limit_torso);

            // setup iCub joint position control
            yarp::os::Property options_arm;
            options_arm.put("device", "remote_controlboard");
            options_arm.put("remote", (robot_port_prefix + "/" + part).c_str());
            options_arm.put("local", (client_port_prefix + "/ANNarchy_Kin_read/" + part).c_str());

            if (!driver_arm.open(options_arm)) {
                std::cerr << "[Kinematic Reader " << part << "] Unable to open " << options_arm.find("device").asString() << "!" << std::endl;
                return false;
            }

            if (!driver_arm.view(encoder_arm)) {
                std::cerr << "[Kinematic Reader " << part << "] Unable to open motor encoder interface!" << std::endl;
                driver_arm.close();
                return false;
            }

            if (!driver_arm.view(limit_arm)) {
                std::cerr << "[Kinematic Reader " << part << "] Unable to open motor limit interface!" << std::endl;
                driver_arm.close();
                return false;
            }

            encoder_arm->getAxes(&joint_arm);
            limits.push_back(limit_arm);

            KinArm->alignJointsBounds(limits);
        }

        this->type = "KinReader";
        init_param["part"] = part;
        init_param["version"] = std::to_string(version);
        init_param["ini_path"] = ini_path;
        this->dev_init = true;
        return true;
    } else {
        std::cerr << "[Kinematic Reader " << icub_part << "] Initialization aready done!" << std::endl;
        return false;
    }
}

#ifdef _USE_GRPC
bool KinReader::InitGRPC(std::string part, float version, std::string ini_path, std::string ip_address, unsigned int port) {
    /*
        Initialize the Kinematic Reader with given parameters

        params: std::string part        -- string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso}
                string ip_address       -- gRPC server ip address
                unsigned int port       -- gRPC server port

        return: bool                    -- return True, if successful
    */

    if (!this->dev_init) {
        if (this->Init(part, version, ini_path)) {
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
bool KinReader::InitGRPC(std::string part, float version, std::string ini_path, std::string ip_address, unsigned int port) {
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

void KinReader::Close() {
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

int KinReader::GetDOF() {
    /*
        Return number of controlled joints

        return: int       -- return number of controlled joints
    */
    if (CheckInit()) {
        if (KinArm->isValid()) {
            return KinArm->getDOF();
        } else if (KinTorso->isValid()) {
            return KinTorso->getDOF();
        } else {
            return 0;
        }
    } else {
        return 0;
    }
}

std::vector<double> KinReader::GetHandPosition() {
    std::vector<double> joint_angles, angles_arm;
    if (CheckInit()) {
        angles_arm = ReadDoubleAll(encoder_arm, joint_arm);
        joint_angles = ReadDoubleAll(encoder_torso, joint_torso);
        joint_angles.insert(joint_angles.end(), angles_arm.begin(), angles_arm.begin() + 7);
        double deg2rad = M_PI / 180.;
        std::transform(joint_angles.begin(), joint_angles.end(), joint_angles.begin(), [deg2rad](double& c) { return c * deg2rad; });
        KinArm->setAng(yarp::sig::Vector(joint_angles.size(), joint_angles.data()));
        yarp::sig::Vector position = KinArm->EndEffPosition();
        return std::vector<double>(position.begin(), position.end());
    }
    return joint_angles;
}

std::vector<double> KinReader::GetCartesianPosition(unsigned int joint) {
    std::vector<double> joint_angles, angles_arm;
    if (CheckInit()) {
        angles_arm = ReadDoubleAll(encoder_arm, joint_arm);
        joint_angles = ReadDoubleAll(encoder_torso, joint_torso);
        joint_angles.insert(joint_angles.end(), angles_arm.begin(), angles_arm.begin() + 7);
        double deg2rad = M_PI / 180.;
        std::transform(joint_angles.begin(), joint_angles.end(), joint_angles.begin(), [deg2rad](double& c) { return c * deg2rad; });
        KinArm->setAng(yarp::sig::Vector(joint_angles.size(), joint_angles.data()));
        yarp::sig::Vector position = KinArm->Position(joint);
        return std::vector<double>(position.begin(), position.end());
        std::vector<double> test;
        return test;
    }
    return joint_angles;
}

/*** gRPC functions ***/
// TODO seperated functions for different modi -> set enc/joints in init
#ifdef _USE_GRPC
std::vector<double> KinReader::provideData(int value) { return std::vector<double>(); }
std::vector<double> KinReader::provideData() { return GetHandPosition(); }
#endif

/*** auxilary functions ***/
bool KinReader::CheckPartKey(std::string key) {
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

std::vector<double> KinReader::ReadDoubleAll(yarp::dev::IEncoders* iencoder, unsigned int joint_count) {
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