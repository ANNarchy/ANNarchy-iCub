/*
 *  Copyright (C) 2019 Torsten Follak
 *
 *  Joint_Writer.hpp is part of the iCub ANNarchy interface
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
#include <vector>

/**
 * \brief Write the joint angles to the iCub robots joints to move them.
 */
class JointWriter {
 public:
    // Constructor
    JointWriter() = default;
    // Destructor
    ~JointWriter();

    /*** public methods for the user ***/

    /**
     * \brief Initialize the joint writer with given parameters
     * \param[in] part A string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso}.
     * \param[in] pop_size Number of neurons per population, encoding each one joint angle; only works if parameter "deg_per_neuron" is not set
     * \param[in] deg_per_neuron (default = 0.0) degree per neuron in the populations, encoding the joints angles; if set: population size depends on joint working range
     * \param[in] speed Velocity to set for the joint movements.
     * \return True, if the initializatiion was successful. False if an error occured. Additionally, an error message is written to the error stream (cerr).
     */
    bool Init(std::string part, int pop_size, double deg_per_neuron = 0.0, double speed = 10.0);

    /**
     * \brief  Close joint writer with cleanup
     */
    void Close();

    /**
     * \brief  Return number of controlled joints
     * \return Number of joints, being controlled by the writer
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
    std::vector<int> GetNeuronsPerJoint();

    /**
     * \brief Return the size of the populations encoding the joint angles
     * \param[in] speed Name of the selected joint writer
     * \param[in] joint (default -1) joint number of the robot part, default -1 for all joints
     * \return True, if set was successful. False if an error occured. Additionally, an error message is written to the error stream (cerr).
     */
    bool SetJointVelocity(double speed, int joint);

    /**
     * \brief Write all joints with double values.
     * \param[in] position Joint angles to write to the robot joints
     * \param[in] blocking if True, function waits for end of movement
     * \return True, if successful. False if an error occured. Additionally, an error message is written to the error stream (cerr).
     */
    bool WriteDoubleAll(std::vector<double> position, bool blocking);

    /**
     * \brief Write one joint with double value.
     * \param[in] position Joint angle to write to the robot joint (in degree)
     * \param[in] joint Joint number of the robot part
     * \param[in] blocking if True, function waits for end of movement
     * \return True, if successful. False if an error occured. Additionally, an error message is written to the error stream (cerr).
     */
    bool WriteDouble(double position, int joint, bool blocking);

    /**
     * \brief Write all joints with joint angles encoded in populations
     * \param[in] position_pops Populations encoding every joint angle for writing them to the associated robot part 
     * \param[in] blocking if True, function waits for end of movement
     * \return True, if successful. False if an error occured. Additionally, an error message is written to the error stream (cerr).
     */
    bool WritePopAll(std::vector<std::vector<double>> position_pops, bool blocking);

    /**
     * \brief Write one joint with the joint angle encoded in a population.
     * \param[in] position_pop Population encoded joint angle for writing to the robot joint 
     * \param[in] joint Joint number of the robot part 
     * \param[in] blocking if True, function waits for end of movement
     * \return True, if successful. False if an error occured. Additionally, an error message is written to the error stream (cerr).
     */
    bool WritePopOne(std::vector<double> position_pop, int joint, bool blocking);

 private:
    /** configuration variables **/
    bool dev_init = false;        // variable for initialization check
    double velocity_max = 100;    // maximum joint velocity
    std::string icub_part;        // string describing the part of the iCub

    std::vector<std::string> key_map{"head", "torso", "right_arm", "left_arm", "right_leg", "left_leg"};    // valid iCub part keys

    /*** population coding data structures ***/
    std::vector<double> joint_deg_res;    // degree per neuron for the population coding, value per joint
    int joints;                           // number of joints

    std::vector<double> joint_min;                  // minimum possible joint angles
    std::vector<double> joint_max;                  // maximum possible joint angles
    std::vector<std::vector<double>> neuron_deg;    // vector of vectors representing the degree values for the neuron populations

    /*** yarp data structures ***/
    yarp::sig::Vector joint_angles;       // yarp vector for reading all joint angles
    yarp::dev::PolyDriver driver;         // yarp driver needed for reading joint encoders
    yarp::dev::IPositionControl *ipos;    // iCub position control interface

    /*** auxilary methods ***/
    // check if init function was called
    bool CheckInit();
    // check if iCub part key is valid
    bool CheckPartKey(std::string key);
    // decode the population coded joint angle to double value
    double Decode(std::vector<double> position_pop, int joint);
};
