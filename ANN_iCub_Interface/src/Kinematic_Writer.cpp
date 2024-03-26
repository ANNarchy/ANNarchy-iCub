/*
 *  Copyright (C) 2022 Torsten Fietzek
 *
 *  KinematicWriter.cpp is part of the ANNarchy iCub interface
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

#include "Kinematic_Writer.hpp"

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
KinematicWriter::~KinematicWriter() { Close(); }

/*** public methods for the user ***/
bool KinematicWriter::Init(std::string part, float version, std::string ini_path, bool offline_mode) {
    /*
        Initialize the Kinematic Writer with given parameters

        params: std::string part        -- string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso}

        return: bool                    -- return True, if successful
    */

    if (!this->dev_init) {
        if (!CheckPartKey(part)) {
            std::cerr << "[Kinematic Writer] " << part << " is an invalid iCub part key!" << std::endl;
            return false;
        }
        this->icub_part = part;

        if (version <= 0. || version >= 4.) {
            std::cerr << "[Kinematic Writer] " << version << " is an invalid version number!" << std::endl;
            return false;
        }

        // Check Yarp-network
        if (!yarp::os::Network::checkNetwork() && !offline_mode) {
            std::cerr << "[Kinematic Writer " << icub_part << "] YARP Network is not online. Check nameserver is running!" << std::endl;
            return false;
        }

#ifdef _USE_LOG_QUIET
        // set YARP logging level to warnings, if the respective environment variable is set
        auto yarp_quiet = GetEnvVar("YARP_QUIET");
        if (yarp_quiet == "on" || yarp_quiet == "1") {
            yarp::os::Log::setMinimumPrintLevel(yarp::os::Log::WarningType);
        }
#endif

        // read configuration data from ini file
        INIReader reader_gen(ini_path + "/interface_param.ini");
        if (reader_gen.ParseError() != 0) {
            std::cerr << "[Kinematic Writer " << icub_part << "] Error in parsing the ini-file! Please check the ini-path \"" << ini_path << "\" and the ini file content!" << std::endl;
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
                std::cerr << "[Kinematic Writer " << icub_part << "] Unable to establish kinematic chain!" << std::endl;
                return false;
            }

            active_torso = false;
            if (!offline_mode) {
                // setup iCub joint position control
                yarp::os::Property options_torso;
                options_torso.put("device", "remote_controlboard");
                options_torso.put("remote", (robot_port_prefix + "/torso").c_str());
                options_torso.put("local", (client_port_prefix + "/ANNarchy_Kin_write/torso").c_str());

                if (!driver_torso.open(options_torso)) {
                    std::cerr << "[Kinematic Writer torso] Unable to open " << options_torso.find("device").asString() << "!" << std::endl;
                    return false;
                } else {
                    if (!driver_torso.view(encoder_torso)) {
                        std::cerr << "[Kinematic Writer torso] Unable to open motor encoder interface!" << std::endl;
                        Close();
                        return false;
                    }

                    if (!driver_torso.view(limit_torso)) {
                        std::cerr << "[Kinematic Writer torso] Unable to open motor limit interface!" << std::endl;
                        Close();
                        return false;
                    }

                    encoder_torso->getAxes(&joint_torso);
                    limits.push_back(limit_torso);

                    // add torso joints to the active part of the kinematic chain
                    KinArm->releaseLink(0);
                    KinArm->releaseLink(1);
                    KinArm->releaseLink(2);

                    active_torso = true;
                }

                // setup iCub joint position control
                yarp::os::Property options_arm;
                options_arm.put("device", "remote_controlboard");
                options_arm.put("remote", (robot_port_prefix + "/" + part).c_str());
                options_arm.put("local", (client_port_prefix + "/ANNarchy_Kin_write/" + part).c_str());

                if (!driver_arm.open(options_arm)) {
                    std::cerr << "[Kinematic Writer " << part << "] Unable to open " << options_arm.find("device").asString() << "!" << std::endl;
                    return false;
                }

                if (!driver_arm.view(encoder_arm)) {
                    std::cerr << "[Kinematic Writer " << part << "] Unable to open motor encoder interface!" << std::endl;
                    Close();
                    return false;
                }

                if (!driver_arm.view(limit_arm)) {
                    std::cerr << "[Kinematic Writer " << part << "] Unable to open motor limit interface!" << std::endl;
                    Close();
                    return false;
                }

                encoder_arm->getAxes(&joint_arm);
                limits.push_back(limit_arm);

                KinArm->alignJointsBounds(limits);
            } else {
                // add torso joints to the active part of the kinematic chain
                KinArm->releaseLink(0);
                KinArm->releaseLink(1);
                KinArm->releaseLink(2);

                angles_set = false;
            }
        }
        this->KinChain = KinArm->asChain();

        this->type = "KinematicWriter";
        offlinemode = offline_mode;
        init_param["part"] = part;
        init_param["version"] = std::to_string(version);
        init_param["ini_path"] = ini_path;
        init_param["offline_mode"] = std::to_string(offline_mode);
        this->dev_init = true;
        return true;
    } else {
        std::cerr << "[Kinematic Writer " << icub_part << "] Initialization aready done!" << std::endl;
        return false;
    }
}

#ifdef _USE_GRPC
bool KinematicWriter::InitGRPC(std::string part, float version, std::string ini_path, std::string ip_address, unsigned int port, bool offline_mode) {
    /*
        Initialize the Kinematic Writer with given parameters

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
            std::cerr << "[Kinematic Writer] Initialization failed!" << std::endl;
            return false;
        }
    } else {
        std::cerr << "[Kinematic Writer] Initialization already done!" << std::endl;
        return false;
    }
}
#else
bool KinematicWriter::InitGRPC(std::string part, float version, std::string ini_path, std::string ip_address, unsigned int port, bool offline_mode) {
    /*
        Initialize the Kinematic Writer with given parameters

        params: std::string part        -- string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso}
                string ip_address       -- gRPC server ip address
                unsigned int port       -- gRPC server port

        return: bool                    -- return True, if successful
    */
    std::cerr << "[Kinematic Writer] gRPC is not included in the setup process!" << std::endl;
    return false;
}
#endif

void KinematicWriter::Close() {
    /*
        Close Kinematic Writer with cleanup
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
void KinematicWriter::BlockLinks(std::vector<int> joints) {
    if (CheckInit() && offlinemode) {
        for (auto it = joints.begin(); it != joints.end(); ++it) {
            KinArm->blockLink(*it);
        }
    }
}

// Get blocked links
std::vector<int> KinematicWriter::GetBlockedLinks() {
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

int KinematicWriter::GetDOF() {
    /*
        Return number of controlled joints

        return: int       -- return number of controlled joints
    */
    if (CheckInit()) {
        return KinChain->getDOF();
    } else {
        return -1;
    }
}

// Get joints being part of active kinematic chain
std::vector<int> KinematicWriter::GetDOFLinks() {
    std::vector<int> dof;
    if (CheckInit() && offlinemode) {
        for (unsigned int i = 0; i < KinArm->getN(); i++) {
            if (!KinArm->isLinkBlocked(i)) {
                dof.push_back(i);
            }
        }
    }
    return dof;
}

// Get joint angles in radians
std::vector<double> KinematicWriter::GetJointAngles() {
    if (CheckInit()) {
        auto angles = KinArm->getAng();
        return std::vector<double>(angles.begin(), angles.end());
    } else {
        return std::vector<double>();
    }
}

// Set released links of kinematic chain
void KinematicWriter::ReleaseLinks(std::vector<int> joints) {
    if (CheckInit() && offlinemode) {
        for (auto it = joints.begin(); it != joints.end(); ++it) {
            KinArm->releaseLink(*it);
        }
    }
}

// Set joint angles for forward kinematic in offline mode
std::vector<double> KinematicWriter::SetJointAngles(std::vector<double> joint_angles) {
    std::vector<double> act_angles;
    if (CheckInit() && offlinemode) {
        yarp::sig::Vector angles = KinArm->setAng(yarp::sig::Vector(joint_angles.size(), joint_angles.data()));
        angles_set = true;
        act_angles.assign(angles.begin(), angles.end());
        return act_angles;
    }
    return act_angles;
}

std::vector<double> KinematicWriter::SolveInvKin(std::vector<double> position, std::vector<int> blocked_links) {
    /*
        Compute the joint configuration for a given 3D End-Effector position (Inverse Kinematics) in online mode.

        return: vector       -- joint angle configuration for given position (free joints)
    */
    std::vector<double> joint_angles, angles_arm, angles_torso, angles;
    if (CheckInit()) {
        // Init necessary data structures
        yarp::sig::Vector pos(position.size(), position.data());
        yarp::sig::Vector jnt_angles;
        bool value = true;

        // in online mode: read the angles from the robot and set them to the kinematic chain
        if (!offlinemode) {
            // read joint angles
            angles_arm = ReadDoubleAll(encoder_arm, joint_arm);
            if (active_torso) {
                angles_torso = ReadDoubleAll(encoder_torso, joint_torso);
            } else {
                angles_torso = std::vector<double>({0., 0., 0.});
                blocked_links.insert(blocked_links.end(), {0, 1, 2});
            }
            angles_torso.insert(angles_torso.end(), angles_arm.begin(), angles_arm.begin() + 7);

            // block links from blocking selection
            if (blocked_links.size() > 0) {
                for (auto it = blocked_links.begin(); it != blocked_links.end(); it++) {
                    value = value & KinArm->blockLink(*it);
                }
                // strip blocked links from joint angle vector
                for (unsigned int i = 0; i < angles_torso.size(); i++) {
                    if (std::find(blocked_links.begin(), blocked_links.end(), i) == blocked_links.end()) {
                        angles.push_back(angles_torso[i]);
                    }
                }
            } else {
                angles = angles_torso;
            }

            // set joint configuration for kinematic chain
            double deg2rad1 = this->deg2rad;
            std::transform(angles.begin(), angles.end(), angles.begin(), [deg2rad1](double& c) { return c * deg2rad1; });
            KinArm->setAng(yarp::sig::Vector(angles.size(), angles.data()));
        }

        // compute inverse kinematics
        iCub::iKin::iKinIpOptMin slv(*this->KinChain, IKINCTRL_POSE_XYZ, 1e-3, 1e-6, 100);
        slv.setUserScaling(true, 100.0, 100.0, 100.0);
        slv.setMaxIter(5000);
        jnt_angles = slv.solve(KinArm->getAng(), pos);
        joint_angles.assign(jnt_angles.begin(), jnt_angles.end());

        if (!offlinemode) {
            // unblock blocked links for further computations
            if (blocked_links.size() > 0) {
                for (auto it = blocked_links.begin(); it != blocked_links.end(); it++) {
                    value = value & KinArm->releaseLink(*it);
                }
            }
        }
    }
    return joint_angles;
}

void KinematicWriter::testinvKin() {
    yarp::sig::Vector q0, qf, qhat, xf, xhat;

    KinChain->blockLink(2);
    KinChain->blockLink(1);
    KinChain->blockLink(0);

    // get initial joints configuration
    q0 = KinChain->getAng();

    // dump DOF bounds using () operators and set
    // a second joints configuration in the middle of the compact set.
    // Remind that angles are expressed in radians
    qf.resize(KinChain->getDOF());
    for (unsigned int i = 0; i < KinChain->getDOF(); i++) {
        double min = (*KinChain)(i).getMin();
        double max = (*KinChain)(i).getMax();
        qf[i] = (min + max) / 2.0;

        // last joint set to 1 deg higher than the bound
        if (i == KinChain->getDOF() - 1) qf[i] = max + 1.0 * iCub::ctrl::CTRL_DEG2RAD;

        std::cout << "joint " << i << " in [" << iCub::ctrl::CTRL_RAD2DEG * min << "," << iCub::ctrl::CTRL_RAD2DEG * max << "] set to " << iCub::ctrl::CTRL_RAD2DEG * qf[i] << std::endl;
    }

    // it is not allowed to overcome the bounds...
    // ...see the result
    qf = KinChain->setAng(qf);
    std::cout << "Actual joints set to " << (iCub::ctrl::CTRL_RAD2DEG * qf).toString() << std::endl;
    // anyway user can disable the constraints checking by calling
    // the chain method setAllConstraints(false)

    // there are three links for the torso which do not belong to the
    // DOF set since they are blocked. User can access them through [] operators
    std::cout << "Torso blocked links at:" << std::endl;
    for (unsigned int i = 0; i < KinChain->getN() - KinChain->getDOF(); i++) std::cout << iCub::ctrl::CTRL_RAD2DEG * (*KinChain)[i].getAng() << " ";
    std::cout << std::endl;

    // retrieve the end-effector pose.
    // Translational part is in meters.
    // Rotational part is in axis-angle representation
    xf = KinChain->EndEffPose();
    std::cout << "Current arm end-effector pose: " << xf.toString() << std::endl;

    // go back to the starting joints configuration
    KinChain->setAng(q0);

    // instantiate a IPOPT solver for inverse kinematic
    // for both translational and rotational part
    iCub::iKin::iKinIpOptMin slv(*KinChain, IKINCTRL_POSE_FULL, 1e-3, 1e-6, 100);

    // In order to speed up the process, a scaling for the problem
    // is usually required (a good scaling holds each element of the jacobian
    // of constraints and the hessian of lagrangian in norm between 0.1 and 10.0).
    slv.setUserScaling(true, 100.0, 100.0, 100.0);

    // note how the solver called internally the chain->setAllConstraints(false)
    // method in order to relax constraints
    for (unsigned int i = 0; i < KinChain->getN(); i++) {
        std::cout << "link " << i << ": " << (KinChain->getConstraint(i) ? "constrained" : "not-constrained") << std::endl;
    }

    // solve for xf starting from current configuration q0
    double t = yarp::os::SystemClock::nowSystem();
    qhat = slv.solve(KinChain->getAng(), xf);
    double dt = yarp::os::SystemClock::nowSystem() - t;

    // in general the solved qf is different from the initial qf
    // due to the redundancy
    std::cout << "qhat: " << (iCub::ctrl::CTRL_RAD2DEG * qhat).toString() << std::endl;

    // check how much we achieve our goal
    // note that the chain has been manipulated by the solver,
    // so it's already in the final configuration
    xhat = KinChain->EndEffPose();
    std::cout << "Desired arm end-effector pose       xf= " << xf.toString() << std::endl;
    std::cout << "Achieved arm end-effector pose K(qhat)= " << xhat.toString() << std::endl;
    std::cout << "||xf-K(qhat)||=" << yarp::math::norm(xf - xhat) << std::endl;
    std::cout << "Solved in " << dt << " [s]" << std::endl;
    KinChain->releaseLink(2);
    KinChain->releaseLink(1);
    KinChain->releaseLink(0);
}

/*** gRPC functions ***/
#ifdef _USE_GRPC
std::vector<double> KinematicWriter::provideData(int value) { return std::vector<double>(); }
#endif

/*** auxilary functions ***/
bool KinematicWriter::CheckPartKey(std::string key) {
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

std::vector<double> KinematicWriter::ReadDoubleAll(yarp::dev::IEncoders* iencoder, unsigned int joint_count) {
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
