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
        Add an instance of visual reader

        params: std::string name        -- name for the added visual reader in the map, can be freely selected
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
    if (parts_reader.count(name) != 0) {
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
    if (parts_writer.count(name) != 0) {
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
    if (tactile_reader.count(name) != 0) {
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
