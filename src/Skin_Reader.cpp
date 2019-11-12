/*
 *  Copyright (C) 2019 Torsten Follak
 *
 *  Skin_Reader.cpp is part of the iCub ANNarchy interface
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

#include <yarp/dev/all.h>
#include <yarp/os/all.h>
#include <yarp/sig/all.h>

// #include <iCub/iKin/iKinFwd.h>    // iCub forward Kinematics
// #include <iCub/skinDynLib/iCubSkin.h>

#include <fstream>
#include <iostream>
#include <queue>
#include <string>

#include "Skin_Reader.hpp"

// Destructor
SkinReader::~SkinReader() { Close();}

// init skin reader with given parameters
bool SkinReader::Init(char arm)
/*
    params: char arm    -- character to choose the arm side (r/R for right; l/L for left)

    return: bool        -- return True, if successful
*/
{
    if (!dev_init) {
        // Init YARP-Network
        yarp::os::Network::init();
        if (!yarp::os::Network::checkNetwork()) {
            std::cerr << "[Skin Reader] YARP Network is not online. Check nameserver is running!" << std::endl;
            return false;
        }

        // set side and read taxel position files depending on selected arm side
        std::string data_dir = "./data/sensor_positions/";
        if (arm == 'r' || arm == 'R') {
            side = "right";
            bool read_err_arm = !ReadTaxelPos(data_dir + "right_arm_mesh_idx.txt", data_dir + "right_arm_mesh_pos.txt", "arm");
            bool read_err_farm = !ReadTaxelPos(data_dir + "right_forearm_V2_idx.txt", data_dir + "right_forearm_V2_pos.txt", "forearm");
            bool read_err_hand = !ReadTaxelPos(data_dir + "right_hand_V2_1_idx.txt", data_dir + "right_hand_V2_1_pos.txt", "hand");
            if (read_err_arm || read_err_farm || read_err_hand) {
                return false;
            }
        } else if (arm == 'l' || arm == 'L') {
            side = "left";
            bool read_err_arm = !ReadTaxelPos(data_dir + "left_arm_mesh_idx.txt", data_dir + "left_arm_mesh_pos.txt", "arm");
            bool read_err_farm = !ReadTaxelPos(data_dir + "left_forearm_V2_idx.txt", data_dir + "left_forearm_V2_pos.txt", "forearm");
            bool read_err_hand = !ReadTaxelPos(data_dir + "left_hand_V2_1_idx.txt", data_dir + "left_hand_V2_1_pos.txt", "hand");

            if (read_err_arm || read_err_farm || read_err_hand) {
                return false;
            }
        } else {
            std::cerr << "[Skin Reader] No correct side descriptor: Use R/r for the right arm and L/l for the left arm!" << std::endl;
            return false;
        }

        // Open and connect YARP-Port to read hand skin sensor data
        std::string port_name_hand = "/Skin_Reader/" + side + "_hand:i";
        port_hand.open(port_name_hand);
        if (!yarp::os::Network::connect(("/icubSim/skin/" + side + "_hand_comp").c_str(), port_name_hand.c_str())) {
            std::cerr << "[Skin Reader] Could not connect skin hand port!" << std::endl;
            return false;
        }

        // Open and connect YARP-Port to read forearm skin sensor data
        std::string port_name_farm = "/Skin_Reader/" + side + "_forearm:i";
        port_forearm.open(port_name_farm);
        if (!yarp::os::Network::connect(("/icubSim/skin/" + side + "_forearm_comp").c_str(), port_name_farm.c_str())) {
            std::cerr << "[Skin Reader] Could not connect skin forearm port!" << std::endl;
            return false;
        }

        // Open and connect YARP-Port to read upper arm skin sensor data
        std::string port_name_arm = "/Skin_Reader/" + side + "_arm:i";
        port_arm.open(port_name_arm);
        if (!yarp::os::Network::connect(("/icubSim/skin/" + side + "_arm_comp").c_str(), port_name_arm.c_str())) {
            std::cerr << "[Skin Reader] Could not connect skin arm port!" << std::endl;
            return false;
        }

        // iCub::iKin::iCubArm libArm(side);
        // kin_chains["arm"] = libArm.asChain();
        // for (int i = 10; i > 2; i--)
        //     {
        //         kin_chains["arm"]->rmLink(i);
        //     }

        // kin_chains["forearm"] = libArm.asChain();
        // for (int i = 10; i > 4; i--)
        //     {
        //         kin_chains["forearm"]->rmLink(i);
        //     }

        // kin_chains["hand"] = libArm.asChain();
        // for (int i = 10; i > 6; i--)
        //     {
        //         kin_chains["hand"]->rmLink(i);
        //     }

        dev_init = true;
        return true;
    } else {
        std::cerr << "[Skin Reader] Initialization aready done!" << std::endl;
        return false;
    }
}

// check if init function was called
bool SkinReader::CheckInit() {
    if (!dev_init) {
        std::cerr << "[Skin Reader] Error: Device is not initialized!" << std::endl;
    }
    return dev_init;
}

// read sensor data from iCub YARP ports
void SkinReader::ReadTactile() {
    if (CheckInit()) {
        tactile_hand = port_hand.read();
        tactile_forearm = port_forearm.read();
        tactile_arm = port_arm.read();

        // HAND
        std::string skin_part_h = "hand";
        auto init_pos_h = taxel_pos_data[skin_part_h].arr;
        auto idx_arr_h = taxel_pos_data[skin_part_h].idx;
        for (int i = 0; i < idx_arr_h.size(); i++) {
            if (idx_arr_h[i] > 0) hand_data.push_back(tactile_hand->data()[i]);
        }

        // FOREARM
        std::string skin_part_f = "forearm";
        auto init_pos_f = taxel_pos_data[skin_part_f].arr;
        auto idx_arr_f = taxel_pos_data[skin_part_f].idx;
        for (int i = 0; i < idx_arr_f.size(); i++) {
            if (idx_arr_f[i] > 0) forearm_data.push_back(tactile_forearm->data()[i]);
        }

        // ARM
        std::string skin_part_a = "arm";
        auto init_pos_a = taxel_pos_data[skin_part_a].arr;
        auto idx_arr_a = taxel_pos_data[skin_part_a].idx;
        for (int i = 0; i < idx_arr_a.size(); i++) {
            if (idx_arr_a[i] > 0) arm_data.push_back(tactile_arm->data()[i]);
        }
    }
}

// return tactile data for hand skin
std::vector<double> SkinReader::GetTactileHand() {
    CheckInit();
    return hand_data;
}

// return tactile data for forearm skin
std::vector<double> SkinReader::GetTactileForearm() {
    CheckInit();
    return forearm_data;
}

// return tactile data for upper arm skin
std::vector<double> SkinReader::GetTactileArm() {
    CheckInit();
    return arm_data;
}

// read information about taxel position from config files
bool SkinReader::ReadTaxelPos(std::string filename_idx, std::string filename_pos, std::string part)
/*
    params: std::string filename_idx    -- filename, containing the path, of the file with the taxel index data 
            std::string filename_pos    -- filename, containing the path, of the file with the taxel position data 
            std::string part            -- skin part to load the data for (e.g. forearm)

    return: bool                        -- return True, if successful
*/
{
    std::ifstream file_idx;
    std::ifstream file_pos;
    std::vector<int> idx;
    std::vector<std::vector<double>> arr;
    std::vector<double> pos;
    TaxelData part_tax_pos;
    int ind;
    double val;
    int i;

    // read information from file about used indices of the skin sensor position data
    i = 0;
    file_idx.open(filename_idx);
    if (file_idx.fail()) {
        std::cerr << "[Skin Reader " + side + "] Could not open taxel index file!" << std::endl;
        return false;
    }
    while (file_idx >> ind) {
        i++;
        idx.push_back(ind);
    }
    file_idx.close();

    // read information about skin sensor (also called taxel) position
    i = 0;
    file_pos.open(filename_pos);
    if (file_pos.fail()) {
        std::cerr << "[Skin Reader " + side + "] Could not open taxel position file!" << std::endl;
        return false;
    }
    while (file_pos >> val) {
        i++;
        i = i % 6;
        if (i < 3) {
            pos.push_back(val);
        }
        if (i % 6 == 0) {
            arr.push_back(pos);
            pos.clear();
        }
    }
    file_pos.close();

    part_tax_pos.idx = idx;
    part_tax_pos.arr = arr;

    taxel_pos_data[part] = part_tax_pos;

    return true;
}

// return the taxel positions given by the ini files
std::vector<std::vector<double>> SkinReader::GetTaxelPos(std::string skin_part)
/*
    params: std::string skin_part               -- skin part to load the data for ("arm", "forearm", "hand")

    return: std::vector<std::vector<double>>    -- Vector containing taxel positions -> reference frame depending on skin part
*/
{
    std::vector<std::vector<double>> taxel_positions;
    if (CheckInit()) {
        // auto root2part = kin_chains[skin_part]->getH();
        // auto part2root = yarp::math::SE3inv(root2part);

        auto init_pos = taxel_pos_data[skin_part].arr;
        auto idx_arr = taxel_pos_data[skin_part].idx;
        // std::cout << "index:" << idx_arr << std::endl;
        yarp::sig::Vector test;
        for (int i = 0; i < idx_arr.size(); i++) {
            if (idx_arr[i] > 0) taxel_positions.push_back(init_pos[i]);
        }
    }
    return taxel_positions;
}

// close and clean skin reader
void SkinReader::Close() {
    if (!port_hand.isClosed()) {
        yarp::os::Network::disconnect("/icubSim/skin/right_hand_comp", "/Skin_Reader/right_hand:i");
        port_hand.close();
    }
    if (!port_forearm.isClosed()) {
        yarp::os::Network::disconnect("/icubSim/skin/right_forearm_comp", "/Skin_Reader/right_forearm:i");
        port_forearm.close();
    }
    if (!port_arm.isClosed()) {
        yarp::os::Network::disconnect("/icubSim/skin/right_arm_comp", "/Skin_Reader/right_arm:i");
        port_arm.close();
    }

    yarp::os::Network::fini();
}
