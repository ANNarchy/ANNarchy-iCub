/*
 *  Copyright (C) 2019 Torsten Follak
 *
 *  Skin_Reader.hpp is part of the iCub ANNarchy interface
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

#include <iCub/iKin/iKinFwd.h>    // iCub forward Kinematics
#include <yarp/os/all.h>
#include <yarp/sig/all.h>

#include <map>
#include <string>
#include <vector>

#include <opencv2/opencv.hpp>

struct TaxelData {
    std::vector<int> idx;
    std::vector<std::vector<double>> arr;
};

class SkinReader {
 public:
    // Constructor
    SkinReader() = default;
    // Destructor
    ~SkinReader();
    // init skin reader with given parameters
    bool Init(char arm, bool norm_data);
    // read sensor data
    bool ReadTactile();

    // return tactile data for hand skin
    std::vector<std::vector<double>> GetTactileHand();
    // return tactile data for forearm skin
    std::vector<std::vector<double>> GetTactileForearm();
    // return tactile data for upper arm skin
    std::vector<std::vector<double>> GetTactileArm();
    // return the taxel positions given by the ini files
    std::vector<std::vector<double>> GetTaxelPos(std::string skin_part);

    // close and clean skin reader
    void Close();

 private:
    bool dev_init = false;    // variable for initialization check

    yarp::os::BufferedPort<yarp::sig::Vector> port_hand;       // port for the hand
    yarp::os::BufferedPort<yarp::sig::Vector> port_forearm;    // port for the forearm
    yarp::os::BufferedPort<yarp::sig::Vector> port_arm;        // port for the arm

    yarp::sig::Vector *tactile_hand;       // YARP Vector for hand sensor data
    yarp::sig::Vector *tactile_forearm;    // YARP Vector for forearm sensor data
    yarp::sig::Vector *tactile_arm;        // YARP Vector for upper arm sensor data

    std::vector<std::vector<double>> hand_data;       // Vector for sorted and cleaned hand sensor data
    std::vector<std::vector<double>> forearm_data;    // Vector for sorted and cleaned forearm sensor data
    std::vector<std::vector<double>> arm_data;        // Vector for sorted and cleaned upper arm sensor data

    std::string side;    // containing information about selected arm (right/left)
    double norm_fac;     // norming factor: 255.0 for naormalized data

    std::map<std::string, TaxelData> taxel_pos_data;              // contains taxel position data for different skin parts
    std::map<std::string, iCub::iKin::iKinChain *> kin_chains;    // contains taxel position data for different skin parts

    bool ReadTaxelPos(std::string filename_idx, std::string filename_pos, std::string part);

    // auxilary functions //
    // check if init function was called
    bool CheckInit();
};
