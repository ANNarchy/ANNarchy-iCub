
#include <iostream>
#include <string>

#include <yarp/dev/all.h>
#include <yarp/os/all.h>
#include <yarp/sig/all.h>

#include "INI_Reader/INIReader.h"
#include "Joint_Writer.hpp"


// Constructor
Joint_Writer::Joint_Writer() {}

// Destructor
Joint_Writer::~Joint_Writer() {}

// initialize the joint writer with given parameters
bool Joint_Writer::init(std::string part, int pop_size, double deg_per_neuron)
/*
    params: std::string part        -- string representing the robot part, has to match iCub part naming
                                        {left_(arm/leg), right_(arm/leg), head, torso}
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

            yarp::os::Network::init();
            if (!yarp::os::Network::checkNetwork())
                {
                    std::cerr << "[Joint Writer " << iCub_part << "] YARP Network is not online. Check nameserver is running" << std::endl;
                    return false;
                }

            yarp::os::Property options;
            options.put("device", "remote_controlboard");
            options.put("remote", ("/icubSim/" + iCub_part).c_str());
            options.put("local", ("/ANNarchy_write/" + iCub_part).c_str());

            if (!driver.open(options))
                {
                    std::cerr << "[Joint Writer " << iCub_part << "] Unable to open" << options.find("device").asString() << std::endl;
                    return false;
                }

            driver.view(iPos);
            iPos->getAxes(&joints);
            joint_angles.resize(joints);
            neuron_deg.resize(joints);
            joint_deg_res.resize(joints);

            double joint_range;
            INIReader reader("joint_limits.ini");

            for (int i = 0; i < joints; i++)
                {
                    joint_min.push_back(reader.GetReal(iCub_part.c_str(), ("joint_" + std::to_string(i) + "_min").c_str(), 0.0));
                    joint_max.push_back(reader.GetReal(iCub_part.c_str(), ("joint_" + std::to_string(i) + "_max").c_str(), 0.0));

                    // printf("joint: %i, min: %f, max: %f\n", i, joint_min[i], joint_max[i]);

                    if (joint_min == joint_max)
                        {
                            std::cerr << "[Joint Writer " << iCub_part << "] Error in reading joint parameters from .ini file "
                                      << std::endl;
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
            std::cerr << "[Joint Writer " << iCub_part << "] Initialization aready done!" << std::endl;
            return false;
        }
}

// helper function to check if init function was called
bool Joint_Writer::check_init()
{
    if (!dev_init)
        {
            std::cerr << "[Joint Writer] Error: Device is not initialized" << std::endl;
            return false;
        }
    else
        {
            return true;
        }
}

// get the size of the populations encoding the joint angles
std::vector<int> Joint_Writer::get_neurons_per_joint()
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
std::vector<double> Joint_Writer::get_joints_deg_res()
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

// decode the population coded joint angle to double value
double Joint_Writer::decode(std::vector<double> position_pop, int joint)
/*
    params: std::vector<double>             -- population encoded joint angle
            int joint                       -- joint number of the robot part

    return: double joint_angle              -- decoded joint angle
*/
{
    int size = position_pop.size();
    double sum_pop_w = 0;
    double sum_pop = 0;
    for (int i = 0; i < size; i++)
        {
            sum_pop_w = sum_pop_w + position_pop[i] * neuron_deg[joint][i];
            sum_pop = sum_pop + position_pop[i];
        }
    double joint_angle = sum_pop_w / sum_pop;

    return joint_angle;
}

// write one joint as double value
bool Joint_Writer::write_double(double position, int joint, bool blocking)
/*
    params: double position     -- joint angle to write to the robot joint
            int joint           -- joint number of the robot part
            bool blocking       -- if True, function waits for end of movement

    return: bool                -- return True, if successful
*/
{
    if (check_init())
        {
            if (joint >= joints)
                {
                    std::cerr << "[Joint Writer " << iCub_part << "] Selected joint out of range" << std::endl;
                    return false;
                }
            if (blocking)
                {
                    auto start = iPos->positionMove(joint, position);
                    if (start)
                        {
                            bool motion = false;
                            while (!motion)
                                {
                                    if (!iPos->checkMotionDone(&motion))
                                        {
                                            std::cerr << "[Joint Writer " << iCub_part << "] Communication error while moving" << std::endl;
                                            return false;
                                        }
                                }
                        }
                    return start;
                }
            else
                {
                    return iPos->positionMove(joint, position);
                }
        }
    else
        {
            return false;
        }
}

// write one joint with the joint angle encoded in a population
bool Joint_Writer::write_one(std::vector<double> position_pop, int joint, bool blocking)
/*
    params: std::vector<double>     -- population encoded joint angle for writing to the robot joint
            int joint               -- joint number of the robot part
            bool blocking           -- if True, function waits for end of movement

    return: bool                    -- return True, if successful
*/
{
    if (check_init())
        {
            if (joint >= joints)
                {
                    std::cerr << "[Joint Writer " << iCub_part << "] Selected joint out of range" << std::endl;
                    return false;
                }
            double angle = decode(position_pop, joint);

            if (blocking)
                {
                    auto start = iPos->positionMove(joint, angle);
                    if (start)
                        {
                            bool motion = false;
                            while (!motion)
                                {
                                    if (!iPos->checkMotionDone(&motion))
                                        {
                                            std::cerr << "[Joint Writer " << iCub_part << "] Communication error while moving" << std::endl;
                                            return false;
                                        }
                                }
                        }
                    return start;
                }
            else
                {
                    return iPos->positionMove(joint, angle);
                }
        }
    else
        {
            return false;
        }
}

// write all joints with joint angles encoded in populations
bool Joint_Writer::write_all(std::vector<std::vector<double>> position_pops, bool blocking)
/*
    params: std::vector<std::vector<double>>    -- populations encoding every joint angle for writing them to the associated robot part
            bool blocking                       -- if True, function waits for end of movement

    return: bool                                -- return True, if successful
*/
{
    if (check_init())
        {
            if (position_pops.size() != joints)
                {
                    std::cerr << "[Joint Writer " << iCub_part << "] Wrong joint count in population input" << std::endl;
                    return false;
                }

            for (int i = 0; i < joints; i++)
                {
                    joint_angles[i] = decode(position_pops[i], i);
                }

            if (blocking)
                {
                    auto start = iPos->positionMove(joint_angles.data());
                    if (start)
                        {
                            bool motion = false;
                            while (!motion)
                                {
                                    if (!iPos->checkMotionDone(&motion))
                                        {
                                            std::cerr << "[Joint Writer " << iCub_part << "] Communication error while moving" << std::endl;
                                            return false;
                                        }
                                }
                        }
                    return start;
                }
            else
                {
                    return iPos->positionMove(joint_angles.data());
                }
        }
    else
        {
            return false;
        }
}

// close joint reader with cleanup
void Joint_Writer::close()
{
    if (check_init())
        {
            driver.close();
        }
    yarp::os::Network::fini();
}
