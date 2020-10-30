/*
 *  Copyright (C) 2019-2020 Torsten Follak; Helge Ülo Dinkelbach
 *
 *  Interface_iCub.cpp is part of the iCub ANNarchy interface
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

#include "Interface_iCub.hpp"

#include <string>
#include <vector>

#include "Joint_Reader.hpp"
#include "Joint_Writer.hpp"
#include "Skin_Reader.hpp"
#include "Visual_Reader.hpp"

iCubANN my_interface;

// Destructor
iCubANN::~iCubANN() {
    parts_writer.clear();
    parts_reader.clear();
    tactile_reader.clear();
    Yarp.fini();
}

/***  Add intstances of the interface modules ***/
bool iCubANN::AddJointReader(std::string name) {
    /*
        Add an instance of joint reader

        params: std::string name        -- name for the added joint reader in the map, can be freely selected
    */

    if (parts_reader.count(name) == 0) {
        parts_reader[name] = std::shared_ptr<JointReader>(new JointReader());
        return true;
    } else {
        std::cerr << "[Joint Reader] Name \"" + name + "\" is already used." << std::endl;
        return false;
    }
}

bool iCubANN::AddJointWriter(std::string name) {
    /*
        Add an instance of joint writer

        params: std::string name        -- name for the added joint writer in the map, can be freely selected
    */

    if (parts_writer.count(name) == 0) {
        parts_writer[name] = std::shared_ptr<JointWriter>(new JointWriter());
        return true;
    } else {
        std::cerr << "[Joint Writer] Name \"" + name + "\" is already used." << std::endl;
        return false;
    }
}

bool iCubANN::AddSkinReader(std::string name) {
    /*
        Add an instance of skin reader

        params: std::string name        -- name for the added skin reader in the map, can be freely selected
    */

    if (tactile_reader.count(name) == 0) {
        tactile_reader[name] = std::shared_ptr<SkinReader>(new SkinReader());
        return true;
    } else {
        std::cerr << "[Skin Reader] Name \"" + name + "\" is already used." << std::endl;
        return false;
    }
}

bool iCubANN::AddVisualReader() {
    /*
        Add the instance of visual reader
    */

    if (visual_input == NULL) {
        visual_input = std::shared_ptr<VisualReader>(new VisualReader());
        return true;
    } else {
        std::cerr << "[Visual Reader] Visual Reader is already defined." << std::endl;
        return false;
    }
}

/***  Remove intstances of the interface modules ***/
bool iCubANN::RemoveJointReader(std::string name) {
    /*
        Remove the instance of the joint reader
    */
    if (parts_reader.count(name)) {
        parts_reader.erase(name);
        return true;
    } else {
        std::cerr << "[Joint Reader] Name \"" + name + "\" does not exists." << std::endl;
        return false;
    }
}

bool iCubANN::RemoveJointWriter(std::string name) {
    /*
        Remove the instance of the joint writer
    */
    if (parts_writer.count(name)) {
        parts_writer.erase(name);
        return true;
    } else {
        std::cerr << "[Joint Writer] Name \"" + name + "\" does not exists." << std::endl;
        return false;
    }
}

bool iCubANN::RemoveSkinReader(std::string name) {
    /*
        Remove the instance of the skin reader
    */
    if (tactile_reader.count(name)) {
        tactile_reader.erase(name);
        return true;
    } else {
        std::cerr << "[Skin Reader] Name \"" + name + "\" does not exists." << std::endl;
        return false;
    }
}

bool iCubANN::RemoveVisualReader() {
    /*
        Remove the instance of the visual reader
    */
    if (visual_input != NULL) {
        visual_input.reset();
        return true;
    } else {
        std::cerr << "[Visual Reader] Visual Reader does not exists." << std::endl;
        return false;
    }
}

std::vector<std::vector<double>> iCubANN::WriteActionSyncOne(std::string jwriter_name, std::string jreader_name, double angle, int joint,
                                                             double dt) {
    std::vector<std::vector<double>> sensor_values;

    // check name exists
    if (parts_writer.count(jwriter_name) && parts_reader.count(jreader_name)) {
        std::vector<std::vector<double>> sensor_values_tmp;

        // read sensor values at motion start
        sensor_values_tmp.push_back(parts_reader[jreader_name]->ReadDoubleOneTime(joint));
        // start joint motion
        bool in_motion = parts_writer[jwriter_name]->WriteDoubleOne(angle, joint, false, "abs");
        if (!in_motion) {
            std::cout << "[Action Sync] Did not start the motion. The position is already reached or an error occured!" << std::endl;
        }
        while (in_motion) {
            // read sensor values, while in motion
            sensor_values_tmp.push_back(parts_reader[jreader_name]->ReadDoubleOneTime(joint));
            // check if motion is finished
            in_motion = !parts_writer[jwriter_name]->MotionDone();
        }

        // offline binning sensor values to timegrid
        std::vector<double> sensor_tmp, sensor_tmp1, filled_steps;
        sensor_values.push_back(sensor_values_tmp.front());
        double t_start = sensor_values[0][0];
        int fill_count = 0;
        double window = dt / 2.;
        double t_old = 0.;
        sensor_values[0][0] = t_old;
        double t_k, t_k1;
        for (int k = 1; k < sensor_values_tmp.size(); k++) {
            sensor_tmp = sensor_values_tmp[k];
            t_k = sensor_tmp[0] - t_start;
            t_k1 = sensor_values.back()[0];

            // replace last value, if new value fits better
            if (std::abs(t_k - t_old) < std::abs(t_k1 - t_old)) {
                sensor_values[k] = sensor_values_tmp[k - 1];

                // check if value should be pushed to timed vector
            } else if (t_k > (t_old + dt - window)) {
                if (t_k < (t_old + dt + window)) {
                    sensor_tmp[0] = t_old + dt;
                    t_old = t_old + dt;
                    sensor_values.push_back(sensor_tmp);
                } else {
                    // fill with last values, while time distance is too high
                    while (t_k > (t_old + 2 * dt - window)) {
                        sensor_tmp1 = sensor_values.back();
                        sensor_tmp1[0] = t_old + dt;
                        t_old = t_old + dt;
                        sensor_values.push_back(sensor_tmp1);
                        fill_count++;
                        filled_steps.push_back(t_old);
                    }
                    // value is near to new time -> fill value in
                    if (t_k < (t_old + dt + window) && (sensor_tmp[0] - t_start) > (t_old + dt - window)) {
                        sensor_tmp[0] = t_old + dt;
                        t_old = t_old + dt;
                        sensor_values.push_back(sensor_tmp);
                    }
                }
            }
        }
        std::cout << "Fill count: " << fill_count << "Steps: " << filled_steps << std::endl;
        if (fill_count > sensor_values.size() / 2) {
            std::cerr << "[Action Sync] Warning! Half of the values are filled, due to slow sensor rate. Please increase the dt value!"
                      << std::endl;
        }
        return sensor_values;
    } else {
        std::cerr << "[Action Sync] At least one of the names does not exists." << std::endl;
        return sensor_values;
    }
}

std::vector<std::vector<double>> iCubANN::WriteActionSyncMult(std::string jwriter_name, std::string jreader_name,
                                                              std::vector<double> angles, std::vector<int> joint_selection, double dt) {
    std::vector<std::vector<double>> sensor_values;

    // check name exists
    if (parts_writer.count(jwriter_name) && parts_reader.count(jreader_name)) {
        std::vector<std::vector<double>> sensor_values_tmp;

        // read sensor values at motion start
        sensor_values_tmp.push_back(parts_reader[jreader_name]->ReadDoubleMultipleTime(joint_selection));
        // start joint motion
        bool in_motion = parts_writer[jwriter_name]->WriteDoubleMultiple(angles, joint_selection, false, "abs");
        if (!in_motion) {
            std::cout << "[Action Sync] Did not start the motion. The position is already reached or an error occured!" << std::endl;
        }
        while (in_motion) {
            // read sensor values, while in motion
            sensor_values_tmp.push_back(parts_reader[jreader_name]->ReadDoubleMultipleTime(joint_selection));
            // check if motion is finished
            in_motion = !parts_writer[jwriter_name]->MotionDone();
        }

        // offline binning sensor values to timegrid
        std::vector<double> sensor_tmp, sensor_tmp1, filled_steps;
        sensor_values.push_back(sensor_values_tmp.front());
        double t_start = sensor_values[0][0];
        int fill_count = 0;
        double window = dt / 2.;
        double t_old = 0.;
        sensor_values[0][0] = t_old;
        double t_k, t_k1;
        for (int k = 1; k < sensor_values_tmp.size(); k++) {
            sensor_tmp = sensor_values_tmp[k];
            t_k = sensor_tmp[0] - t_start;
            t_k1 = sensor_values.back()[0];

            // replace last value, if new value fits better
            if (std::abs(t_k - t_old) < std::abs(t_k1 - t_old)) {
                sensor_values[k] = sensor_values_tmp[k - 1];

                // check if value should be pushed to timed vector
            } else if (t_k > (t_old + dt - window)) {
                if (t_k < (t_old + dt + window)) {
                    sensor_tmp[0] = t_old + dt;
                    t_old = t_old + dt;
                    sensor_values.push_back(sensor_tmp);
                } else {
                    // fill with last values, while time distance is too high
                    while (t_k > (t_old + 2 * dt - window)) {
                        sensor_tmp1 = sensor_values.back();
                        sensor_tmp1[0] = t_old + dt;
                        t_old = t_old + dt;
                        sensor_values.push_back(sensor_tmp1);
                        fill_count++;
                        filled_steps.push_back(t_old);
                    }
                    // value is near to new time -> fill value in
                    if (t_k < (t_old + dt + window) && (sensor_tmp[0] - t_start) > (t_old + dt - window)) {
                        sensor_tmp[0] = t_old + dt;
                        t_old = t_old + dt;
                        sensor_values.push_back(sensor_tmp);
                    }
                }
            }
        }
        std::cout << "Fill count: " << fill_count << "Steps: " << filled_steps << std::endl;
        if (fill_count > sensor_values.size() / 2) {
            std::cerr << "[Action Sync] Warning! Half of the values are filled, due to slow sensor rate. Please increase the dt value!"
                      << std::endl;
        }
        return sensor_values;
    } else {
        std::cerr << "[Joint Reader/Writer] At least one of the names does not exists." << std::endl;
        return sensor_values;
    }
}

std::vector<std::vector<double>> iCubANN::WriteActionSyncAll(std::string jwriter_name, std::string jreader_name, std::vector<double> angles,
                                                             double dt) {
    std::vector<std::vector<double>> sensor_values;

    // check name exists
    if (parts_writer.count(jwriter_name) && parts_reader.count(jreader_name)) {
        std::vector<std::vector<double>> sensor_values_tmp;

        // read sensor values at motion start
        sensor_values_tmp.push_back(parts_reader[jreader_name]->ReadDoubleAllTime());
        // start joint motion
        bool in_motion = parts_writer[jwriter_name]->WriteDoubleAll(angles, false, "abs");
        if (!in_motion) {
            std::cout << "Did not start the motion. The position is already reached or an error occured!" << std::endl;
        }
        while (in_motion) {
            // read sensor values, while in motion
            sensor_values_tmp.push_back(parts_reader[jreader_name]->ReadDoubleAllTime());
            // check if motion is finished
            in_motion = !parts_writer[jwriter_name]->MotionDone();
        }

        // offline binning sensor values to timegrid
        std::vector<double> sensor_tmp, sensor_tmp1, filled_steps;
        sensor_values.push_back(sensor_values_tmp.front());
        double t_start = sensor_values[0][0];
        int fill_count = 0;
        double window = dt / 2.;
        double t_old = 0.;
        sensor_values[0][0] = t_old;
        double t_k, t_k1;
        for (int k = 1; k < sensor_values_tmp.size(); k++) {
            sensor_tmp = sensor_values_tmp[k];
            t_k = sensor_tmp[0] - t_start;
            t_k1 = sensor_values.back()[0];

            // replace last value, if new value fits better
            if (std::abs(t_k - t_old) < std::abs(t_k1 - t_old)) {
                sensor_values[k] = sensor_values_tmp[k - 1];

                // check if value should be pushed to timed vector
            } else if (t_k > (t_old + dt - window)) {
                if (t_k < (t_old + dt + window)) {
                    sensor_tmp[0] = t_old + dt;
                    t_old = t_old + dt;
                    sensor_values.push_back(sensor_tmp);
                } else {
                    // fill with last values, while time distance is too high
                    while (t_k > (t_old + 2 * dt - window)) {
                        sensor_tmp1 = sensor_values.back();
                        sensor_tmp1[0] = t_old + dt;
                        t_old = t_old + dt;
                        sensor_values.push_back(sensor_tmp1);
                        fill_count++;
                        filled_steps.push_back(t_old);
                    }
                    // value is near to new time -> fill value in
                    if (t_k < (t_old + dt + window) && (sensor_tmp[0] - t_start) > (t_old + dt - window)) {
                        sensor_tmp[0] = t_old + dt;
                        t_old = t_old + dt;
                        sensor_values.push_back(sensor_tmp);
                    }
                }
            }
        }
        std::cout << "Fill count: " << fill_count << "Steps: " << filled_steps << std::endl;
        if (fill_count > sensor_values.size() / 2) {
            std::cerr << "[Action Sync] Warning! Half of the values are filled, due to slow sensor rate. Please increase the dt value!"
                      << std::endl;
        }
        return sensor_values;
    } else {
        std::cerr << "[Joint Reader/Writer] At least one of the names does not exists." << std::endl;
        return sensor_values;
    }
}