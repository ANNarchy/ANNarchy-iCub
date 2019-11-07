
#include <iostream>
#include <string>

#include <yarp/dev/all.h>
#include <yarp/os/all.h>
#include <yarp/sig/all.h>

#include "INI_Reader/INIReader.h"
#include "Joint_Reader.hpp"


// Destructor
Joint_Reader::~Joint_Reader() {}

// initialize the joint reader with given parameters
bool Joint_Reader::init(std::string part, double sigma, int pop_size, double deg_per_neuron)
/*
    params: std::string part        -- string representing the robot part, has to match iCub part naming
                                        {left_(arm/leg), right_(arm/leg), head, torso}
            sigma                   -- sigma for the joints angles populations coding
            int pop_size            -- number of neurons per population, encoding each one joint angle;
                                        only works if parameter "deg_per_neuron" is not set
            double deg_per_neuron   -- degree per neuron in the populations, encoding the joints angles;
                                        if set: population size depends on joint working range

    return: bool                    -- return True, if successful
*/
{
    if (!dev_init)
        {
            iCub_part = part;
            sigma_pop = sigma;
            yarp::os::Network::init();
            if (!yarp::os::Network::checkNetwork())
                {
                    std::cerr << "[Joint Reader " << iCub_part << "] YARP Network is not online. Check nameserver is running" << std::endl;
                    return false;
                }

            yarp::os::Property options;
            options.put("device", "remote_controlboard");
            options.put("remote", ("/icubSim/" + iCub_part).c_str());
            options.put("local", ("/ANNarchy_read/" + iCub_part).c_str());

            if (!driver.open(options))
                {
                    std::cerr << "[Joint Reader " << iCub_part << "] Unable to open " << options.find("device").asString() << std::endl;
                    return false;
                }

            driver.view(iEnc);
            iEnc->getAxes(&joints);
            joint_angles.resize(joints);
            neuron_deg.resize(joints);
            joint_deg_res.resize(joints);

            double joint_range;
            INIReader reader("joint_limits.ini");

            for (int i = 0; i < joints; i++)
                {
                    joint_min.push_back(reader.GetReal(iCub_part.c_str(), ("joint_" + std::to_string(i) + "_min").c_str(), 0.0));
                    joint_max.push_back(reader.GetReal(iCub_part.c_str(), ("joint_" + std::to_string(i) + "_max").c_str(), 0.0));

                    // printf("joint: %i, min: %f, max: %f \n", i, joint_min[i], joint_max[i]);

                    if (joint_min == joint_max)
                        {
                            std::cerr << "[Joint Reader " << iCub_part << "] Error in reading joint parameters from .ini file" << std::endl;
                            return false;
                        }

                    joint_range = joint_max[i] - joint_min[i];

                    if (deg_per_neuron > 0.0)
                        {
                            joint_res = std::floor(joint_range / deg_per_neuron);
                            neuron_deg[i].resize(joint_res);
                            joint_deg_res[i] = deg_per_neuron;

                            for (int j = 0; j < neuron_deg[i].size(); j++)
                                {
                                    neuron_deg[i][j] = joint_min[i] + j * deg_per_neuron;
                                }
                        }
                    else if (pop_size > 0)
                        {
                            neuron_deg[i].resize(pop_size);
                            joint_deg_res[i] = joint_range / pop_size;

                            for (int j = 0; j < neuron_deg[i].size(); j++)
                                {
                                    neuron_deg[i][j] = joint_min[i] + j * joint_deg_res[i];
                                }
                        }
                    else
                        {
                            std::cerr << "[Joint Reader " << iCub_part << "] Error in population size definition" << std::endl;
                            return false;
                        }
                }

            dev_init = true;
            return true;
        }
    else
        {
            std::cerr << "[Joint Reader " << iCub_part << "] Initialization aready done!" << std::endl;
            return false;
        }
}

// check if init function was called
bool Joint_Reader::check_init()
{
    if (!dev_init)
        {
            std::cerr << "[Joint Reader] Error: Device is not initialized" << std::endl;
            return false;
        }
    else
        {
            return true;
        }
}

// get the size of the populations encoding the joint angles
std::vector<int> Joint_Reader::get_neurons_per_joint()
/*
  return: std::vector<int>        -- return vector, containing the population size for every joint
*/
{
    if (check_init())
        {
            std::vector<int> neuron_counts(joints);
            for (int i = 0; i < joints; i++)
                {
                    neuron_counts[i] = neuron_deg[i].size();
                }
            return neuron_counts;
        }
    else
        {
            std::vector<int> empty;
            return empty;
        }
}

// get the resolution in degree of the populations encoding the joint angles
std::vector<double> Joint_Reader::get_joints_deg_res()
/*
  return: std::vector<double>        -- return vector, containing the resolution for every joints population codimg in degree
*/
{
    if (check_init())
        {
            return joint_deg_res;
        }
    else
        {
            std::vector<double> empty;
            return empty;
        }
}

// return the normal distribution value for a given value, mean and sigma
double Joint_Reader::normal_pdf(double value, double mean, double sigma)
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
std::vector<double> Joint_Reader::encode(double joint_angle, int joint)
/*
    params: double joint_angle              -- joint angle read from the robot
            int joint                       -- joint number of the robot part

    return: std::vector<double>             -- population encoded joint angle
*/
{
    int size = neuron_deg.at(joint).size();
    std::vector<double> pos_pop(size);

    for (int i = 0; i < size; i++)
        {
            pos_pop[i] = (normal_pdf(neuron_deg[joint][i], joint_angle, sigma_pop));
        }

    return pos_pop;
}

// read one joint and return joint angle directly as double value
double Joint_Reader::read_double(int joint)
/*
    params: int joint       -- joint number of the robot part

    return: double          -- joint angle read from the robot
*/
{
    if (check_init())
        {
            if (joint >= joints)
                {
                    std::cerr << "[Joint Reader " << iCub_part << "] Selected joint out of range" << std::endl;
                }
            double angle;
            if (!iEnc->getEncoder(joint, &angle))
                {
                    std::cerr << "[Joint Reader " << iCub_part << "] Error in reading joint angle from iCub" << std::endl;
                }
            return angle;
        }
    else
        {
            double empty;
            return empty;
        }
}

// read one joint and return the joint angle encoded in a vector
std::vector<double> Joint_Reader::read_one(int joint)
/*
    params: int joint               -- joint number of the robot part

    return: std::vector<double>     -- population vector encoding the joint angle
*/
{
    if (check_init())
        {
            if (joint >= joints)
                {
                    std::cerr << "[Joint Reader " << iCub_part << "] Selected joint out of range" << std::endl;
                }

            double angle;
            if (!iEnc->getEncoder(joint, &angle))
                {
                    std::cerr << "[Joint Reader " << iCub_part << "] Error in reading joint angle from iCub" << std::endl;
                }
            return encode(angle, joint);
        }
    else
        {
            std::vector<double> empty;
            return empty;
        }
}

// read all joints and return the joint angles encoded in vectors
std::vector<std::vector<double>> Joint_Reader::read_all()
/*
    return: std::vector<std::vector<double>>    -- population vectors encoding every joint angle from associated robot part
*/
{
    if (check_init())
        {
            double angles[joints];
            std::vector<std::vector<double>> pops;
            if (!iEnc->getEncoders(angles))
                {
                    std::cerr << "[Joint Reader " << iCub_part << "] Error in reading joint angle from iCub" << std::endl;
                }
            for (int i = 0; i < joints; i++)
                {
                    pops[i] = encode(angles[i], i);
                }
            return pops;
        }
    else
        {
            std::vector<std::vector<double>> empty;
            return empty;
        }
}

// close joint reader with cleanup
void Joint_Reader::close()
{
    if (check_init())
        {
            driver.close();
        }
    yarp::os::Network::fini();
}