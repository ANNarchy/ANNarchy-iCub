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

#include <string>

#include <yarp/dev/all.h>
#include <yarp/sig/all.h>

class Joint_Writer
{
  public:
    // Constructor
    Joint_Writer();
    // Destructor
    ~Joint_Writer();

    // initialize the joint writer with given parameters
    bool Init(std::string part, int pop_size, double deg_per_neuron = 0.0);
    // get the size of the populations encoding the joint angles
    std::vector<int> GetNeuronsPerJoint();
    // get the resolution in degree of the populations encoding the joint angles
    std::vector<double> GetJointsDegRes();
    // close joint reader with cleanup
    void Close();

    // write one joint as double value
    bool WriteDouble(double position, int joint, bool blocking);
    // write one joint with the joint angle encoded in a population
    bool WriteOne(std::vector<double> position_pop, int joint, bool blocking);
    // write all joints with joint angles encoded in populations
    bool WriteAll(std::vector<std::vector<double>> position_pops, bool blocking);

  private:
    bool dev_init = false; // variable for initialization check
    std::string icub_part; // string describing the part of the iCub

    int joint_res;                     // neuron count for the population coding, if degree per neuron is set by argument
    std::vector<double> joint_deg_res; // degree per neuron for the population coding, value per joint; if neuron count is set by argument
    int joints;                        // number of joints

    std::vector<double> joint_min;               // minimum possible joint angles
    std::vector<double> joint_max;               // maximum possible joint angles
    std::vector<std::vector<double>> neuron_deg; // vector of vectors representing the degree values for the neuron populations

    yarp::sig::Vector joint_angles;    // yarp vector for reading all joint angles
    yarp::dev::PolyDriver driver;      // yarp driver needed for reading joint encoders
    yarp::dev::IPositionControl *ipos; // iCub position control interface

    // auxilary functions //
    // check if init function was called
    bool CheckInit();
    // decode the population coded joint angle to double value
    double Decode(std::vector<double> position_pop, int joint);
};
