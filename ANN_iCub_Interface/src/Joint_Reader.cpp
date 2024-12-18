/*
 *  Copyright (C) 2019-2022 Torsten Fietzek
 *
 *  JointReader.cpp is part of the ANNarchy iCub interface
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

#include "Joint_Reader.hpp"

#include <yarp/dev/all.h>
#include <yarp/os/all.h>
#include <yarp/sig/all.h>

#include <algorithm>
#include <ctime>
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
JointReader::~JointReader() { Close(); }

/*** public methods for the user ***/
bool JointReader::Init(std::string part, double sigma, unsigned int pop_size, double deg_per_neuron, std::string ini_path) {
    /*
        Initialize the joint reader with given parameters

        params: string part             -- string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso}
                double sigma            -- sigma for the joints angles populations coding
                int pop_size            -- number of neurons per population, encoding each one joint angle; only works if parameter "deg_per_neuron" is not set
                double deg_per_neuron   -- degree per neuron in the populations, encoding the joints angles; if set: population size depends on joint working range
                string ini_path         -- Path to the "interface_param.ini"-file

        return: bool                    -- return True, if successful
    */

    if (!this->dev_init) {
        if (!CheckPartKey(part)) {
            std::cerr << "[Joint Reader] " << part << " is an invalid iCub part key!" << std::endl;
            return false;
        }
        this->icub_part = part;

        if (pop_size < 0) {
            std::cerr << "[Joint Reader " << icub_part << "] Population size have to be positive!" << std::endl;
            return false;
        }
        if (sigma < 0) {
            std::cerr << "[Joint Reader " << icub_part << "] Sigma have to be positive!" << std::endl;
            return false;
        }
        sigma_pop = sigma;

        // Check Yarp-network
        if (!yarp::os::Network::checkNetwork()) {
            std::cerr << "[Joint Reader " << icub_part << "] YARP Network is not online. Check nameserver is running!" << std::endl;
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
            std::cerr << "[Joint Reader " << icub_part << "] Error in parsing the ini-file! Please check the ini-path \"" << ini_path << "\" and the ini file content!" << std::endl;
            return false;
        }
        std::string robot_port_prefix = reader_gen.Get("general", "robot_port_prefix", "/icubSim");
        std::string client_port_prefix = reader_gen.Get("general", "client_port_prefix", "/client");

        // setup iCub joint control board
        yarp::os::Property options;
        options.put("device", "remote_controlboard");
        options.put("remote", (robot_port_prefix + "/" + icub_part).c_str());
        options.put("local", (client_port_prefix + "/ANNarchy_Jread_" + std::to_string(std::time(NULL)) + "/" + icub_part).c_str());

        if (!driver.open(options)) {
            std::cerr << "[Joint Reader " << icub_part << "] Unable to open " << options.find("device").asString() << "!" << std::endl;
            return false;
        }

        // Open joint encoder interface
        if (!driver.view(ienc)) {
            std::cerr << "[Joint Reader " << icub_part << "] Unable to open motor encoder interface!" << std::endl;
            driver.close();
            return false;
        }

        // Open joint limits interface
        if (!driver.view(ilim)) {
            std::cerr << "[Joint Reader " << icub_part << "] Unable to open motor limit interface!" << std::endl;
            driver.close();
            return false;
        }

        ienc->getAxes(&joints);
        joint_angles.resize(joints);
        neuron_deg.resize(joints);
        joint_deg_res.resize(joints);

        // Variables needed to set joint limits
        double joint_range;
        double min, max;

        for (int i = 0; i < joints; i++) {
            // read joint limits
            ilim->getLimits(i, &min, &max);
            joint_min.push_back(min);
            joint_max.push_back(max);

            // printf("joint: %i, min: %f, max: %f \n", i, joint_min[i], joint_max[i]);

            if (joint_min == joint_max) {
                std::cerr << "[Joint Reader " << icub_part << "] Error in reading joint limits!" << std::endl;
                return false;
            }

            // compute population code resolution
            joint_range = joint_max[i] - joint_min[i] + 1;

            if (pop_size > 0) {    // with given population size
                neuron_deg[i].resize(pop_size);
                joint_deg_res[i] = joint_range / pop_size;

                for (unsigned int j = 0; j < neuron_deg[i].size(); j++) {
                    neuron_deg[i][j] = joint_min[i] + j * joint_deg_res[i];
                }

            } else if (deg_per_neuron > 0.0) {    // with given neuron resolution
                int joint_res = std::floor(joint_range / deg_per_neuron);
                neuron_deg[i].resize(joint_res);
                joint_deg_res[i] = deg_per_neuron;

                for (unsigned int j = 0; j < neuron_deg[i].size(); j++) {
                    neuron_deg[i][j] = joint_min[i] + j * deg_per_neuron;
                }
            } else {
                std::cerr << "[Joint Reader " << icub_part << "] Error in population size definition. Check the values for pop_size or deg_per_neuron!" << std::endl;
                return false;
            }
        }

        // set parameter for save robot to file
        this->type = "JointReader";
        init_param["part"] = part;
        init_param["sigma"] = std::to_string(sigma);
        init_param["popsize"] = std::to_string(pop_size);
        if (deg_per_neuron != 0.0) {
            init_param["deg_per_neuron"] = std::to_string(deg_per_neuron);
        }
        init_param["ini_path"] = ini_path;

        this->dev_init = true;
        return true;
    } else {
        std::cerr << "[Joint Reader " << icub_part << "] Initialization aready done!" << std::endl;
        return false;
    }
}

#ifdef _USE_GRPC
bool JointReader::InitGRPC(std::string part, double sigma, unsigned int pop_size, double deg_per_neuron, std::string ini_path, std::string ip_address, unsigned int port) {
    /*
        Initialize the joint reader with given parameters

        params: std::string part        -- string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso}
                sigma                   -- sigma for the joints angles populations coding
                int pop_size            -- number of neurons per population, encoding each one joint angle; only works if parameter "deg_per_neuron" is not set
                double deg_per_neuron   -- degree per neuron in the populations, encoding the joints angles; if set: population size depends on joint working range
                ini_path                -- Path to the "interface_param.ini"-file
                string ip_address       -- gRPC server ip address
                unsigned int port       -- gRPC server port

        return: bool                    -- return True, if successful
    */

    if (!this->dev_init) {
        if (this->Init(part, sigma, pop_size, deg_per_neuron, ini_path)) {
            this->_ip_address = ip_address;
            this->_port = port;
            this->joint_source = new ServerInstance(ip_address, port, this);
            this->server_thread = std::thread(&ServerInstance::wait, this->joint_source);
            this->dev_init_grpc = true;
            init_param["ip_address"] = ip_address;
            init_param["port"] = std::to_string(port);
            return true;
        } else {
            std::cerr << "[Joint Reader] Initialization failed!" << std::endl;
            return false;
        }
    } else {
        std::cerr << "[Joint Reader] Initialization already done!" << std::endl;
        return false;
    }
}
#else
bool JointReader::InitGRPC(std::string part, double sigma, unsigned int pop_size, double deg_per_neuron, std::string ini_path, std::string ip_address, unsigned int port) {
    /*
        Initialize the joint reader with given parameters

        params: string part             -- string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso}
                double sigma            -- sigma for the joints angles populations coding
                int pop_size            -- number of neurons per population, encoding each one joint angle; only works if parameter "deg_per_neuron" is not set
                double deg_per_neuron   -- degree per neuron in the populations, encoding the joints angles; if set: population size depends on joint working range
                string ini_path         -- Path to the "interface_param.ini"-file
                string ip_address       -- gRPC server ip address
                unsigned int port       -- gRPC server port

        return: bool                    -- return True, if successful
    */
    std::cerr << "[Joint Reader] gRPC is not included in the setup process!" << std::endl;
    return false;
}
#endif

void JointReader::Close() {
    /*
        Close joint reader with cleanup
    */
    if (driver.isValid()) {
        driver.close();
    }
#ifdef _USE_GRPC
    if (dev_init_grpc) {
        joint_source->shutdown();
        server_thread.join();
        delete joint_source;
        dev_init_grpc = false;
    }
#endif

    this->dev_init = false;
}

int JointReader::GetJointCount() {
    /*
        Return number of controlled joints

        return: int       -- return number of controlled joints
    */
    if (CheckInit())
        return joints;
    else
        return 0;
}

std::vector<double> JointReader::GetJointsDegRes() {
    /*
        Get the resolution in degree of the populations encoding the joint angles

        return: std::vector<double>        -- return vector, containing the resolution for every joint population in degree
    */

    CheckInit();
    return joint_deg_res;
}

std::vector<unsigned int> JointReader::GetNeuronsPerJoint() {
    /*
        Return the size of the populations encoding the joint angles

        return: std::vector<unsigned int>        -- return vector, containing the population size for every joint
    */

    std::vector<unsigned int> neuron_counts(joints);
    if (CheckInit()) {
        for (int i = 0; i < joints; i++) {
            neuron_counts[i] = neuron_deg[i].size();
        }
    }
    return neuron_counts;
}

std::vector<double> JointReader::ReadDoubleAll() {
    /*
        Read all joints and return joint angles directly as double value

        return: std::vector<double>     -- joint angles read from the robot
    */

    std::vector<double> angles;
    if (CheckInit()) {
        angles.resize(joints);
        while (!ienc->getEncoders(angles.data())) {
            yarp::os::Time::delay(0.001);
        }
    }
    return angles;
}

std::vector<double> JointReader::ReadDoubleAllTime() {
    /*
        Read all joints and return joint angles directly as double value

        return: std::vector<double>     -- joint angles read from the robot
    */
    std::vector<double> angles, angle_stamped;

    if (CheckInit()) {
        angles.resize(joints);
        while (!ienc->getEncoders(angles.data())) {
            yarp::os::Time::delay(0.001);
        }
        angle_stamped.push_back(yarp::os::Time::now() * 1000.);
        angle_stamped.insert(angle_stamped.end(), angles.begin(), angles.end());
    }
    return angle_stamped;
}

std::vector<double> JointReader::ReadDoubleMultiple(std::vector<int> joint_select) {
    /*
        Read multiple joints and return joint angles directly as double value

        params: std::vector<int> joint  -- joint selection of the robot part

        return: std::vector<double>     -- joint angles read from the robot
    */

    std::vector<double> angles, angle_select;

    if (CheckInit()) {
        const auto [min, max] = std::minmax_element(joint_select.begin(), joint_select.end());
        if (*min >= 0 && *max < joints) {
            angles.resize(joints);
            while (!ienc->getEncoders(angles.data())) {
                yarp::os::Time::delay(0.001);
            }
            for (unsigned int i = 0; i < joint_select.size(); i++) {
                angle_select.push_back(angles[joint_select[i]]);
            }
        }
    }
    return angle_select;
}

std::vector<double> JointReader::ReadDoubleMultipleTime(std::vector<int> joint_select) {
    /*
        Read all joints and return joint angles directly as double value

        return: std::vector<double>     -- joint angles read from the robot
    */
    std::vector<double> angles, angle_select, angle_stamped;

    if (CheckInit()) {
        const auto [min, max] = std::minmax_element(joint_select.begin(), joint_select.end());
        if (*min > 0 && *max < joints) {
            angles.resize(joints);
            while (!ienc->getEncoders(angles.data())) {
                yarp::os::Time::delay(0.001);
            }
            angle_stamped.push_back(yarp::os::Time::now() * 1000.);
            for (unsigned int i = 0; i < joint_select.size(); i++) {
                angle_select.push_back(angles[joint_select[i]]);
            }
            angle_stamped.insert(angle_stamped.end(), angle_select.begin(), angle_select.end());
        }
    }
    return angle_stamped;
}

double JointReader::ReadDoubleOne(int joint) {
    /*
        Read one joint and return joint angle directly as double value

        params: unsigned int joint      -- joint number of the robot part

        return: double                  -- joint angle read from the robot
    */

    double angle = -999.;
    if (CheckInit()) {
        if (joint < joints && joint >= 0) {
            while (!ienc->getEncoder(joint, &angle)) {
                yarp::os::Time::delay(0.001);
            }
        } else {
            std::cerr << "[Joint Reader " << icub_part << "] Selected joint <" << joint << "> is out of range!" << std::endl;
        }
    }
    return angle;
}

std::vector<double> JointReader::ReadDoubleOneTime(int joint) {
    /*
        Read one joint and return joint angle directly as double value

        params: int joint       -- joint number of the robot part

        return: double          -- joint angle read from the robot
    */

    double angle = -999.;
    std::vector<double> angle_stamped;

    if (CheckInit()) {
        if (joint < joints && joint >= 0) {
            while (!ienc->getEncoder(joint, &angle)) {
                yarp::os::Time::delay(0.001);
            }
            angle_stamped.push_back(yarp::os::Time::now() * 1000.);
            angle_stamped.push_back(angle);
        } else {
            std::cerr << "[Joint Reader " << icub_part << "] Selected joint <" << joint << "> is out of range!" << std::endl;
        }
    }
    return angle_stamped;
}

std::vector<std::vector<double>> JointReader::ReadPopAll() {
    /*
        Read all joints and return the joint angles encoded in vectors

        return: std::vector<std::vector<double>>    -- vector of population vectors encoding every joint angle from associated robot part
    */

    auto angle_pops = std::vector<std::vector<double>>(joints, std::vector<double>());

    if (CheckInit()) {
        std::vector<double> angles;
        angles.resize(joints);
        while (!ienc->getEncoders(angles.data())) {
            yarp::os::Time::delay(0.01);
        }
        for (int i = 0; i < joints; i++) {
            angle_pops[i] = Encode(angles[i], i);
        }
    }
    return angle_pops;
}

std::vector<std::vector<double>> JointReader::ReadPopMultiple(std::vector<int> joint_select) {
    /*
        Read multiple joints and return joint angles encoded in vectors

        params: std::vector<int> joint  -- joint selection of the robot part

        return: std::vector<std::vector<double>>    -- vector of population vectors encoding every joint angle from associated robot part
    */

    std::vector<double> angles;
    std::vector<std::vector<double>> angle_select;

    if (CheckInit()) {
        const auto [min, max] = std::minmax_element(joint_select.begin(), joint_select.end());
        if (*min >= 0 && *max < joints) {
            angles.resize(joints);
            while (!ienc->getEncoders(angles.data())) {
                yarp::os::Time::delay(0.001);
            }
            for (unsigned int i = 0; i < joint_select.size(); i++) {
                angle_select.push_back(Encode(angles[joint_select[i]], joint_select[i]));
            }
        }
    }
    return angle_select;
}

std::vector<double> JointReader::ReadPopOne(int joint) {
    /*
        Read one joint and return the joint angle encoded in a vector

        params: unsigned int joint      -- joint number of the robot part

        return: std::vector<double>     -- population vector encoding the joint angle
    */

    std::vector<double> angle_pop;
    if (CheckInit()) {
        if (joint < joints && joint >= 0) {
            double angle;
            while (!ienc->getEncoder(joint, &angle)) {
                yarp::os::Time::delay(0.01);
            }
            angle_pop = Encode(angle, joint);
        } else {
            std::cerr << "[Joint Reader " << icub_part << "] Selected joint <" << joint << "> is out of range!" << std::endl;
        }
    }
    return angle_pop;
}

/*** gRPC functions ***/
#ifdef _USE_GRPC
std::vector<double> JointReader::provideData(int value, bool enc) {
    if (enc) {
        return ReadPopOne(value);
    } else {
        return std::vector<double>(1, ReadDoubleOne(value));
    }
}

std::vector<double> JointReader::provideData(std::vector<int> value, bool enc) {
    if (enc) {
        auto angles = ReadPopMultiple(value);
        std::vector<double> v;
        for (unsigned int i = 0; i < angles.size(); i++) {
            v.insert(v.end(), angles[i].begin(), angles[i].end());
        }
        return v;
    } else {
        return ReadDoubleMultiple(value);
    }
}

std::vector<double> JointReader::provideData(bool enc) {
    if (enc) {
        auto angles = ReadPopAll();
        std::vector<double> v;
        for (size_t i = 0; i < angles.size(); i++) {
            v.insert(v.end(), angles[i].begin(), angles[i].end());
        }
        return v;
    } else {
        return ReadDoubleAll();
    }
}
#endif

/*** auxilary functions ***/
bool JointReader::CheckPartKey(std::string key) {
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

std::vector<double> JointReader::Encode(double joint_angle, int joint) {
    /*
        Encode given joint position into a vector

        params: double joint_angle              -- joint angle read from the robot
                int joint                       -- joint number of the robot part

        return: std::vector<double>             -- population encoded joint angle
    */

    auto size = neuron_deg.at(joint).size();
    std::vector<double> pos_pop(size);
    for (unsigned int i = 0; i < size; i++) {
        pos_pop[i] = (NormalPdf(neuron_deg[joint][i], joint_angle, sigma_pop));
    }

    return pos_pop;
}

double JointReader::NormalPdf(double value, double mean, double sigma) {
    /*
        Return the normal distribution value for a given value, mean and sigma

        params: double value            -- value to calculate normal distribution at
                double mean             -- mean of the normal distribution
                double sigma            -- sigma of the normal distribution

        return: double                  -- function value for the normal distribution
    */

    // double inv_sqrt_2pi = 4.0 / (sigma * std::sqrt(2 * M_PI));
    double a = (value - mean) / sigma;

    // return inv_sqrt_2pi * std::exp(-0.5 * a * a);
    return 1.0 * std::exp(-0.5 * a * a);
}
