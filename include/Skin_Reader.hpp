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

/**
 * \brief  Struct for the skin taxel positiiion data per iCub part
 */
struct TaxelData {
    std::vector<int> idx;                    // index array
    std::vector<std::vector<double>> arr;    // taxel position array -> x;y;z position for the idx taxel
};

/**
 * \brief  Read-out of the skin sensor data from the iCubs artificial skin
 */
class SkinReader {
 public:
    // Constructor
    SkinReader() = default;
    // Destructor
    ~SkinReader();

    /*** public methods for the user ***/
    /**
     * \brief Initialize skin reader with given parameters.
     * \param[in] arm character to choose the arm side (r/R for right; l/L for left)
     * \param[in] norm_data if True, data is normalized from 0..255 to 0..1.0
     * \param[in] ini_path Path to the "interface_param.ini"-file.
     * \return True, if the initializatiion was successful. False if an error occured. Additionally, an error message is written to the error stream (cerr).
     */
    bool Init(char arm, bool norm_data, std::string ini_path = "../data/");

    /**
     * \brief  Close and clean skin reader
     */
    void Close();

    /**
     * \brief Return tactile data for upper arm skin.
     * \return vector, containing the tactile data of the upper arm for the last time steps
     */
    std::vector<std::vector<double>> GetTactileArm();

    /**
     * \brief Return tactile data for forearm skin.
     * \return vector, containing the tactile data of the upper arm for the last time steps
     */
    std::vector<std::vector<double>> GetTactileForearm();

    /**
     * \brief Return tactile data for hand skin.
     * \return vector, containing the tactile data of the upper arm for the last time steps
     */
    std::vector<std::vector<double>> GetTactileHand();

    /**
     * \brief Return the taxel positions given by the ini files.
     * \param[in] skin_part Skin part to load the data for ("arm", "forearm", "hand")
     * \return Vector containing taxel positions -> reference frame depending on skin part
     */
    std::vector<std::vector<double>> GetTaxelPos(std::string skin_part);

    /**
     * \brief The sensor data is read and buffered inside. It can be accessed through #GetTactileArm, #GetTactileForearm and #GetTactileHand.
     * \return True, if successful. False if an error occured. Additionally, an error message is written to the error stream (cerr).
     */
    bool ReadTactile();

 private:
    /*** configuration variables ***/
    bool dev_init = false;    // variable for initialization check
    std::string side;         // containing information about selected arm (right/left)
    double norm_fac;          // norming factor: 255.0 for normalized data

    /*** yarp data structures ***/
    yarp::os::BufferedPort<yarp::sig::Vector> port_hand;       // port for the hand
    yarp::os::BufferedPort<yarp::sig::Vector> port_forearm;    // port for the forearm
    yarp::os::BufferedPort<yarp::sig::Vector> port_arm;        // port for the arm

    yarp::sig::Vector *tactile_hand;       // YARP Vector for hand sensor data
    yarp::sig::Vector *tactile_forearm;    // YARP Vector for forearm sensor data
    yarp::sig::Vector *tactile_arm;        // YARP Vector for upper arm sensor data

    /*** vectors to store tactile data ***/
    std::vector<std::vector<double>> hand_data;       // Vector for sorted and cleaned hand sensor data
    std::vector<std::vector<double>> forearm_data;    // Vector for sorted and cleaned forearm sensor data
    std::vector<std::vector<double>> arm_data;        // Vector for sorted and cleaned upper arm sensor data

    /*** sensor position data ***/
    std::map<std::string, TaxelData> taxel_pos_data;    // contains taxel position data for different skin parts

    // std::map<std::string, iCub::iKin::iKinChain *> kin_chains;    // iCub kinematic chain

    /*** auxilary functions ***/
    // check if init function was called
    bool CheckInit();
    // Read taxel positions from the ini files
    bool ReadTaxelPos(std::string filename_idx, std::string filename_pos, std::string part);
};
