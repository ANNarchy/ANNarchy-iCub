/*
 *  Copyright (C) 2019-2021 Torsten Fietzek
 *
 *  Joint_Writer.cpp is part of the iCub ANNarchy interface
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

#include "Joint_Writer.hpp"

#include <yarp/dev/all.h>
#include <yarp/os/all.h>
#include <yarp/sig/all.h>

#include <algorithm>
#include <boost/algorithm/string.hpp>
#include <iostream>
#include <string>

#include "INI_Reader/INIReader.h"

// Destructor
JointWriter::~JointWriter() { Close(); }

/*** public methods for the user ***/
bool JointWriter::Init(std::string part, int pop_size, double deg_per_neuron, double speed, std::string ini_path) {
    /*
        Initialize the joint writer with given parameters

        params: std::string part        -- string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso}
                int pop_size            -- number of neurons per population, encoding each one joint angle; only works if parameter "deg_per_neuron" is not set
                double deg_per_neuron   -- degree per neuron in the populations, encoding the joints angles; if set: population size depends on joint working range
                double speed            -- velocity for the joint motions
                ini_path                -- Path to the "interface_param.ini"-file

        return: bool                    -- return True, if successful
    */

    if (!getDevInit()) {
        // Check validity of the iCub part key
        if (!CheckPartKey(part)) {
            std::cerr << "[Joint Writer] " << part << " is an invalid iCub part key!" << std::endl;
            return false;
        }

        // Check validity of the population size
        icub_part = part;
        setType("Joint Writer", icub_part);
        if (pop_size < 0) {
            std::cerr << "[Joint Writer " << icub_part << "] Population size have to be positive!" << std::endl;
            return false;
        }

        // Check Yarp-network
        if (!yarp::os::Network::checkNetwork()) {
            std::cerr << "[Joint Writer " << icub_part << "] YARP Network is not online. Check nameserver is running!" << std::endl;
            return false;
        }

        // read configuration data from ini file
        INIReader reader_gen(ini_path + "interface_param.ini");
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

        if (!driver.view(ipos) || !driver.view(ienc) || !driver.view(ivel) || !driver.view(icont)) {
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

        // setup ini-Reader for joint limits
        double joint_range;
        std::string joint_path;
        if (on_Simulator) {
            joint_path = reader_gen.Get("motor", "sim_joint_limits_path", "");
        } else {
            joint_path = reader_gen.Get("motor", "robot_joint_limits_path", "");
        }

        if (joint_path == "") {
            std::cerr << "[Joint Writer " << icub_part << "] Ini-path for joint limits is empty!" << std::endl;
            return false;
        }
        INIReader reader(joint_path);

        for (int i = 0; i < joints; i++) {
            // set joint velocity
            if (speed > 0 && speed <= velocity_max) {
                ipos->setRefSpeed(i, speed);
            }

            // read joint limits
            joint_min.push_back(reader.GetReal(icub_part.c_str(), ("joint_" + std::to_string(i) + "_min").c_str(), 0.0));
            joint_max.push_back(reader.GetReal(icub_part.c_str(), ("joint_" + std::to_string(i) + "_max").c_str(), 0.0));

            // printf("joint: %i, min: %f, max: %f\n", i, joint_min[i], joint_max[i]);

            if (joint_min[i] == joint_max[i]) {
                std::cerr << "[Joint Writer " << icub_part << "] Error in reading joint parameters from .ini file " << std::endl;
                driver.close();
                return false;
            }

            // compute population code resolution
            joint_range = joint_max[i] - joint_min[i] + 1;
            if (pop_size > 0) {    // with given population size
                // absolute joint angles
                neuron_deg_abs[i].resize(pop_size);
                joint_deg_res_abs[i] = joint_range / pop_size;

                for (int j = 0; j < neuron_deg_abs[i].size(); j++) {
                    neuron_deg_abs[i][j] = joint_min[i] + j * joint_deg_res_abs[i];
                }
                // relative joint angles
                neuron_deg_rel[i].resize(pop_size);
                joint_deg_res_rel[i] = 2 * joint_range / pop_size;

                for (int j = 0; j < neuron_deg_rel[i].size(); j++) {
                    neuron_deg_rel[i][j] = -joint_range + j * joint_deg_res_rel[i];
                }
            } else if (deg_per_neuron > 0.0) {    // with given neuron resolution
                // absolute joint angles
                int joint_res = std::floor(joint_range / deg_per_neuron);
                neuron_deg_abs[i].resize(joint_res);
                joint_deg_res_abs[i] = deg_per_neuron;

                for (int j = 0; j < neuron_deg_abs[i].size(); j++) {
                    neuron_deg_abs[i][j] = joint_min[i] + j * deg_per_neuron;
                }
                // relative joint angles
                joint_res = std::floor(2 * joint_range / deg_per_neuron);
                neuron_deg_rel[i].resize(joint_res);
                joint_deg_res_rel[i] = deg_per_neuron;

                for (int j = 0; j < neuron_deg_rel[i].size(); j++) {
                    neuron_deg_rel[i][j] = -joint_range + j * deg_per_neuron;
                }
            } else {
                std::cerr << "[Joint Reader " << icub_part
                          << "] Error in population size definition. Check the values for pop_size or deg_per_neuron!" << std::endl;
                driver.close();
                return false;
            }
        }
        setDevInit(true);
        return true;
    } else {
        std::cerr << "[Joint Writer " << icub_part << "] Initialization aready done!" << std::endl;
        return false;
    }
}

void JointWriter::Close() {
    /*
        Close joint writer with cleanup
    */
    if (driver.isValid()) {
        driver.close();
    }
    setDevInit(false);
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

std::vector<int> JointWriter::GetNeuronsPerJoint() {
    /*
        Get the size of the populations, encoding the joint angles

        return: std::vector<int>        -- return vector, containing the population size for every joint
    */

    std::vector<int> neuron_counts(joints);
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

bool JointWriter::SetJointControlMode(std::string control_mode, int joint) {
    if (joint >= joints || joint < -1) {
        std::cerr << "[Joint Writer " << icub_part << "] Selected joint out of range!" << std::endl;
        return false;
    }
    if (joint < 0) {
        for (int i = 0; i < joints; i++) {
            // set control modes
            boost::algorithm::to_lower(control_mode);
            if (control_mode == "position") {
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
        boost::algorithm::to_lower(control_mode);
        if (control_mode == "position") {
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

bool JointWriter::WriteDoubleAll(std::vector<double> position, bool blocking, std::string mode) {
    /*
        Write all joints with double values

        params: double position     -- joint angles to write to the robot joints
                bool blocking       -- if True, function waits for end of motion
                string mode         -- motion mode: absolute or relative

        return: bool                -- return True, if successful
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
            for (int i = 0; i < position.size(); i++) {
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
        } else {
            std::cerr << "[Joint Writer " << icub_part << "] No valid motion mode is given. Possible options are 'abs' or 'rel' !"
                      << std::endl;
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

bool JointWriter::WriteDoubleMultiple(std::vector<double> position, std::vector<int> joint_selection, bool blocking, std::string mode) {
    /*
        Write multiple joints with double values

        params: double position     -- joint angles to write to the robot joints
                bool blocking       -- if True, function waits for end of motion
                string mode         -- motion mode: absolute or relative

        return: bool                -- return True, if successful
    */

    if (CheckInit()) {
        // Check joint count
        if (joint_selection.size() > joints) {
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

        // execute motion dependent on selected mode
        bool start = false;
        if (mode == "abs") {
            // clamp to joint limits
            for (int i = 0; i < position.size(); i++) {
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
        } else {
            std::cerr << "[Joint Writer " << icub_part << "] No valid motion mode is given. Possible options are 'abs' or 'rel' !"
                      << std::endl;
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

bool JointWriter::WriteDoubleOne(double position, int joint, bool blocking, std::string mode) {
    /*
        Write one joint with double value

        params: double position     -- joint angle or velocity to write to the robot joint
                int joint           -- joint number of the robot part
                bool blocking       -- if True, function waits for end of motion
                string mode         -- motion mode: absolute, relative or velocity

        return: bool                -- return True, if successful
    */

    if (CheckInit()) {
        // Check joint number
        if (joint >= joints || joint < 0) {
            std::cerr << "[Joint Writer " << icub_part << "] Selected joint out of range!" << std::endl;
            return false;
        }
        double act_pos;

        // execute motion dependent on selected mode
        bool start = false;
        if (mode == "abs") {
            if (joint_control_mode[joint] == VOCAB_CM_POSITION) {
                // clamp to joint limits
                position = std::clamp(position, joint_min[joint], joint_max[joint]);
                // start motion
                start = ipos->positionMove(joint, position);
            } else {
                std::cerr << "[Joint Writer " << icub_part
                          << "] Motion mode does not fit with control mode! Use 'position' control mode for 'abs' motion mode" << std::endl;
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
                std::cerr << "[Joint Writer " << icub_part
                          << "] Motion mode does not fit with control mode! Use 'position' control mode for 'rel' motion mode" << std::endl;
            }
        } else if (mode == "vel") {
            if (joint_control_mode[joint] == VOCAB_CM_VELOCITY) {
                // clamp to joint limits
                position = std::clamp(position, -50., 50.);
                // start motion
                start = ivel->velocityMove(joint, position);
            } else {
                std::cerr << "[Joint Writer " << icub_part
                          << "] Motion mode does not fit with control mode! Use 'velocity' control mode for 'vel' motion mode" << std::endl;
            }
        } else {
            std::cerr << "[Joint Writer " << icub_part << "] No valid motion mode is given. Possible options are 'abs' or 'rel' !"
                      << std::endl;
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

bool JointWriter::WritePopAll(std::vector<std::vector<double>> position_pops, bool blocking, std::string mode) {
    /*
        Write all joints with joint angles encoded in populations

        params: std::vector<std::vector<double>>    -- populations encoding every joint angle for writing them to the associated robot part
                bool blocking                       -- if True, function waits for end of motion
                string mode                         -- motion mode: absolute or relative

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
            std::cerr << "[Joint Writer " << icub_part << "] No valid motion mode is given. Possible options are 'abs' or 'rel' !"
                      << std::endl;
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

bool JointWriter::WritePopMultiple(std::vector<std::vector<double>> position_pops, std::vector<int> joint_selection, bool blocking,
                                   std::string mode) {
    /*
        Write multiple joints with joint angles encoded in populations

        params: std::vector<std::vector<double>>    -- populations encoding every joint angle for writing them to the associated robot part
                bool blocking                       -- if True, function waits for end of motion
                string mode                         -- motion mode: absolute or relative

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
            for (int i = 0; i < joint_selection.size(); i++) {
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
            for (int i = 0; i < joint_selection.size(); i++) {
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
            std::cerr << "[Joint Writer " << icub_part << "] No valid motion mode is given. Possible options are 'abs' or 'rel' !"
                      << std::endl;
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

bool JointWriter::WritePopOne(std::vector<double> position_pop, int joint, bool blocking, std::string mode) {
    /*
        Write one joint with the joint angle encoded in a population

        params: std::vector<double>     -- population encoded joint angle for writing to the robot joint
                int joint               -- joint number of the robot part
                bool blocking           -- if True, function waits for end of motion
                string mode             -- motion mode: absolute or relative

        return: bool                    -- return True, if successful
    */

    if (CheckInit()) {
        // Check joint number
        if (joint >= joints || joint < 0) {
            std::cerr << "[Joint Writer " << icub_part << "] Selected joint is out of range!" << std::endl;
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
            std::cerr << "[Joint Writer " << icub_part << "] No valid motion mode is given. Possible options are 'abs' or 'rel' !"
                      << std::endl;
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

    int size = position_pop.size();
    double sum_pop_w = 0;
    double sum_pop = 0;
    for (int i = 0; i < size; i++) {
        sum_pop_w = sum_pop_w + position_pop[i] * neuron_deg[joint][i];
        sum_pop = sum_pop + position_pop[i];
    }
    double joint_angle = sum_pop_w / sum_pop;

    return joint_angle;
}

bool JointWriter::MotionDone() {
    bool test;
    ipos->checkMotionDone(&test);
    return test;
}