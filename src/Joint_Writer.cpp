/*
 *  Copyright (C) 2019 Torsten Follak
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

#include <yarp/dev/all.h>
#include <yarp/os/all.h>
#include <yarp/sig/all.h>

#include <algorithm>
#include <iostream>
#include <string>

#include "INI_Reader/INIReader.h"
#include "Joint_Writer.hpp"

// Destructor
JointWriter::~JointWriter() { Close(); }

/*** public methods for the user ***/
bool JointWriter::Init(std::string part, int pop_size, double deg_per_neuron, double speed) {
    /*
        Initialize the joint writer with given parameters

        params: std::string part        -- string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso}
                int pop_size            -- number of neurons per population, encoding each one joint angle; only works if parameter "deg_per_neuron" is not set
                double deg_per_neuron   -- degree per neuron in the populations, encoding the joints angles; if set: population size depends on joint working range
                double speed            -- velocity for the joint motions

        return: bool                    -- return True, if successful
    */

    if (!dev_init) {
        // Check validity of the iCub part key
        if (!CheckPartKey(part)) {
            std::cerr << "[Joint Writer] " << part << " is an invalid iCub part key!" << std::endl;
            return false;
        }

        // Check validity of the population size
        icub_part = part;
        if (pop_size < 0) {
            std::cerr << "[Joint Writer " << icub_part << "] Population size must be positive!" << std::endl;
            return false;
        }

        // Check Yarp-network
        yarp::os::Network::init();
        if (!yarp::os::Network::checkNetwork()) {
            std::cerr << "[Joint Writer " << icub_part << "] YARP Network is not online. Check nameserver is running!" << std::endl;
            return false;
        }

        // setup iCub joint position control
        yarp::os::Property options;
        options.put("device", "remote_controlboard");
        options.put("remote", ("/icubSim/" + icub_part).c_str());
        options.put("local", ("/ANNarchy_write/" + icub_part).c_str());

        if (!driver.open(options)) {
            std::cerr << "[Joint Writer " << icub_part << "] Unable to open" << options.find("device").asString() << "!" << std::endl;
            return false;
        }
        driver.view(ipos);
        ipos->getAxes(&joints);

        // resize vector for saving joint parameter
        joint_angles.resize(joints);
        neuron_deg_abs.resize(joints);
        neuron_deg_rel.resize(joints);
        joint_deg_res_abs.resize(joints);
        joint_deg_res_rel.resize(joints);

        // setup ini-Reader for joint limits
        double joint_range;
        INIReader reader("data/joint_limits.ini");

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
            joint_range = joint_max[i] - joint_min[i];
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
        dev_init = true;
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

    if (CheckInit()) {
        driver.close();
    }
    yarp::os::Network::fini();
    dev_init = false;
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

        for (int i = 0; i < position.size(); i++) {
            position[i] = std::clamp(position[i], joint_min[i], joint_max[i]);
        }

        // execute motion dependent on selected mode
        bool start = false;
        if (mode == "abs") {
            start = ipos->positionMove(position.data());
        } else if (mode == "rel") {
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
        if (joint_selection.size() < joints) {
            std::cerr << "[Joint Writer " << icub_part << "] To many joints for the robot part!" << std::endl;
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

        for (int i = 0; i < position.size(); i++) {
            position[i] = std::clamp(position[i], joint_min[joint_selection[i]], joint_max[joint_selection[i]]);
        }

        // execute motion dependent on selected mode
        bool start = false;
        if (mode == "abs") {
            start = ipos->positionMove(joint_selection.size(), joint_selection.data(), position.data());
        } else if (mode == "rel") {
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
        
        params: double position     -- joint angle to write to the robot joint
                int joint           -- joint number of the robot part
                bool blocking       -- if True, function waits for end of motion
                string mode         -- motion mode: absolute or relative

        return: bool                -- return True, if successful
    */

    if (CheckInit()) {
        // Check joint number
        if (joint >= joints || joint < 0) {
            std::cerr << "[Joint Writer " << icub_part << "] Selected joint out of range!" << std::endl;
            return false;
        }

        position = std::clamp(position, joint_min[joint], joint_max[joint]);

        // execute motion dependent on selected mode
        bool start = false;
        if (mode == "abs") {
            start = ipos->positionMove(joint, position);
        } else if (mode == "rel") {
            start = ipos->relativeMove(joint, position);
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
        Write all joints with joint angles encoded in populations

        params: std::vector<std::vector<double>>    -- populations encoding every joint angle for writing them to the associated robot part
                bool blocking                       -- if True, function waits for end of motion
                string mode                         -- motion mode: absolute or relative

        return: bool                                -- return True, if successful
    */

    if (CheckInit()) {
        // Check joint count
        if (joint_selection.size() < joints) {
            std::cerr << "[Joint Writer " << icub_part << "] To many joints for the robot part!" << std::endl;
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
            for (int i = 0; i < joints; i++) {
                joint_angles[i] = Decode(position_pops[i], i, neuron_deg_abs);
                if (std::isnan(joint_angles[i])) {
                    std::cerr << "[Joint Writer " << icub_part << "] Invalid joint angle in population code!" << std::endl;
                    return false;
                }
            }
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
            start = ipos->positionMove(joint, angle);
        } else if (mode == "rel") {
            // Decode relative position from population
            double angle = Decode(position_pop, joint, neuron_deg_rel);
            if (std::isnan(angle)) {
                std::cerr << "[Joint Writer " << icub_part << "] Invalid joint angle in population code!" << std::endl;
                return false;
            }
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
bool JointWriter::CheckInit() {
    /* 
        Helper function to check if init function was called
    */

    if (!dev_init) {
        std::cerr << "[Joint Writer] Error: Device is not initialized!" << std::endl;
    }
    return dev_init;
}

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
