/*
 *  Copyright (C) 2019-2021 Torsten Fietzek
 *
 *  Joint_Reader.hpp is part of the iCub ANNarchy interface
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

#pragma once

#include <yarp/dev/all.h>
#include <yarp/sig/all.h>

#include <string>
#include <thread>
#include <vector>

#include "Module_Base_Class.hpp"
#include "ProvideInputServer.h"

/**
 * \brief  Read-out of the joint angles of the iCub robot
 */
class JointReader : public Mod_BaseClass {
 public:
    // Constructor
    JointReader() = default;
    // Destructor
    ~JointReader();

    /*** public methods for the user ***/

    /**
     * \brief Initialize the joint reader with given parameters
     * \param[in] part A string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso}.
     * \param[in] sigma Standard deviation for the joints angles populations coding.
     * \param[in] pop_n Number of neurons per population, encoding each one joint angle; only works if parameter "deg_per_neuron" is not set
     * \param[in] deg_per_neuron (default = 0.0) degree per neuron in the populations, encoding the joints angles; if set: population size depends on joint working range
     * \param[in] ini_path Path to the "interface_param.ini"-file.
     * \return True, if the initializatiion was successful. False if an error occured. Additionally, an error message is written to the error stream (cerr).\n
     *          Typical errors:
     *              - arguments not valid: e.g. part string not correct or ini file not in given path \n
     *              - YARP-Server not running
     */
    bool Init(std::string part, double sigma, unsigned int pop_n, double deg_per_neuron, std::string ini_path);

    /**
     * \brief Initialize the joint reader with given parameters
     * \param[in] part A string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso}.
     * \param[in] sigma Standard deviation for the joints angles populations coding.
     * \param[in] pop_n Number of neurons per population, encoding each one joint angle; only works if parameter "deg_per_neuron" is not set
     * \param[in] deg_per_neuron (default = 0.0) degree per neuron in the populations, encoding the joints angles; if set: population size depends on joint working range
     * \param[in] ini_path Path to the "interface_param.ini"-file.
     * \param[in] ip_address gRPC server ip address -> has to match ip address of the JointReadOut-Population
     * \param[in] port gRPC server port -> has to match port of the JointReadOut-Population
     * \return True, if the initializatiion was successful. False if an error occured. Additionally, an error message is written to the error stream (cerr).\n
     *          Typical errors:
     *              - arguments not valid: e.g. part string not correct or ini file not in given path \n
     *              - YARP-Server not running
     */
    bool InitGRPC(std::string part, double sigma, unsigned int pop_n, double deg_per_neuron, std::string ini_path, std::string ip_address,
                  unsigned int port);

    /**
     * \brief  Close joint reader with cleanup
     */
    void Close() override;

    /**
     * \brief  Return number of controlled joints
     * \return Number of joints, being controlled by the reader
     */
    int GetJointCount();

    /**
     * \brief  Return the resolution in degree of the populations encoding the joint angles.
     * \return Return a vector of double, containing the resolution for every joints population coding in degree. E.g. Joint 0 is coded with 1° resolution: vector[0] = 1.0.
     */
    std::vector<double> GetJointsDegRes();

    /**
     * \brief Return the size of the populations encoding the joint angles
     * \return Return vector, containing the population size for every joint. E.g. Angle of joint 0 is encoded in a population with 10 neurons: vector[0] = 10
     */
    std::vector<unsigned int> GetNeuronsPerJoint();

    /**
     * \brief Read all joints and return joint angles directly in degree as double values
     * \return Joint angles, read from the robot in degree.
     */
    std::vector<double> ReadDoubleAll();
    std::vector<double> ReadDoubleAllTime();

    /**
     * \brief Read multiple joints and return joint angles directly in degree as double values
     * \param[in] joint_select Joint number selection of the robot part
     * \return Joint angles, read from the robot in degree.
     */
    std::vector<double> ReadDoubleMultiple(std::vector<int> joint_select);
    std::vector<double> ReadDoubleMultipleTime(std::vector<int> joint_select);

    /**
     * \brief Read one joint and return joint angle directly in degree as double value
     * \param[in] joint Joint number of the robot part
     * \return Joint angle, read from the robot in degree.
     */
    double ReadDoubleOne(int joint);
    std::vector<double> ReadDoubleOneTime(int joint);

    /**
     * \brief Read all joints and return the joint angles encoded in populations.
     * \return Population vectors encoding every joint angle from associated robot part.
     */
    std::vector<std::vector<double>> ReadPopAll();

    /**
     * \brief Read multiple joints and return the joint angles encoded in populations.
     * \return Population vectors encoding multiple joint angles from associated robot part.
     */
    std::vector<std::vector<double>> ReadPopMultiple(std::vector<int> joint_select);

    /**
     * \brief Read one joint and return the joint angle encoded in a population. 
     * \param[in] joint joint number of the robot part 
     * \return Population vector encoding the joint angle.
     */
    std::vector<double> ReadPopOne(int joint);

    /*** gRPC functions ***/
    std::vector<double> provideData(int value, bool enc);
    std::vector<double> provideData(std::vector<int> value, bool enc);
    std::vector<double> provideData(bool enc);

 private:
    /*** configuration variables ***/
    std::vector<std::string> key_map{"head", "torso", "right_arm", "left_arm", "right_leg", "left_leg"};    // valid iCub part keys

    /*** population coding parameters ***/
    std::vector<double> joint_deg_res;    // degree per neuron for the population coding, value per joint
    int joints = 0;                       // number of joints
    double sigma_pop;                     // sigma for Gaussian envelope in the population coding

    std::vector<double> joint_min;                  // minimum possible joint angles
    std::vector<double> joint_max;                  // maximum possible joint angles
    std::vector<std::vector<double>> neuron_deg;    // vector of vectors representing the degree values for the neuron populations

    /*** yarp data structures ***/
    yarp::sig::Vector joint_angles;    // yarp vector for reading all joint angles
    yarp::dev::PolyDriver driver;      // yarp driver needed for reading joint encoders
    yarp::dev::IEncoders *ienc;        // iCub joint encoder interface

    /** grpc communication **/
    std::string _ip_address = "";    // gRPC server ip address
    unsigned int _port = -1;         // gRPC server port
    ServerInstance *joint_source;    // gRPC server instance
    std::thread server_thread;       // thread for running the gRPC server in parallel

    /*** auxilary functions ***/
    // check if iCub part key is valid
    bool CheckPartKey(std::string key);
    // encode joint position into a vector
    std::vector<double> Encode(double joint_angle, int joint);
    // return the normal distribution value for a given value, mean and sigma
    double NormalPdf(double value, double mean, double sigma);
};
