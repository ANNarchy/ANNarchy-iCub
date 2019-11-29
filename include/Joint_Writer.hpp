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

class JointWriter {
 public:
    // Constructor
    JointWriter() = default;
    // Destructor
    ~JointWriter();

    /*** public methods for the user ***/
    // initialize the joint writer with given parameters
    bool Init(std::string part, int pop_size, double deg_per_neuron = 0.0, double speed = 10.0);
    // close joint reader with cleanup
    void Close();
    // get number of controlled joints
    int GetJointCount();
    // get the resolution in degree of the populations encoding the joint angles
    std::vector<double> GetJointsDegRes();
    // get the size of the populations encoding the joint angles
    std::vector<int> GetNeuronsPerJoint();
    // set velocity for a given joint or all joints
    bool SetJointVelocity(double speed, int joint);

    // write all joints as double values
    bool WriteDoubleAll(std::vector<double> position, bool blocking);
    // write one joint as double value
    bool WriteDouble(double position, int joint, bool blocking);
    // write all joints with joint angles encoded in populations
    bool WritePopAll(std::vector<std::vector<double>> position_pops, bool blocking);
    // write one joint with the joint angle encoded in a population
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
