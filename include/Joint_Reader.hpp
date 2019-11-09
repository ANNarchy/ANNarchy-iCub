/*
 *  Copyright (C) 2019 Torsten Follak
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

#include <string>

#include <yarp/dev/all.h>
#include <yarp/sig/all.h>

class Joint_Reader
{
  public:
    // Constructor
    Joint_Reader() = default;
    // Destructor
    ~Joint_Reader();

    // initialize the joint reader with given parameters
    bool Init(std::string part, double sigma, int pop_n, double deg_per_neuron = 0.);
    // get the size of the populations encoding the joint angles
    std::vector<int> GetNeuronsPerJoint();
    // get the resolution in degree of the populations encoding the joint angles
    std::vector<double> GetJointsDegRes();
    // close joint reader with cleanup
    void Close();

    // read one joint and return joint angle directly as double value
    double ReadDouble(int joint);
    // read one joint and return the joint angle encoded in a vector
    std::vector<double> ReadOne(int joint);
    // read all joints and return the joint angles encoded in vectors
    std::vector<std::vector<double>> ReadAll();

  private:
    bool dev_init = false; // variable for initialization check
    std::string icub_part; // string describing the part of the iCub

    int joint_res;                     // neuron count for the population coding, if degree per neuron is set by argument
    std::vector<double> joint_deg_res; // degree per neuron for the population coding, value per joint; if neuron count is set by argument
    int joints;                        // number of joints
    double sigma_pop;                  // sigma for Gaussian envelope in the population coding

    std::vector<double> joint_min;               // minimum possible joint angles
    std::vector<double> joint_max;               // maximum possible joint angles
    std::vector<std::vector<double>> neuron_deg; // vector of vectors representing the degree values for the neuron populations

    yarp::sig::Vector joint_angles; // yarp vector for reading all joint angles
    yarp::dev::PolyDriver driver;   // yarp driver needed for reading joint encoders
    yarp::dev::IEncoders *ienc;     // iCub joint encoder interface

    // auxilary functions //
    // check if init function was called
    bool CheckInit();
    // encode joint position into a vector
    std::vector<double> Encode(double joint_angle, int joint);
    // return the normal distribution value for a given value, mean and sigma
    double NormalPdf(double value, double mean, double sigma);
};
