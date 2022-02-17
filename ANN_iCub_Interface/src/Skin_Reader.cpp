/*
 *  Copyright (C) 2019-2022 Torsten Fietzek
 *
 *  Skin_Reader.cpp is part of the ANNarchy iCub interface
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

#include "Skin_Reader.hpp"

#include <yarp/dev/all.h>
#include <yarp/os/all.h>
#include <yarp/sig/all.h>

// #include <iCub/iKin/iKinFwd.h>    // iCub forward Kinematics
// #include <iCub/skinDynLib/iCubSkin.h>

#include <fstream>
#include <iostream>
#include <map>
#include <queue>
#include <string>

#include "INI_Reader/INIReader.h"
#include "Module_Base_Class.hpp"
#ifdef _USE_GRPC
#include "ProvideInputServer.h"
#endif

// Destructor
SkinReader::~SkinReader() { Close(); }

/*** public methods for the user ***/
bool SkinReader::Init(std::string name, char arm, bool norm_data, std::string ini_path) {
    /*
        Init skin reader with given parameters

        params: char arm        -- character to choose the arm side (r/R for right; l/L for left)
                bool norm_data  -- true for normalized tactile data (iCub data: [0..255]; normalized [0..1.0])
                ini_path        -- Path to the "interface_param.ini"-file

        return: bool            -- return True, if successful
    */

    if (!this->dev_init) {
        // check YARP-Network
        if (!yarp::os::Network::checkNetwork()) {
            std::cerr << "[Skin Reader] YARP Network is not online. Check nameserver is running!" << std::endl;
            return false;
        }

#ifdef _USE_LOG_QUIET
        // set YARP loging level to warnings, if the respective environment variable is set
        auto yarp_quiet = GetEnvVar("YARP_QUIET");
        if (yarp_quiet == "on" or yarp_quiet == "1") {
            yarp::os::Log::setMinimumPrintLevel(yarp::os::Log::WarningType);
        }
#endif

        // Prepare Reader for normalization
        std::string norm;
        if (norm_data) {
            norm_fac = 1.0 / 255.0;
            norm = "normalized";
        } else {
            norm_fac = 1.0;
            norm = "raw";
        }

        // Open ini file
        INIReader reader_gen(ini_path + "/interface_param.ini");
        if (reader_gen.ParseError() != 0) {
            std::cerr << "[Skin Reader] Error in parsing the ini-file! Please check the ini-path \"" << ini_path << "\" and the ini file content!" << std::endl;
            return false;
        }

        // Set side and read taxel position files depending on selected arm side
        std::string data_dir = reader_gen.Get("skin", "sensor_position_dir", "../data/sensor_positions/");
        if (arm == 'r' || arm == 'R') {
            side = "right";
            bool read_err_arm = !ReadTaxelPos(data_dir + "right_arm_mesh_idx.txt", data_dir + "right_arm_mesh_pos.txt", "arm");
            bool read_err_farm = !ReadTaxelPos(data_dir + "right_forearm_V2_idx.txt", data_dir + "right_forearm_V2_pos.txt", "forearm");
            bool read_err_hand = !ReadTaxelPos(data_dir + "right_hand_V2_1_idx.txt", data_dir + "right_hand_V2_1_pos.txt", "hand");
            if (read_err_arm || read_err_farm || read_err_hand) {
                std::cerr << "[Skin Reader] Error while reading taxel positions! Check the existence of the .ini files in the "
                             "sensor_positions folder."
                          << std::endl;
                return false;
            }
        } else if (arm == 'l' || arm == 'L') {
            side = "left";
            bool read_err_arm = !ReadTaxelPos(data_dir + "left_arm_mesh_idx.txt", data_dir + "left_arm_mesh_pos.txt", "arm");
            bool read_err_farm = !ReadTaxelPos(data_dir + "left_forearm_V2_idx.txt", data_dir + "left_forearm_V2_pos.txt", "forearm");
            bool read_err_hand = !ReadTaxelPos(data_dir + "left_hand_V2_1_idx.txt", data_dir + "left_hand_V2_1_pos.txt", "hand");

            if (read_err_arm || read_err_farm || read_err_hand) {
                std::cerr << "[Skin Reader] Error while reading taxel positions! Check the existence of the .ini files in the "
                             "sensor_positions folder."
                          << std::endl;
                return false;
            }
        } else {
            std::cerr << "[Skin Reader] No correct side descriptor: Use R/r for the right arm and L/l for the left arm!" << std::endl;
            return false;
        }

        // Read configuration data from ini file
        bool on_Simulator = reader_gen.GetBoolean("general", "simulator", true);
        std::string robot_port_prefix = reader_gen.Get("general", "robot_port_prefix", "/icubSim");
        if (on_Simulator && (robot_port_prefix != "/icubSim")) {
            std::cerr << "[Skin Reader " << side << "] The port prefix does not match the default simulator prefix!" << std::endl;
        }
        std::string client_port_prefix = reader_gen.Get("general", "client_port_prefix", "/client");

        // Open and connect YARP-Port to read upper arm skin sensor data
        std::string port_name_arm = client_port_prefix + "/" + name + "/Skin_Reader_" + norm + "/" + side + "_arm:i";
        if (!port_arm.open(port_name_arm)) {
            std::cerr << "[Skin Reader " << side << "] Could not open skin arm port!" << std::endl;
            return false;
        }
        if (!yarp::os::Network::connect((robot_port_prefix + "/skin/" + side + "_arm_comp").c_str(), port_name_arm.c_str())) {
            std::cerr << "[Skin Reader " << side << "] Could not connect skin arm port!" << std::endl;
            return false;
        }

        // Open and connect YARP-Port to read forearm skin sensor data
        std::string port_name_farm = client_port_prefix + "/" + name + "/Skin_Reader_" + norm + "/" + side + "_forearm:i";
        if (!port_forearm.open(port_name_farm)) {
            std::cerr << "[Skin Reader" << side << "] Could not open skin forearm port!" << std::endl;
            return false;
        }
        if (!yarp::os::Network::connect((robot_port_prefix + "/skin/" + side + "_forearm_comp").c_str(), port_name_farm.c_str())) {
            std::cerr << "[Skin Reader " << side << "] Could not connect skin forearm port!" << std::endl;
            return false;
        }

        // Open and connect YARP-Port to read hand skin sensor data
        std::string port_name_hand = client_port_prefix + "/" + name + "/Skin_Reader_" + norm + "/" + side + "_hand:i";
        if (!port_hand.open(port_name_hand)) {
            std::cerr << "[Skin Reader " << side << "] Could not open skin hand port!" << std::endl;
            return false;
        }
        if (!yarp::os::Network::connect((robot_port_prefix + "/skin/" + side + "_hand_comp").c_str(), port_name_hand.c_str())) {
            std::cerr << "[Skin Reader " << side << "] Could not connect skin hand port!" << std::endl;
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

        this->type = "SkinReader";
        this->icub_part = std::string(1, arm);
        init_param["name"] = name;
        init_param["arm"] = std::to_string(arm);
        init_param["norm_data"] = std::to_string(norm_data);
        init_param["ini_path"] = ini_path;
        this->dev_init = true;
        return true;
    } else {
        std::cerr << "[Skin Reader " << side << "] Initialization aready done!" << std::endl;
        return false;
    }
}

#ifdef _USE_GRPC
bool SkinReader::InitGRPC(std::string name, char arm, bool norm_data, std::string ini_path, std::string ip_address, unsigned int port) {
    if (!this->dev_init) {
        if (this->Init(name, arm, norm_data, ini_path)) {
            this->_ip_address = ip_address;
            this->_port = port;
            this->skin_source = new ServerInstance(ip_address, port, this);
            this->server_thread = std::thread(&ServerInstance::wait, this->skin_source);
            init_param["ip_address"] = ip_address;
            init_param["port"] = std::to_string(port);
            this->dev_init_grpc = true;
            return true;
        } else {
            std::cerr << "[Skin Reader] Initialization failed!" << std::endl;
            return false;
        }
    } else {
        std::cerr << "[Skin Reader] Initialization already done!" << std::endl;
        return false;
    }
}
#else
bool SkinReader::InitGRPC(std::string name, char arm, bool norm_data, std::string ini_path, std::string ip_address, unsigned int port) {
    std::cerr << "[Skin Reader] gRPC is not included in the setup process!" << std::endl;
    return false;
}
#endif

void SkinReader::Close() {
    /*
        Close and clean skin reader
    */

    if (!port_hand.isClosed()) {
        yarp::os::Network::disconnect(("/icubSim/skin/" + side + "_hand_comp").c_str(), ("/Skin_Reader/" + side + "_hand:i").c_str());
        port_hand.close();
    }
    if (!port_forearm.isClosed()) {
        yarp::os::Network::disconnect(("/icubSim/skin/" + side + "_forearm_comp").c_str(), ("/Skin_Reader/" + side + "_forearm:i").c_str());
        port_forearm.close();
    }
    if (!port_arm.isClosed()) {
        yarp::os::Network::disconnect(("/icubSim/skin/" + side + "_arm_comp").c_str(), ("/Skin_Reader/" + side + "_arm:i").c_str());
        port_arm.close();
    }
#ifdef _USE_GRPC
    if (dev_init_grpc) {
        skin_source->shutdown();
        server_thread.join();
        delete skin_source;
        dev_init_grpc = false;
    }
#endif
    this->dev_init = false;
}

std::vector<std::vector<double>> SkinReader::GetTactileArm() {
    /*
        Return tactile data for upper arm skin

        return: std::vector<std::vector<double>>    -- vector, containing the tactile data of the upper arm for the last time steps
    */
    CheckInit();
    auto data = arm_data;
    arm_data.clear();
    return data;
}

std::vector<std::vector<double>> SkinReader::GetTactileForearm() {
    /*
        Return tactile data for forearm skin

        return: std::vector<std::vector<double>>    -- vector, containing the tactile data of the forearm for the last time steps
    */
    CheckInit();
    auto data = forearm_data;
    forearm_data.clear();
    return data;
}

std::vector<std::vector<double>> SkinReader::GetTactileHand() {
    /*
        Return tactile data for hand skin

        return: std::vector<std::vector<double>>    -- vector, containing the tactile data of the hand for the last time steps
    */

    CheckInit();
    auto data = hand_data;
    hand_data.clear();
    return data;
}

std::vector<std::vector<double>> SkinReader::GetTaxelPos(std::string skin_part) {
    /*
        Return the taxel positions given by the ini files

        params: std::string skin_part               -- skin part to load the data for ("arm", "forearm", "hand")

        return: std::vector<std::vector<double>>    -- Vector containing taxel positions -> reference frame depending on skin part
    */

    std::vector<std::vector<double>> taxel_positions;
    if (CheckInit()) {
        // auto root2part = kin_chains[skin_part]->getH();
        // auto part2root = yarp::math::SE3inv(root2part);

        auto init_pos = taxel_pos_data[skin_part].arr;
        auto idx_arr = taxel_pos_data[skin_part].idx;
        // std::cout << "index:" << idx_arr << std::endl;
        yarp::sig::Vector test;
        for (unsigned int i = 0; i < idx_arr.size(); i++) {
            if (idx_arr[i] > 0) taxel_positions.push_back(init_pos[i]);
        }
    }
    return taxel_positions;
}

bool SkinReader::ReadTactile() {
    /*
        Read sensor data from iCub YARP ports

        return: bool            -- return True, if successful
    */

    if (CheckInit()) {
        tactile_arm = port_arm.read();
        tactile_forearm = port_forearm.read();
        tactile_hand = port_hand.read();

        bool no_error = true;

        // HAND
        if (tactile_hand != NULL) {
            std::string skin_part_h = "hand";
            // auto init_pos_h = taxel_pos_data[skin_part_h].arr;
            auto idx_arr_h = taxel_pos_data[skin_part_h].idx;
            std::vector<double> tmp_hand_data;
            for (unsigned int i = 0; i < idx_arr_h.size(); i++) {
                if (idx_arr_h[i] > 0) tmp_hand_data.push_back(tactile_hand->data()[i] * norm_fac);
            }
            hand_data.push_back(tmp_hand_data);
        } else {
            std::cerr << "[Skin Reader " + side + "] Error in reading hand tactile data from the iCub!" << std::endl;
            no_error = false;
        }

        // FOREARM
        if (tactile_forearm != NULL) {
            std::string skin_part_f = "forearm";
            // auto init_pos_f = taxel_pos_data[skin_part_f].arr;
            auto idx_arr_f = taxel_pos_data[skin_part_f].idx;
            std::vector<double> tmp_farm_data;
            for (unsigned int i = 0; i < idx_arr_f.size(); i++) {
                if (idx_arr_f[i] > 0) tmp_farm_data.push_back(tactile_forearm->data()[i] * norm_fac);
            }
            forearm_data.push_back(tmp_farm_data);
        } else {
            std::cerr << "[Skin Reader " + side + "] Error in reading forearm tactile data from the iCub!" << std::endl;
            no_error = false;
        }

        // ARM
        if (tactile_arm != NULL) {
            std::string skin_part_a = "arm";
            // auto init_pos_a = taxel_pos_data[skin_part_a].arr;
            auto idx_arr_a = taxel_pos_data[skin_part_a].idx;
            std::vector<double> tmp_arm_data;
            for (unsigned int i = 0; i < idx_arr_a.size(); i++) {
                if (idx_arr_a[i] > 0) tmp_arm_data.push_back(tactile_arm->data()[i] * norm_fac);
            }
            arm_data.push_back(tmp_arm_data);
        } else {
            std::cerr << "[Skin Reader " + side + "] Error in reading arm tactile data from the iCub!" << std::endl;
            no_error = false;
        }
        return no_error;
    } else {
        return false;
    }
}

unsigned int SkinReader::GetTactileArmSize() { return taxel_pos_data["arm"].idx.size(); }
unsigned int SkinReader::GetTactileForearmSize() { return taxel_pos_data["forearm"].idx.size(); }
unsigned int SkinReader::GetTactileHandSize() { return taxel_pos_data["hand"].idx.size(); }

/*** gRPC related functions ***/
// TODO seperated functions for different sections
#ifdef _USE_GRPC
std::vector<double> SkinReader::provideData(int section) {
    std::vector<double> sensor_data;

    if (section == 3) {
        tactile_hand = port_hand.read();
        if (tactile_hand != NULL) {
            std::string skin_part_h = "hand";
            auto idx_arr_h = taxel_pos_data[skin_part_h].idx;
            for (unsigned int i = 0; i < idx_arr_h.size(); i++) {
                if (idx_arr_h[i] > 0) sensor_data.push_back(tactile_hand->data()[i] * norm_fac);
            }
        } else {
            std::cerr << "[Skin Reader " + side + "] Error in reading hand tactile data from the iCub!" << std::endl;
        }

    } else if (section == 2) {
        tactile_forearm = port_forearm.read();
        if (tactile_forearm != NULL) {
            std::string skin_part_f = "forearm";
            auto idx_arr_f = taxel_pos_data[skin_part_f].idx;
            for (unsigned int i = 0; i < idx_arr_f.size(); i++) {
                if (idx_arr_f[i] > 0) sensor_data.push_back(tactile_forearm->data()[i] * norm_fac);
            }
        } else {
            std::cerr << "[Skin Reader " + side + "] Error in reading forearm tactile data from the iCub!" << std::endl;
        }

    } else if (section == 1) {
        tactile_arm = port_arm.read();
        // ARM
        if (tactile_arm != NULL) {
            std::string skin_part_a = "arm";
            auto idx_arr_a = taxel_pos_data[skin_part_a].idx;
            for (unsigned int i = 0; i < idx_arr_a.size(); i++) {
                if (idx_arr_a[i] > 0) sensor_data.push_back(tactile_arm->data()[i] * norm_fac);
            }
        } else {
            std::cerr << "[Skin Reader " + side + "] Error in reading arm tactile data from the iCub!" << std::endl;
        }
    } else {
        std::cerr << "[Skin Reader " + side + "] Undefined skin section!" << std::endl;
    }
    return sensor_data;
}
#endif

/*** auxilary functions ***/
bool SkinReader::ReadTaxelPos(std::string filename_idx, std::string filename_pos, std::string part) {
    /*
        Read information about taxel position from config files

        params: std::string filename_idx    -- filename, containing the path, of the file with the taxel index data
                std::string filename_pos    -- filename, containing the path, of the file with the taxel position data
                std::string part            -- skin part to load the data for (e.g. forearm)

        return: bool                        -- return True, if successful
    */

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
