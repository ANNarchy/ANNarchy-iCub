/*
 *  Copyright (C) 2019 Torsten Follak
 *
 *  JointReader.cpp is part of the iCub ANNarchy interface
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
#include "Joint_Reader.hpp"

// Destructor
JointReader::~JointReader() {}

// initialize the joint reader with given parameters
bool JointReader::Init(std::string part, double sigma, int pop_size, double deg_per_neuron)
/*
    params: std::string part        -- string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso}
            sigma                   -- sigma for the joints angles populations coding 
            int pop_size            -- number of neurons per population, encoding each one joint angle; only works if parameter "deg_per_neuron" is not set
            double deg_per_neuron   -- degree per neuron in the populations, encoding the joints angles; if set: population size depends on joint working range

    return: bool                    -- return True, if successful
*/
{
    if (!dev_init) {
        icub_part = part;
        sigma_pop = sigma;
        yarp::os::Network::init();
        if (!yarp::os::Network::checkNetwork()) {
            std::cerr << "[Joint Reader " << icub_part << "] YARP Network is not online. Check nameserver is running" << std::endl;
            return false;
        }

        yarp::os::Property options;
        options.put("device", "remote_controlboard");
        options.put("remote", ("/icubSim/" + icub_part).c_str());
        options.put("local", ("/ANNarchy_read/" + icub_part).c_str());

        if (!driver.open(options)) {
            std::cerr << "[Joint Reader " << icub_part << "] Unable to open " << options.find("device").asString() << std::endl;
            return false;
        }

        driver.view(ienc);
        ienc->getAxes(&joints);
        joint_angles.resize(joints);
        neuron_deg.resize(joints);
        joint_deg_res.resize(joints);

        double joint_range;
        INIReader reader("data/joint_limits.ini");

        for (int i = 0; i < joints; i++) {
            joint_min.push_back(reader.GetReal(icub_part.c_str(), ("joint_" + std::to_string(i) + "_min").c_str(), 0.0));
            joint_max.push_back(reader.GetReal(icub_part.c_str(), ("joint_" + std::to_string(i) + "_max").c_str(), 0.0));

            // printf("joint: %i, min: %f, max: %f \n", i, joint_min[i], joint_max[i]);

            if (joint_min == joint_max) {
                std::cerr << "[Joint Reader " << icub_part << "] Error in reading joint parameters from .ini file" << std::endl;
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
        std::cerr << "[Joint Reader " << icub_part << "] Initialization aready done!" << std::endl;
        return false;
    }
}

// check if init function was called
bool JointReader::CheckInit() {
    if (!dev_init) {
        std::cerr << "[Joint Reader] Error: Device is not initialized" << std::endl;
    }
    return dev_init;
}

// get the size of the populations encoding the joint angles
std::vector<int> JointReader::GetNeuronsPerJoint()
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
std::vector<double> JointReader::GetJointsDegRes()
/*
  return: std::vector<double>        -- return vector, containing the resolution for every joints population codimg in degree
*/
{
    CheckInit();
    return joint_deg_res;
}

// return the normal distribution value for a given value, mean and sigma
double JointReader::NormalPdf(double value, double mean, double sigma)
/*
    params: double value            -- value to calculate normal distribution at
            double mean             -- mean of the normal distribution
            double sigma            -- sigma of the normal distribution

    return: double                  -- function value for the normal distribution
*/
{
    double inv_sqrt_2pi = 1 / (sigma * std::sqrt(2 * M_PI));
    double a = (value - mean) / sigma;

    return inv_sqrt_2pi * std::exp(-0.5 * a * a);
}

// encode joint position into a vector
std::vector<double> JointReader::Encode(double joint_angle, int joint)
/*
    params: double joint_angle              -- joint angle read from the robot
            int joint                       -- joint number of the robot part

    return: std::vector<double>             -- population encoded joint angle
*/
{
    int size = neuron_deg.at(joint).size();
    std::vector<double> pos_pop(size);

    for (int i = 0; i < size; i++) {
        pos_pop[i] = (NormalPdf(neuron_deg[joint][i], joint_angle, sigma_pop));
    }

    return pos_pop;
}

// read one joint and return joint angle directly as double value
double JointReader::ReadDouble(int joint)
/*
    params: int joint       -- joint number of the robot part

    return: double          -- joint angle read from the robot
*/
{
    double angle = 0.0;
    if (CheckInit()) {
        if (joint >= joints) {
            std::cerr << "[Joint Reader " << icub_part << "] Selected joint out of range" << std::endl;
        }
        if (!ienc->getEncoder(joint, &angle)) {
            std::cerr << "[Joint Reader " << icub_part << "] Error in reading joint angle from iCub" << std::endl;
        }
    }
    return angle;
}

// read one joint and return the joint angle encoded in a vector
std::vector<double> JointReader::ReadOne(int joint)
/*
    params: int joint               -- joint number of the robot part

    return: std::vector<double>     -- population vector encoding the joint angle
*/
{
    std::vector<double> angle_pop;
    if (CheckInit()) {
        if (joint >= joints) {
            std::cerr << "[Joint Reader " << icub_part << "] Selected joint out of range" << std::endl;
        }

        double angle;
        if (!ienc->getEncoder(joint, &angle)) {
            std::cerr << "[Joint Reader " << icub_part << "] Error in reading joint angle from iCub" << std::endl;
        }
        angle_pop = Encode(angle, joint);
    }
    return angle_pop;
}

// read all joints and return the joint angles encoded in vectors
std::vector<std::vector<double>> JointReader::ReadAll()
/*
    return: std::vector<std::vector<double>>    -- vector of population vectors encoding every joint angle from associated robot part
*/
{
    std::vector<std::vector<double>> angle_pops;
    if (CheckInit()) {
        double angles[joints];
        if (!ienc->getEncoders(angles)) {
            std::cerr << "[Joint Reader " << icub_part << "] Error in reading joint angle from iCub" << std::endl;
        }
        for (int i = 0; i < joints; i++) {
            angle_pops[i] = Encode(angles[i], i);
        }
    }
    return angle_pops;
}

// close joint reader with cleanup
void JointReader::Close() {
    if (CheckInit()) {
        driver.close();
    }
    yarp::os::Network::fini();
}
