/*
 *  Copyright (C) 2019-2022 Torsten Fietzek
 *
 *  Joint_Writer.cpp is part of the ANNarchy iCub interface
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

#include "Joint_Writer.hpp"

#include <yarp/dev/all.h>
#include <yarp/os/all.h>
#include <yarp/sig/all.h>

#include <algorithm>
#include <iostream>
#include <sstream>
#include <string>

#include "INI_Reader/INIReader.h"
#include "Module_Base_Class.hpp"
#ifdef _USE_GRPC
#include "WriteOutputClient.h"
#endif

// Destructor
JointWriter::~JointWriter() { Close(); }

/*** public methods for the user ***/
bool JointWriter::Init(std::string part, unsigned int pop_size, double deg_per_neuron, double speed, std::string ini_path) {
    /*
        Initialize the joint writer with given parameters

        params: std::string part        -- string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso}
                unsigned int pop_size   -- number of neurons per population, encoding each one joint angle; only works if parameter "deg_per_neuron" is not set
                double deg_per_neuron   -- degree per neuron in the populations, encoding the joints angles; if set: population size depends on joint working range
                double speed            -- velocity for the joint motions
                ini_path                -- Path to the "interface_param.ini"-file

        return: bool                    -- return True, if successful
    */

    if (!this->dev_init) {
        // Check validity of the iCub part key
        if (!CheckPartKey(part)) {
            std::cerr << "[Joint Writer] " << part << " is an invalid iCub part key!" << std::endl;
            return false;
        }
        this->icub_part = part;

        // Check validity of the population size
        if (pop_size < 0) {
            std::cerr << "[Joint Writer " << icub_part << "] Population size have to be positive!" << std::endl;
            return false;
        }

        // Check Yarp-network
        if (!yarp::os::Network::checkNetwork()) {
            std::cerr << "[Joint Writer " << icub_part << "] YARP Network is not online. Check nameserver is running!" << std::endl;
            return false;
        }

#ifdef _USE_LOG_QUIET
        // set YARP loging level to warnings, if the respective environment variable is set
        auto yarp_quiet = GetEnvVar("YARP_QUIET");
        if (yarp_quiet == "on" or yarp_quiet == "1") {
            yarp::os::Log::setMinimumPrintLevel(yarp::os::Log::WarningType);
        }
#endif

        // read configuration data from ini file
        INIReader reader_gen(ini_path + "/interface_param.ini");
        if (reader_gen.ParseError() != 0) {
            std::cerr << "[Joint Writer " << icub_part << "] Error in parsing the ini-file! Please check the ini-path \"" << ini_path << "\" and the ini file content!" << std::endl;
            return false;
        }
        bool on_Simulator = reader_gen.GetBoolean("general", "simulator", true);
        std::string port_prefix = reader_gen.Get("general", "robot_port_prefix", "/icubSim");
        if (on_Simulator && (port_prefix != "/icubSim")) {
            std::cerr << "[Joint Writer " << icub_part << "] The port prefix does not match the default simulator prefix!" << std::endl;
        }
        std::string client_port_prefix = reader_gen.Get("general", "client_port_prefix", "/client");

        // setup iCub joint position and velocity control
        yarp::os::Property options;
        options.put("device", "remote_controlboard");
        options.put("remote", (port_prefix + "/" + icub_part).c_str());
        options.put("local", (client_port_prefix + "/ANNarchy_write/" + icub_part).c_str());

        if (!driver.open(options)) {
            std::cerr << "[Joint Writer " << icub_part << "] Unable to open" << options.find("device").asString() << "!" << std::endl;
            return false;
        }

        if (!driver.view(ipos) || !driver.view(ienc) || !driver.view(ivel) || !driver.view(icont) || !driver.view(ilim)) {
            std::cerr << "[Joint Writer " << icub_part << "] Unable to open motor control interfaces!" << std::endl;
            driver.close();
            return false;
        }

        ipos->getAxes(&joints);
        yarp::sig::Vector tmp;
        tmp.resize(joints);

        int i;
        for (i = 0; i < joints; i++) {
            tmp[i] = 50.0;
        }
        ipos->setRefAccelerations(tmp.data());

        for (i = 0; i < joints; i++) {
            tmp[i] = 10.0;
            ipos->setRefSpeed(i, tmp[i]);
        }

        // resize vector for saving joint parameter
        joint_angles.resize(joints);
        neuron_deg_abs.resize(joints);
        neuron_deg_rel.resize(joints);
        joint_deg_res_abs.resize(joints);
        joint_deg_res_rel.resize(joints);
        joint_control_mode.resize(joints);

        // set default control mode -> position
        SetJointControlMode("position", -1);

        // Variables needed to set joint limits
        double joint_range;
        double min, max;

        for (int i = 0; i < joints; i++) {
            // set joint velocity
            if (speed > 0 && speed <= velocity_max) {
                ipos->setRefSpeed(i, speed);
            }
            // read joint limits
            ilim->getLimits(i, &min, &max);
            joint_min.push_back(min);
            joint_max.push_back(max);

            // printf("joint: %i, min: %f, max: %f \n", i, joint_min[i],
            // joint_max[i]);

            if (joint_min == joint_max) {
                std::cerr << "[Joint Writer " << icub_part << "] Error in reading joint limits!" << std::endl;
                return false;
            }

            // compute population code resolution
            joint_range = joint_max[i] - joint_min[i] + 1;
            if (pop_size > 0) {    // with given population size
                // absolute joint angles
                neuron_deg_abs[i].resize(pop_size);
                joint_deg_res_abs[i] = joint_range / pop_size;

                for (unsigned int j = 0; j < neuron_deg_abs[i].size(); j++) {
                    neuron_deg_abs[i][j] = joint_min[i] + j * joint_deg_res_abs[i];
                }
                // relative joint angles
                neuron_deg_rel[i].resize(pop_size);
                joint_deg_res_rel[i] = 2 * joint_range / pop_size;

                for (unsigned int j = 0; j < neuron_deg_rel[i].size(); j++) {
                    neuron_deg_rel[i][j] = -joint_range + j * joint_deg_res_rel[i];
                }
            } else if (deg_per_neuron > 0.0) {    // with given neuron resolution
                // absolute joint angles
                int joint_res = std::floor(joint_range / deg_per_neuron);
                neuron_deg_abs[i].resize(joint_res);
                joint_deg_res_abs[i] = deg_per_neuron;

                for (unsigned int j = 0; j < neuron_deg_abs[i].size(); j++) {
                    neuron_deg_abs[i][j] = joint_min[i] + j * deg_per_neuron;
                }
                // relative joint angles
                joint_res = std::floor(2 * joint_range / deg_per_neuron);
                neuron_deg_rel[i].resize(joint_res);
                joint_deg_res_rel[i] = deg_per_neuron;

                for (unsigned int j = 0; j < neuron_deg_rel[i].size(); j++) {
                    neuron_deg_rel[i][j] = -joint_range + j * deg_per_neuron;
                }
            } else {
                std::cerr << "[Joint Writer " << icub_part << "] Error in population size definition. Check the values for pop_size or deg_per_neuron!" << std::endl;
                driver.close();
                return false;
            }
        }

        this->type = "JointWriter";
        init_param["part"] = part;
        init_param["pop_size"] = std::to_string(pop_size);
        init_param["deg_per_neuron"] = std::to_string(deg_per_neuron);
        init_param["speed"] = std::to_string(speed);
        init_param["ini_path"] = ini_path;
        this->dev_init = true;
        return true;
    } else {
        std::cerr << "[Joint Writer " << icub_part << "] Initialization aready done!" << std::endl;
        return false;
    }
}
#ifdef _USE_GRPC
bool JointWriter::InitGRPC(std::string part, unsigned int pop_size, std::vector<int> joint_select, std::string mode, bool blocking, double deg_per_neuron, double speed, std::string ini_path,
                           std::string ip_address, unsigned int port) {
    /*
        Initialize the joint Writer with given parameters

        params: std::string part        -- string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso}
                unsigned int pop_size   -- number of neurons per population, encoding each one joint angle; only works if parameter "deg_per_neuron" is not set
                double deg_per_neuron   -- degree per neuron in the populations, encoding the joints angles; if set: population size depends on joint working range
                string ip_address
                unsigned int port

        return: bool                    -- return True, if successful
    */

    if (!this->dev_init) {
        if (this->Init(part, pop_size, deg_per_neuron, speed, ini_path)) {
            this->_ip_address = ip_address;
            this->_port = port;
            this->joint_source = std::make_unique<WriteClientInstance> (ip_address, port);
            this->_blocking = blocking;
            this->_mode = mode;
            this->_joint_select = joint_select;
            this->pop_size = pop_size;
            init_param["joint_select"] = vec2string<std::vector<int>>(joint_select);
            init_param["mode"] = mode;
            init_param["blocking"] = std::to_string(blocking);
            init_param["ip_address"] = ip_address;
            init_param["port"] = std::to_string(port);
            return true;
        } else {
            std::cerr << "[Joint Writer] Initialization failed!" << std::endl;
            return false;
        }
    } else {
        std::cerr << "[Joint Writer] Initialization already done!" << std::endl;
        return false;
    }
}
#else
bool JointWriter::InitGRPC(std::string part, unsigned int pop_size, std::vector<int> joint_select, std::string mode, bool blocking, double deg_per_neuron, double speed, std::string ini_path,
                           std::string ip_address, unsigned int port) {
    /*
        Initialize the joint Writer with given parameters

        params: std::string part        -- string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso}
                unsigned int pop_size   -- number of neurons per population, encoding each one joint angle; only works if parameter "deg_per_neuron" is not set
                double deg_per_neuron   -- degree per neuron in the populations, encoding the joints angles; if set: population size depends on joint working range
                string ip_address
                unsigned int port

        return: bool                    -- return True, if successful
    */
    std::cerr << "[Joint Writer] gRPC is not included in the setup process!" << std::endl;
    return false;
}
#endif
void JointWriter::Close() {
    /*
        Close joint writer with cleanup
    */
    if (driver.isValid()) {
        SetJointControlMode("position", -1);
        driver.close();
    }
#ifdef _USE_GRPC
    if (this->joint_source)
#endif
    this->dev_init = false;
}

int JointWriter::GetJointCount() {
    /*
        Get number of controlled joints

        return: int       -- return number of controlled joints
    */

    return joints;
}

std::vector<double> JointWriter::GetJointsDegRes() {
    /*
        Get the resolution in degree of the populations, encoding the joint angles

        return: std::vector<double>        -- return vector, containing the resolution for every joints population codimg in degree
    */

    CheckInit();
    return joint_deg_res_abs;
}

std::vector<unsigned int> JointWriter::GetNeuronsPerJoint() {
    /*
        Get the size of the populations, encoding the joint angles

        return: std::vector<unsigned int>        -- return vector, containing the population size for every joint
    */

    std::vector<unsigned int> neuron_counts(joints);
    if (CheckInit()) {
        for (int i = 0; i < joints; i++) {
            neuron_counts[i] = neuron_deg_abs[i].size();
        }
    }
    return neuron_counts;
}

bool JointWriter::SetJointVelocity(double speed, int joint) {
    /*
        Set velocity for a given joint or all joints

        params: double speed        -- velocity value to be set
                int joint           -- joint number of the robot part; -1 for all joints

        return: bool                -- return True, if successful
    */
    if (joint >= joints || joint < -1) {
        std::cerr << "[Joint Writer " << icub_part << "] Selected joint out of range!" << std::endl;
        return false;
    }
    // set velocity for all joints
    if (joint < 0) {
        for (int i = 0; i < joints; i++) {
            // set joint velocity
            if (speed > 0 && speed <= velocity_max) {
                ipos->setRefSpeed(i, speed);
            }
        }
        // set velocity for a single joint
    } else {
        // set joint velocity
        if (speed > 0 && speed < velocity_max) {
            ipos->setRefSpeed(joint, speed);
        }
    }
    return true;
}

bool JointWriter::SetJointAcceleration(double acc, int joint) {
    /*
        Set acceleration for a given joint or all joints

        params: double acc          -- acceleration value to be set
                int joint           -- joint number of the robot part; -1 for all joints

        return: bool                -- return True, if successful
    */
    if (joint >= joints || joint < -1) {
        std::cerr << "[Joint Writer " << icub_part << "] Selected joint out of range!" << std::endl;
        return false;
    }
    // set acceleration for all joints
    if (joint < 0) {
        for (int i = 0; i < joints; i++) {
            // set joint acceleration
            if (acc > 0 && acc <= acc_max) {
                ipos->setRefAcceleration(i, acc);
            }
        }
        // set acceleration for a single joint
    } else {
        // set joint acceleration
        if (acc > 0 && acc < acc_max) {
            ipos->setRefAcceleration(joint, acc);
        }
    }
    return true;
}

bool JointWriter::SetJointControlMode(std::string control_mode, int joint) {
    if (joint >= joints || joint < -1) {
        std::cerr << "[Joint Writer " << icub_part << "] Selected joint out of range!" << std::endl;
        return false;
    }
    if (joint < 0) {
        for (int i = 0; i < joints; i++) {
            // set control modes
            std::transform(control_mode.begin(), control_mode.end(), control_mode.begin(), [](unsigned char c) { return std::tolower(c); });
            if (control_mode == "position") {
                if (joint_control_mode[i] == VOCAB_CM_VELOCITY) {
                    ivel->stop(i);
                }
                icont->setControlMode(i, VOCAB_CM_POSITION);
                joint_control_mode[i] = static_cast<int32_t>(VOCAB_CM_POSITION);
            } else if (control_mode == "velocity") {
                icont->setControlMode(i, VOCAB_CM_VELOCITY);
                ivel->stop(i);
                joint_control_mode[i] = static_cast<int32_t>(VOCAB_CM_VELOCITY);
            } else {
                std::cerr << "[Joint Writer " << icub_part << "] Given Control mode is not valid!" << std::endl;
                return false;
            }
        }
    } else {
        // set control modes
        std::transform(control_mode.begin(), control_mode.end(), control_mode.begin(), [](unsigned char c) { return std::tolower(c); });
        if (control_mode == "position") {
            if (joint_control_mode[joint] == VOCAB_CM_VELOCITY) {
                ivel->stop(joint);
            }
            icont->setControlMode(joint, VOCAB_CM_POSITION);
            joint_control_mode[joint] = static_cast<int32_t>(VOCAB_CM_POSITION);
        } else if (control_mode == "velocity") {
            icont->setControlMode(joint, VOCAB_CM_VELOCITY);
            ivel->stop(joint);
            joint_control_mode[joint] = static_cast<int32_t>(VOCAB_CM_VELOCITY);
        } else {
            std::cerr << "[Joint Writer " << icub_part << "] Given Control mode is not valid!" << std::endl;
            return false;
        }
    }
    return true;
}

bool JointWriter::WriteDoubleAll(std::vector<double> position, std::string mode, bool blocking) {
    /*
        Write all joints with double values

        params: std::vector<double> position    -- joint angles to write to the robot joints
                string mode                     -- motion mode: absolute or relative
                bool blocking                   -- if True, function waits for end of motion

        return: bool                            -- return True, if successful
    */

    if (CheckInit()) {
        // Check joint count
        if (position.size() != joints) {
            std::cerr << "[Joint Writer " << icub_part << "] Array size does not fit with joint count!" << std::endl;
            return false;
        }
        std::vector<double> act_pos;
        act_pos.resize(joints);
        // execute motion dependent on selected mode
        bool start = false;
        if (mode == "abs") {
            // clamp to joint limits
            for (unsigned int i = 0; i < position.size(); i++) {
                position[i] = std::clamp(position[i], joint_min[i], joint_max[i]);
            }
            // start motion
            start = ipos->positionMove(position.data());

        } else if (mode == "rel") {
            // clamp to joint limits
            ienc->getEncoders(act_pos.data());
            for (int i = 0; i <= joints; i++) {
                double new_pos = act_pos[i] + position[i];
                if (new_pos > joint_max[i]) {
                    position[i] = joint_max[i] - act_pos[i];
                }
                if (new_pos < joint_min[i]) {
                    position[i] = joint_min[i] - act_pos[i];
                }
            }
            // start motion
            start = ipos->relativeMove(position.data());

        } else if (mode == "vel") {
            bool check_ctrl = true;
            // clamp to joint limits
            for (unsigned int i = 0; i < joints; i++) {
                check_ctrl = check_ctrl && (joint_control_mode[i] == VOCAB_CM_VELOCITY);
                position[i] = std::clamp(position[i], -velocity_max, velocity_max);
            }
            if (check_ctrl) {
                // start motion
                start = ivel->velocityMove(position.data());
            } else {
                std::cerr << "[Joint Writer " << icub_part << "] Motion mode does not fit with control mode! Use 'velocity' control mode for 'vel' motion mode" << std::endl;
            }

        } else {
            std::cerr << "[Joint Writer " << icub_part << "] No valid motion mode is given. Possible options are 'abs', 'rel' or 'vel' !" << std::endl;
        }

        // move joints blocking/non-blocking
        if (start) {
            if (blocking) {
                bool motion = false;
                while (!motion) {
                    if (!ipos->checkMotionDone(&motion)) {
                        std::cerr << "[Joint Writer " << icub_part << "] Communication error while moving occured!" << std::endl;
                        return false;
                    }
                }
            }
        }
        return start;
    } else {
        return false;
    }
}

bool JointWriter::WriteDoubleMultiple(std::vector<double> position, std::vector<int> joint_selection, std::string mode, bool blocking) {
    /*
        Write multiple joints with double values

        params: std::vector<double> position    -- joint angles to write to the robot joints
                std::vector<int> joint          -- joint selection of the robot part
                string mode                     -- motion mode: absolute or relative
                bool blocking                   -- if True, function waits for end of motion

        return: bool                            -- return True, if successful
    */

    if (CheckInit()) {
        // Check joint count
        if (joint_selection.size() > (unsigned int)joints) {
            std::cerr << "[Joint Writer " << icub_part << "] Too many joints for the robot part!" << std::endl;
            return false;
        }

        if (joint_selection.size() != position.size()) {
            std::cerr << "[Joint Writer " << icub_part << "] Position count and joint count does not fit together!" << std::endl;
            return false;
        }

        if (*(std::max_element(joint_selection.begin(), joint_selection.end())) >= joints) {
            std::cerr << "[Joint Writer " << icub_part << "] Maximum joint number is out of range!" << std::endl;
            return false;
        }

        if (*(std::min_element(joint_selection.begin(), joint_selection.end())) < 0) {
            std::cerr << "[Joint Writer " << icub_part << "] Minimum joint number is out of range!" << std::endl;
            return false;
        }

        // execute motion dependent on selected mode
        bool start = false;
        if (mode == "abs") {
            // clamp to joint limits
            for (unsigned int i = 0; i < position.size(); i++) {
                position[i] = std::clamp(position[i], joint_min[joint_selection[i]], joint_max[joint_selection[i]]);
            }
            // start motion
            start = ipos->positionMove(joint_selection.size(), joint_selection.data(), position.data());
        } else if (mode == "rel") {
            // clamp to joint limits
            std::vector<double> act_pos;
            act_pos.resize(joints);
            ienc->getEncoders(act_pos.data());
            int i = 0;
            for (std::vector<int>::iterator it = joint_selection.begin(); it != joint_selection.end(); ++it) {
                double new_pos = act_pos[*it] + position[i];
                if (new_pos > joint_max[*it]) {
                    position[i] = joint_max[*it] - act_pos[*it];
                }
                if (new_pos < joint_min[*it]) {
                    position[i] = joint_min[*it] - act_pos[*it];
                }
                i++;
            }
            // start motion
            start = ipos->relativeMove(joint_selection.size(), joint_selection.data(), position.data());
        } else if (mode == "vel") {
            bool check_ctrl = true;
            // clamp to joint limits
            for (unsigned int i = 0; i < joint_selection.size(); i++) {
                check_ctrl = check_ctrl && (joint_control_mode[joint_selection[i]] == VOCAB_CM_VELOCITY);
                position[i] = std::clamp(position[i], -velocity_max, velocity_max);
            }
            if (check_ctrl) {
                // start motion
                start = ivel->velocityMove(joint_selection.size(), joint_selection.data(), position.data());
            } else {
                std::cerr << "[Joint Writer " << icub_part << "] Motion mode does not fit with control mode! Use 'velocity' control mode for 'vel' motion mode" << std::endl;
            }
        } else {
            std::cerr << "[Joint Writer " << icub_part << "] No valid motion mode is given. Possible options are 'abs', 'rel' or 'vel !" << std::endl;
        }

        // move joints blocking/non-blocking
        if (start) {
            if (blocking) {
                bool motion = false;
                while (!motion) {
                    if (!ipos->checkMotionDone(&motion)) {
                        std::cerr << "[Joint Writer " << icub_part << "] Communication error while moving occured!" << std::endl;
                        return false;
                    }
                }
            }
        }
        return start;
    } else {
        return false;
    }
}

bool JointWriter::WriteDoubleOne(double position, int joint, std::string mode, bool blocking) {
    /*
        Write one joint with double value

        params: double position     -- joint angle or velocity to write to the robot joint
                int joint           -- joint number of the robot part
                string mode         -- motion mode: absolute, relative or velocity
                bool blocking       -- if True, function waits for end of motion

        return: bool                -- return True, if successful
    */

    if (CheckInit()) {
        // Check joint number
        if (joint >= joints || joint < 0) {
            std::cerr << "[Joint Writer " << icub_part << "] Selected joint <" << joint << "> out of range!" << std::endl;
            return false;
        }
        double act_pos;
        bool start = false;

        // execute motion dependent on selected mode
        if (mode == "abs") {
            if (joint_control_mode[joint] == VOCAB_CM_POSITION) {
                // clamp to joint limits
                position = std::clamp(position, joint_min[joint], joint_max[joint]);
                // start motion
                start = ipos->positionMove(joint, position);
            } else {
                std::cerr << "[Joint Writer " << icub_part << "] Motion mode does not fit with control mode! Use 'position' control mode for 'abs' motion mode" << std::endl;
            }
        } else if (mode == "rel") {
            if (joint_control_mode[joint] == VOCAB_CM_POSITION) {
                // clamp to joint limits
                ienc->getEncoder(joint, &act_pos);
                double new_pos = act_pos + position;

                if (new_pos > joint_max[joint]) {
                    position = joint_max[joint] - act_pos;
                } else if (new_pos < joint_min[joint]) {
                    position = joint_min[joint] - act_pos;
                }
                // start motion
                start = ipos->relativeMove(joint, position);
            } else {
                std::cerr << "[Joint Writer " << icub_part << "] Motion mode does not fit with control mode! Use 'position' control mode for 'rel' motion mode" << std::endl;
            }
        } else if (mode == "vel") {
            if (joint_control_mode[joint] == VOCAB_CM_VELOCITY) {
                // clamp to joint limits
                position = std::clamp(position, -velocity_max, velocity_max);
                // start motion
                start = ivel->velocityMove(joint, position);
            } else {
                std::cerr << "[Joint Writer " << icub_part << "] Motion mode does not fit with control mode! Use 'velocity' control mode for 'vel' motion mode" << std::endl;
            }
        } else {
            std::cerr << "[Joint Writer " << icub_part << "] No valid motion mode is given. Possible options are 'abs' or 'rel' !" << std::endl;
        }
        // move joint blocking/non-blocking
        if (start) {
            if (blocking) {
                bool motion = false;
                while (!motion) {
                    if (!ipos->checkMotionDone(&motion)) {
                        std::cerr << "[Joint Writer " << icub_part << "] Communication error while moving occured!" << std::endl;
                        return false;
                    }
                }
            }
        } else {
            std::cerr << "[Joint Writer " << icub_part << "] Could not start motion!" << std::endl;
            return false;
        }
        return start;
    } else {
        return false;
    }
}

bool JointWriter::WritePopAll(std::vector<std::vector<double>> position_pops, std::string mode, bool blocking) {
    /*
        Write all joints with joint angles encoded in populations

        params: std::vector<std::vector<double>>    -- populations encoding every joint angle for writing them to the associated robot part
                string mode                         -- motion mode: absolute or relative
                bool blocking                       -- if True, function waits for end of motion

        return: bool                                -- return True, if successful
    */

    if (CheckInit()) {
        // Check population count
        if (position_pops.size() != joints) {
            std::cerr << "[Joint Writer " << icub_part << "] Invalid joint count in population input!" << std::endl;
            return false;
        }

        // execute motion dependent on selected mode
        bool start = false;
        if (mode == "abs") {
            // Decode positions from populations
            for (int i = 0; i < joints; i++) {
                joint_angles[i] = Decode(position_pops[i], i, neuron_deg_abs);
                if (std::isnan(joint_angles[i])) {
                    std::cerr << "[Joint Writer " << icub_part << "] Invalid joint angle in population code!" << std::endl;
                    return false;
                }
            }
            // start motion
            start = ipos->positionMove(joint_angles.data());
        } else if (mode == "rel") {
            // Decode positions from populations
            for (int i = 0; i < joints; i++) {
                joint_angles[i] = Decode(position_pops[i], i, neuron_deg_rel);
                if (std::isnan(joint_angles[i])) {
                    std::cerr << "[Joint Writer " << icub_part << "] Invalid joint angle in population code!" << std::endl;
                    return false;
                }
            }

            // clamp to joint limits
            std::vector<double> act_pos;
            act_pos.resize(joints);
            ienc->getEncoders(act_pos.data());
            for (int i = 0; i <= joints; i++) {
                double new_pos = act_pos[i] + joint_angles[i];
                if (new_pos > joint_max[i]) {
                    joint_angles[i] = joint_max[i] - act_pos[i];
                }
                if (new_pos < joint_min[i]) {
                    joint_angles[i] = joint_min[i] - act_pos[i];
                }
            }

            // start motion
            start = ipos->relativeMove(joint_angles.data());
        } else {
            std::cerr << "[Joint Writer " << icub_part << "] No valid motion mode is given. Possible options are 'abs' or 'rel' !" << std::endl;
        }

        // move joints blocking/non-blocking
        if (start) {
            if (blocking) {
                bool motion = false;
                while (!motion) {
                    if (!ipos->checkMotionDone(&motion)) {
                        std::cerr << "[Joint Writer " << icub_part << "] Communication error while moving occured!" << std::endl;
                        return false;
                    }
                }
            }
        }
        return start;
    } else {
        return false;
    }
}

bool JointWriter::WritePopMultiple(std::vector<std::vector<double>> position_pops, std::vector<int> joint_selection, std::string mode, bool blocking) {
    /*
        Write multiple joints with joint angles encoded in populations

        params: std::vector<std::vector<double>>    -- populations encoding every joint angle for writing them to the associated robot part
                std::vector<int> joint              -- joint selection of the robot part
                string mode                         -- motion mode: absolute or relative
                bool blocking                       -- if True, function waits for end of motion

        return: bool                                -- return True, if successful
    */

    if (CheckInit()) {
        // Check joint count
        if (joint_selection.size() > joints) {
            std::cerr << "[Joint Writer " << icub_part << "] Too many joints for the robot part!" << std::endl;
            return false;
        }

        if (joint_selection.size() != position_pops.size()) {
            std::cerr << "[Joint Writer " << icub_part << "] Position count and joint count does not fit together!" << std::endl;
            return false;
        }

        if (*(std::max_element(joint_selection.begin(), joint_selection.end())) >= joints) {
            std::cerr << "[Joint Writer " << icub_part << "] Maximum joint number is out of range!" << std::endl;
            return false;
        }

        // execute motion dependent on selected mode
        bool start = false;
        if (mode == "abs") {
            // Decode positions from populations
            for (unsigned int i = 0; i < joint_selection.size(); i++) {
                joint_angles[i] = Decode(position_pops[i], joint_selection[i], neuron_deg_abs);
                if (std::isnan(joint_angles[i])) {
                    std::cerr << "[Joint Writer " << icub_part << "] Invalid joint angle in population code!" << std::endl;
                    return false;
                }
            }
            // start motion
            start = ipos->positionMove(joint_selection.size(), joint_selection.data(), joint_angles.data());

        } else if (mode == "rel") {
            // Decode positions from populations
            for (unsigned int i = 0; i < joint_selection.size(); i++) {
                joint_angles[i] = Decode(position_pops[i], joint_selection[i], neuron_deg_rel);
                if (std::isnan(joint_angles[i])) {
                    std::cerr << "[Joint Writer " << icub_part << "] Invalid joint angle in population code!" << std::endl;
                    return false;
                }
            }
            // clamp to joint limits
            std::vector<double> act_pos;
            act_pos.resize(joints);
            ienc->getEncoders(act_pos.data());
            int i = 0;
            for (std::vector<int>::iterator it = joint_selection.begin(); it != joint_selection.end(); ++it) {
                double new_pos = act_pos[*it] + joint_angles[i];
                if (new_pos > joint_max[*it]) {
                    joint_angles[i] = joint_max[*it] - act_pos[*it];
                }
                if (new_pos < joint_min[*it]) {
                    joint_angles[i] = joint_min[*it] - act_pos[*it];
                }
                i++;
            }
            // start motion
            start = ipos->relativeMove(joint_selection.size(), joint_selection.data(), joint_angles.data());

        } else {
            std::cerr << "[Joint Writer " << icub_part << "] No valid motion mode is given. Possible options are 'abs' or 'rel' !" << std::endl;
        }

        // move joints blocking/non-blocking
        if (start) {
            if (blocking) {
                bool motion = false;
                while (!motion) {
                    if (!ipos->checkMotionDone(&motion)) {
                        std::cerr << "[Joint Writer " << icub_part << "] Communication error while moving occured!" << std::endl;
                        return false;
                    }
                }
            }
        }
        return start;
    } else {
        return false;
    }
}

bool JointWriter::WritePopOne(std::vector<double> position_pop, int joint, std::string mode, bool blocking) {
    /*
        Write one joint with the joint angle encoded in a population

        params: std::vector<double>     -- population encoded joint angle for writing to the robot joint
                int joint               -- joint number of the robot part
                string mode             -- motion mode: absolute or relative
                bool blocking           -- if True, function waits for end of motion

        return: bool                    -- return True, if successful
    */

    if (CheckInit()) {
        // Check joint number
        if (joint >= joints || joint < 0) {
            std::cerr << "[Joint Writer " << icub_part << "] Selected joint <" << joint << "> is out of range!" << std::endl;
            return false;
        }

        // execute motion dependent on selected mode
        bool start = false;
        if (mode == "abs") {
            // Decode absolute position from population
            double angle = Decode(position_pop, joint, neuron_deg_abs);
            if (std::isnan(angle)) {
                std::cerr << "[Joint Writer " << icub_part << "] Invalid joint angle in population code!" << std::endl;
                return false;
            }
            // start motion
            start = ipos->positionMove(joint, angle);
        } else if (mode == "rel") {
            // Decode relative position from population
            double angle = Decode(position_pop, joint, neuron_deg_rel);
            if (std::isnan(angle)) {
                std::cerr << "[Joint Writer " << icub_part << "] Invalid joint angle in population code!" << std::endl;
                return false;
            }

            // clamp to joint limits
            double act_pos;
            ienc->getEncoder(joint, &act_pos);
            double new_pos = act_pos + angle;
            if (new_pos > joint_max[joint]) {
                angle = joint_max[joint] - act_pos;
            }
            if (new_pos < joint_min[joint]) {
                angle = joint_min[joint] - act_pos;
            }

            // start motion
            start = ipos->relativeMove(joint, angle);
        } else {
            std::cerr << "[Joint Writer " << icub_part << "] No valid motion mode is given. Possible options are 'abs' or 'rel' !" << std::endl;
        }

        // move joint blocking/non-blocking
        if (start) {
            if (blocking) {
                bool motion = false;
                while (!motion) {
                    if (!ipos->checkMotionDone(&motion)) {
                        std::cerr << "[Joint Writer " << icub_part << "] Communication error while moving occured!" << std::endl;
                        return false;
                    }
                }
            }
        }
        return start;
    } else {
        return false;
    }
}

double JointWriter::Decode_ext(std::vector<double> position_pop, int joint) { return Decode(position_pop, joint, neuron_deg_abs); }

/*** gRPC related functions ***/
#ifdef _USE_GRPC
void JointWriter::Retrieve_ANNarchy_Input_SJ() { joint_value = joint_source->retrieve_singletarget(); }
void JointWriter::Write_ANNarchy_Input_SJ() { WriteDoubleOne(joint_value, _joint_select[0], _mode, _blocking); }

void JointWriter::Retrieve_ANNarchy_Input_SJ_enc() { joint_value_1dvector = joint_source->retrieve_singletarget_enc(); }
void JointWriter::Write_ANNarchy_Input_SJ_enc() { WritePopOne(joint_value_1dvector, _joint_select[0], _mode, _blocking); }

void JointWriter::Retrieve_ANNarchy_Input_MJ() { joint_value_1dvector = joint_source->retrieve_multitarget(); }
void JointWriter::Write_ANNarchy_Input_MJ() { WriteDoubleMultiple(joint_value_1dvector, _joint_select, _mode, _blocking); }

void JointWriter::Retrieve_ANNarchy_Input_MJ_enc() {
    joint_value_1dvector = joint_source->retrieve_multitarget_enc();
    for (unsigned int i = 0; i < joint_value_1dvector.size(); i += pop_size) {
        joint_value_2dvector.push_back(std::vector<double>((joint_value_1dvector.begin() + i), (joint_value_1dvector.begin() + i + pop_size + 1)));
    }
}
void JointWriter::Write_ANNarchy_Input_MJ_enc() { WritePopMultiple(joint_value_2dvector, _joint_select, _mode, _blocking); }

void JointWriter::Retrieve_ANNarchy_Input_AJ() { joint_value_1dvector = joint_source->retrieve_alltarget(); }
void JointWriter::Write_ANNarchy_Input_AJ() { WriteDoubleAll(joint_value_1dvector, _mode, _blocking); }

void JointWriter::Retrieve_ANNarchy_Input_AJ_enc() {
    joint_value_1dvector = joint_source->retrieve_alltarget_enc();
    for (unsigned int i = 0; i < joint_value_1dvector.size(); i += pop_size) {
        joint_value_2dvector.push_back(std::vector<double>((joint_value_1dvector.begin() + i), (joint_value_1dvector.begin() + i + pop_size + 1)));
    }
}
void JointWriter::Write_ANNarchy_Input_AJ_enc() { WritePopAll(joint_value_2dvector, _mode, _blocking); }
#else
void JointWriter::Retrieve_ANNarchy_Input_SJ() { std::cerr << "[Joint Writer] gRPC is not included in the setup process!" << std::endl; }
void JointWriter::Write_ANNarchy_Input_SJ() { std::cerr << "[Joint Writer] gRPC is not included in the setup process!" << std::endl; }

void JointWriter::Retrieve_ANNarchy_Input_SJ_enc() { std::cerr << "[Joint Writer] gRPC is not included in the setup process!" << std::endl; }
void JointWriter::Write_ANNarchy_Input_SJ_enc() { std::cerr << "[Joint Writer] gRPC is not included in the setup process!" << std::endl; }

void JointWriter::Retrieve_ANNarchy_Input_MJ() { std::cerr << "[Joint Writer] gRPC is not included in the setup process!" << std::endl; }
void JointWriter::Write_ANNarchy_Input_MJ() { std::cerr << "[Joint Writer] gRPC is not included in the setup process!" << std::endl; }

void JointWriter::Retrieve_ANNarchy_Input_MJ_enc() { std::cerr << "[Joint Writer] gRPC is not included in the setup process!" << std::endl; }
void JointWriter::Write_ANNarchy_Input_MJ_enc() { std::cerr << "[Joint Writer] gRPC is not included in the setup process!" << std::endl; }

void JointWriter::Retrieve_ANNarchy_Input_AJ() { std::cerr << "[Joint Writer] gRPC is not included in the setup process!" << std::endl; }
void JointWriter::Write_ANNarchy_Input_AJ() { std::cerr << "[Joint Writer] gRPC is not included in the setup process!" << std::endl; }

void JointWriter::Retrieve_ANNarchy_Input_AJ_enc() { std::cerr << "[Joint Writer] gRPC is not included in the setup process!" << std::endl; }
void JointWriter::Write_ANNarchy_Input_AJ_enc() { std::cerr << "[Joint Writer] gRPC is not included in the setup process!" << std::endl; }
#endif

/*** auxilary methods ***/
bool JointWriter::CheckPartKey(std::string key) {
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

double JointWriter::Decode(std::vector<double> position_pop, int joint, std::vector<std::vector<double>> neuron_deg) {
    /*
        Decode the population coded joint angle to double value

        params: std::vector<double>             -- population encoded joint angle
                int joint                       -- joint number of the robot part

        return: double joint_angle              -- decoded joint angle
    */

    double sum_pop_w = 0;
    double sum_pop = 0;
    for (unsigned int i = 0; i < position_pop.size(); i++) {
        sum_pop_w = sum_pop_w + position_pop[i] * neuron_deg[joint][i];
        sum_pop = sum_pop + position_pop[i];
    }
    return sum_pop_w / sum_pop;
}

bool JointWriter::MotionDone() {
    bool test;
    ipos->checkMotionDone(&test);
    return test;
}

template <typename T>
std::string JointWriter::vec2string(const T &vec) {
    std::stringstream stream;
    for (size_t i = 0; i < vec.size(); ++i) {
        if (i != 0) stream << ",";
        stream << vec[i];
    }
    return stream.str();
}