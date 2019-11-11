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

#include <iostream>
#include <string>

#include "INI_Reader/INIReader.h"
#include "Joint_Writer.hpp"

// Destructor
JointWriter::~JointWriter() {}

// initialize the joint writer with given parameters
bool JointWriter::Init(std::string part, int pop_size, double deg_per_neuron)
/*
    params: std::string part        -- string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso}
            int pop_size            -- number of neurons per population, encoding each one joint angle; only works if parameter "deg_per_neuron" is not set
            double deg_per_neuron   -- degree per neuron in the populations, encoding the joints angles; if set: population size depends on joint working range

    return: bool                    -- return True, if successful
*/
{
    if (!dev_init) {
        icub_part = part;

        yarp::os::Network::init();
        if (!yarp::os::Network::checkNetwork()) {
            std::cerr << "[Joint Writer " << icub_part << "] YARP Network is not online. Check nameserver is running" << std::endl;
            return false;
        }

        yarp::os::Property options;
        options.put("device", "remote_controlboard");
        options.put("remote", ("/icubSim/" + icub_part).c_str());
        options.put("local", ("/ANNarchy_write/" + icub_part).c_str());

        if (!driver.open(options)) {
            std::cerr << "[Joint Writer " << icub_part << "] Unable to open" << options.find("device").asString() << std::endl;
            return false;
        }

        driver.view(ipos);
        ipos->getAxes(&joints);
        joint_angles.resize(joints);
        neuron_deg.resize(joints);
        joint_deg_res.resize(joints);

        double joint_range;
        INIReader reader("data/joint_limits.ini");

        for (int i = 0; i < joints; i++) {
            joint_min.push_back(reader.GetReal(icub_part.c_str(), ("joint_" + std::to_string(i) + "_min").c_str(), 0.0));
            joint_max.push_back(reader.GetReal(icub_part.c_str(), ("joint_" + std::to_string(i) + "_max").c_str(), 0.0));

            // printf("joint: %i, min: %f, max: %f\n", i, joint_min[i], joint_max[i]);

            if (joint_min == joint_max) {
                std::cerr << "[Joint Writer " << icub_part << "] Error in reading joint parameters from .ini file " << std::endl;
                return false;
            }

            joint_range = joint_max[i] - joint_min[i];

            if (deg_per_neuron > 0.0) {
                joint_res = std::floor(joint_range / deg_per_neuron);
                neuron_deg[i].resize(joint_res);
                joint_deg_res[i] = deg_per_neuron;

                for (int j = 0; j < neuron_deg[i].size(); j++) {
                    neuron_deg[i][j] = joint_min[i] + j * deg_per_neuron;
                }
            } else if (pop_size > 0) {
                neuron_deg[i].resize(pop_size);
                joint_deg_res[i] = joint_range / pop_size;

                for (int j = 0; j < neuron_deg[i].size(); j++) {
                    neuron_deg[i][j] = joint_min[i] + j * joint_deg_res[i];
                }
            } else {
                std::cerr << "[Joint Reader " << icub_part << "] Error in population size definition" << std::endl;
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

// helper function to check if init function was called
bool JointWriter::CheckInit() {
    if (!dev_init) {
        std::cerr << "[Joint Writer] Error: Device is not initialized" << std::endl;
    }
    return dev_init;
}

// get the size of the populations encoding the joint angles
std::vector<int> JointWriter::GetNeuronsPerJoint()
/*
  return: std::vector<int>        -- return vector, containing the population size for every joint
*/
{
    std::vector<int> neuron_counts(joints);
    if (CheckInit()) {
        for (int i = 0; i < joints; i++) {
            neuron_counts[i] = neuron_deg[i].size();
        }
    }
    return neuron_counts;
}

// get the resolution in degree of the populations encoding the joint angles
std::vector<double> JointWriter::GetJointsDegRes()
/*
  return: std::vector<double>        -- return vector, containing the resolution for every joints population codimg in degree
*/
{
    CheckInit();
    return joint_deg_res;
}

// decode the population coded joint angle to double value
double JointWriter::Decode(std::vector<double> position_pop, int joint)
/*
    params: std::vector<double>             -- population encoded joint angle
            int joint                       -- joint number of the robot part

    return: double joint_angle              -- decoded joint angle
*/
{
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

// write one joint as double value
bool JointWriter::WriteDouble(double position, int joint, bool blocking)
/*
    params: double position     -- joint angle to write to the robot joint
            int joint           -- joint number of the robot part
            bool blocking       -- if True, function waits for end of movement

    return: bool                -- return True, if successful
*/
{
    if (CheckInit()) {
        if (joint >= joints) {
            std::cerr << "[Joint Writer " << icub_part << "] Selected joint out of range" << std::endl;
            return false;
        }
        if (blocking) {
            auto start = ipos->positionMove(joint, position);
            if (start) {
                bool motion = false;
                while (!motion) {
                    if (!ipos->checkMotionDone(&motion)) {
                        std::cerr << "[Joint Writer " << icub_part << "] Communication error while moving" << std::endl;
                        return false;
                    }
                }
            }
            return start;
        } else {
            return ipos->positionMove(joint, position);
        }
    } else {
        return false;
    }
}

// write one joint with the joint angle encoded in a population
bool JointWriter::WriteOne(std::vector<double> position_pop, int joint, bool blocking)
/*
    params: std::vector<double>     -- population encoded joint angle for writing to the robot joint
            int joint               -- joint number of the robot part
            bool blocking           -- if True, function waits for end of movement

    return: bool                    -- return True, if successful
*/
{
    if (CheckInit()) {
        if (joint >= joints) {
            std::cerr << "[Joint Writer " << icub_part << "] Selected joint out of range" << std::endl;
            return false;
        }
        double angle = Decode(position_pop, joint);
        if (blocking) {
            bool start = ipos->positionMove(joint, angle);
            if (start) {
                bool motion = false;
                while (!motion) {
                    if (!ipos->checkMotionDone(&motion)) {
                        std::cerr << "[Joint Writer " << icub_part << "] Communication error while moving" << std::endl;
                        return false;
                    }
                }
            }
            return start;
        } else {
            return ipos->positionMove(joint, angle);
        }
    } else {
        return false;
    }
}

// write all joints with joint angles encoded in populations
bool JointWriter::WriteAll(std::vector<std::vector<double>> position_pops, bool blocking)
/*
    params: std::vector<std::vector<double>>    -- populations encoding every joint angle for writing them to the associated robot part
            bool blocking                       -- if True, function waits for end of movement

    return: bool                                -- return True, if successful
*/
{
    if (CheckInit()) {
        if (position_pops.size() != joints) {
            std::cerr << "[Joint Writer " << icub_part << "] Wrong joint count in population input" << std::endl;
            return false;
        }

        for (int i = 0; i < joints; i++) {
            joint_angles[i] = Decode(position_pops[i], i);
        }

        if (blocking) {
            auto start = ipos->positionMove(joint_angles.data());
            if (start) {
                bool motion = false;
                while (!motion) {
                    if (!ipos->checkMotionDone(&motion)) {
                        std::cerr << "[Joint Writer " << icub_part << "] Communication error while moving" << std::endl;
                        return false;
                    }
                }
            }
            return start;
        } else {
            return ipos->positionMove(joint_angles.data());
        }
    } else {
        return false;
    }
}

// close joint reader with cleanup
void JointWriter::Close() {
    if (CheckInit()) {
        driver.close();
    }
    yarp::os::Network::fini();
}
