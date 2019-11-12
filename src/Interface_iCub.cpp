/*
 *  Copyright (C) 2019 Torsten Follak
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

#include <string>
#include <vector>

#include "Interface_iCub.hpp"

#include "Joint_Reader.hpp"
#include "Joint_Writer.hpp"
#include "Skin_Reader.hpp"
#include "Visual_Reader.hpp"

iCubANN my_interface;

// add an instance of joint reader
void iCubANN::AddJointReader(std::string name)
/*
    params: std::string name        -- name for the added joint reader in the map, can be freely selected
*/
{
    if (parts_reader.count(name) == 0) {
        parts_reader[name] = new JointReader();
    } else {
        std::cerr << "[Joint Reader] Name \"" + name + "\" is already used.\n";
    }
}

// add an instance of joint writer
void iCubANN::AddJointWriter(std::string name)
/*
    params: std::string name        -- name for the added joint writer in the map, can be freely selected
*/
{
    if (parts_writer.count(name) == 0) {
        parts_writer[name] = new JointWriter();
    } else {
        std::cerr << "[Joint Writer] Name \"" + name + "\" is already used.\n";
    }
}

// add an instance of skin reader
void iCubANN::AddSkinReader(std::string name)
/*
    params: std::string name        -- name for the added skin reader in the map, can be freely selected
*/
{
    if (tactile_reader.count(name) == 0) {
        tactile_reader[name] = new SkinReader();
    } else {
        std::cerr << "[Skin Reader] Name \"" + name + "\" is already used.\n";
    }
}

// add an instance of visual reader
void iCubANN::AddVisualReader()
/*
    params: std::string name        -- name for the added visual reader in the map, can be freely selected
*/
{
    if (visual_input == NULL) {
        visual_input = new VisualReader();
    } else {
        std::cerr << "Visual Reader is already defined.\n";
    }
}

// Access to joint reader member functions //
// initialize the joint reader with given parameters
bool iCubANN::JointRInit(std::string name, std::string part, double sigma, int pop_size, double deg_per_neuron)
/*
    params: std::string name        -- name of the selected joint reader
            std::string part        -- string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso}
            sigma                   -- sigma for the joints angles populations coding 
            int pop_size            -- number of neurons per population, encoding each one joint angle; only works if parameter "deg_per_neuron" is not set
            double deg_per_neuron   -- degree per neuron in the populations, encoding the joints angles; if set: population size depends on joint working range

    return: bool                    -- return True, if successful
*/
{
    if (parts_reader.count(name)) {
        return parts_reader[name]->Init(part, sigma, pop_size, deg_per_neuron);
    } else {
        std::cerr << "[Joint Reader] " << name << ": This name is not defined." << std::endl;
        return false;
    }
}

// get the size of the populations encoding the joint angles
std::vector<int> iCubANN::JointRGetNeuronsPerJoint(std::string name)
/*
    params: std::string name        -- name of the selected joint reader

    return: std::vector<int>        -- return vector, containing the population size for every joint
*/
{
    if (parts_reader.count(name)) {
        return parts_reader[name]->GetNeuronsPerJoint();
    } else {
        std::cerr << "[Joint Reader] " << name << ": This name is not defined." << std::endl;
        std::vector<int> empty;
        return empty;
    }
}

// get the resolution in degree of the populations encoding the joint angles
std::vector<double> iCubANN::JointRGetJointsDegRes(std::string name)
/*
    params: std::string name        -- name of the selected joint reader

    return: std::vector<double>     -- return vector, containing the resolution for every joints population codimg in degree
*/
{
    if (parts_reader.count(name)) {
        return parts_reader[name]->GetJointsDegRes();
    } else {
        std::cerr << "[Joint Reader] " << name << ": This name is not defined." << std::endl;
        std::vector<double> empty;
        return empty;
    }
}

// read one joint and return joint angle directly as double value
double iCubANN::JointRReadDouble(std::string name, int joint)
/*
    params: std::string name    -- name of the selected joint reader
            int joint           -- joint number of the robot part

    return: double              -- joint angle read from the robot
*/
{
    if (parts_reader.count(name)) {
        return parts_reader[name]->ReadDouble(joint);
    } else {
        std::cerr << "[Joint Reader] " << name << ": This name is not defined." << std::endl;
        double empty;
        return empty;
    }
}

// read one joint and return the joint angle encoded in a vector
std::vector<double> iCubANN::JointRReadOne(std::string name, int joint)
/*
    params: std::string name        -- name of the selected joint reader
            int joint               -- joint number of the robot part

    return: std::vector<double>     -- population vector encoding the joint angle
*/
{
    if (parts_reader.count(name)) {
        return parts_reader[name]->ReadOne(joint);
    } else {
        std::cerr << "[Joint Reader] " << name << ": This name is not defined." << std::endl;
        std::vector<double> empty;
        return empty;
    }
}

// read all joints and return the joint angles encoded in vectors
std::vector<std::vector<double> > iCubANN::JointRReadAll(std::string name)
/*
    params: std::string name                    -- name of the selected joint reader

    return: std::vector<std::vector<double>>    -- population vectors encoding every joint angle from associated robot part
*/
{
    printf("readall1");
    if (parts_reader.count(name)) {
        printf("readall2");
        return parts_reader[name]->ReadAll();
    } else {
        std::cerr << "[Joint Reader] " << name << ": This name is not defined." << std::endl;
        std::vector<std::vector<double>> empty;
        return empty;
    }
}

// close joint reader with cleanup
void iCubANN::JointRClose(std::string name)
/*
    params: std::string name        -- name of the selected joint reader
*/
{
    if (parts_reader.count(name)) {
        parts_reader[name]->Close();
    } else {
        std::cerr << "[Joint Reader] " << name << ": This name is not defined." << std::endl;
    }
}

// Access to joint writer member functions //
// initialize the joint writer with given parameters
bool iCubANN::JointWInit(std::string name, std::string part, int pop_size, double deg_per_neuron)
/*
    params: std::string name        -- name of the selected joint writer
            std::string part        -- string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso} 
            int pop_size            -- number of neurons per population, encoding each one joint angle; only works if parameter "deg_per_neuron" is not set double
            deg_per_neuron          -- degree per neuron in the populations, encoding the joints angles; if set: population size depends on joint working range

    return: bool                    -- return True, if successful
*/
{
    if (parts_writer.count(name)) {
        return parts_writer[name]->Init(part, pop_size, deg_per_neuron);
    } else {
        std::cerr << "[Joint Writer] " << name << ": This name is not defined." << std::endl;
        return false;
    }
}

// get the size of the populations encoding the joint angles
std::vector<int> iCubANN::JointWGetNeuronsPerJoint(std::string name)
/*
    params: std::string name        -- name of the selected joint writer

    return: std::vector<int>        -- return vector, containing the population size for every joint
*/
{
    if (parts_writer.count(name)) {
        return parts_writer[name]->GetNeuronsPerJoint();
    } else {
        std::cerr << "[Joint Writer] " << name << ": This name is not defined." << std::endl;
        std::vector<int> empty;
        return empty;
    }
}

// get the resolution in degree of the populations encoding the joint angles
std::vector<double> iCubANN::JointWGetJointsDegRes(std::string name)
/*
    params: std::string name        -- name of the selected joint writer

    return: std::vector<double>     -- return vector, containing the resolution for every joints population codimg in degree
*/
{
    if (parts_writer.count(name)) {
        return parts_writer[name]->GetJointsDegRes();
    } else {
        std::cerr << "[Joint Writer] " << name << ": This name is not defined." << std::endl;
        std::vector<double> empty;
        return empty;
    }
}

// write one joint as double value
bool iCubANN::JointWWriteDouble(std::string name, double position, int joint, bool blocking)
/*
    params: std::string name    -- name of the selected joint writer
            double position     -- joint angle to write to the robot joint
            int joint           -- joint number of the robot part
            bool blocking       -- if True, function waits for end of movement

    return: bool                -- return True, if successful
*/
{
    if (parts_writer.count(name)) {
        return parts_writer[name]->WriteDouble(position, joint, blocking);
    } else {
        std::cerr << "[Joint Writer] " << name << ": This name is not defined." << std::endl;
        return false;
    }
}

// write one joint with the joint angle encoded in a population
bool iCubANN::JointWWriteOne(std::string name, std::vector<double> position_pop, int joint, bool blocking)
/*
    params: std::string name        -- name of the selected joint writer
            std::vector<double>     -- population encoded joint angle for writing to the robot joint 
            int joint               -- joint number of the robot part 
            bool blocking           -- if True, function waits for end of movement

    return: bool                    -- return True, if successful
*/
{
    if (parts_writer.count(name)) {
        return parts_writer[name]->WriteOne(position_pop, joint, blocking);
    } else {
        std::cerr << "[Joint Writer] " << name << ": This name is not defined." << std::endl;
        return false;
    }
}

// write all joints with joint angles encoded in populations
bool iCubANN::JointWWriteAll(std::string name, std::vector<std::vector<double>> position_pops, bool blocking)
/*
    params: std::string name                    -- name of the selected joint writer 
            std::vector<std::vector<double>>    -- populations encoding every joint angle for writing them to the associated robot part 
            bool blocking                       -- if True, function waits for end of movement

    return: bool                                -- return True, if successful
*/
{
    if (parts_writer.count(name)) {
        return parts_writer[name]->WriteAll(position_pops, blocking);
    } else {
        std::cerr << "[Joint Writer] " << name << ": This name is not defined." << std::endl;
        return false;
    }
}

// close joint reader with cleanup
void iCubANN::JointWClose(std::string name)
/*
    params: std::string name        -- name of the selected joint writer
*/
{
    if (parts_writer.count(name)) {
        parts_writer[name]->Close();
    } else {
        std::cerr << "[Joint Writer] " << name << ": This name is not defined." << std::endl;
    }
}

// Access to skin reader member functions //
// init skin reader with given parameters
bool iCubANN::SkinRInit(std::string name, char arm)
/*
    params: std::string name        -- name of the selected skin reader
            char arm                -- character to choose the arm side (r/R for right; l/L for left)

    return: bool                    -- return True, if successful
*/
{
    if (tactile_reader.count(name)) {
        return tactile_reader[name]->Init(arm);
    } else {
        std::cerr << "[Skin Reader] " << name << ": This name is not defined." << std::endl;
        return false;
    }
}

// read sensor data
void iCubANN::SkinRReadTactile(std::string name)
/*
    params: std::string name        -- name of the selected skin reader
*/
{
    if (tactile_reader.count(name)) {
        tactile_reader[name]->ReadTactile();
    } else {
        std::cerr << "[Skin Reader] " << name << ": This name is not defined." << std::endl;
    }
}

// return tactile data for hand skin
std::vector<double> iCubANN::SkinRGetTactileHand(std::string name)
/*
    params: std::string name        -- name of the selected skin reader
*/
{
    if (tactile_reader.count(name)) {
        return tactile_reader[name]->GetTactileHand();
    } else {
        std::cerr << "[Skin Reader] " << name << ": This name is not defined." << std::endl;
        std::vector<double> empty;
        return empty;
    }
}

// return tactile data for forearm skin
std::vector<double> iCubANN::SkinRGetTactileForearm(std::string name)
/*
    params: std::string name        -- name of the selected skin reader
*/
{
    if (tactile_reader.count(name)) {
        return tactile_reader[name]->GetTactileForearm();
    } else {
        std::cerr << "[Skin Reader] " << name << ": This name is not defined." << std::endl;
        std::vector<double> empty;
        return empty;
    }
}

// return tactile data for upper arm skin
std::vector<double> iCubANN::SkinRGetTactileArm(std::string name)
/*
    params: std::string name        -- name of the selected skin reader
*/
{
    if (tactile_reader.count(name)) {
        return tactile_reader[name]->GetTactileArm();
    } else {
        std::cerr << "[Skin Reader] " << name << ": This name is not defined." << std::endl;
        std::vector<double> empty;
        return empty;
    }
}

// return the taxel positions given by the ini files
std::vector<std::vector<double>> iCubANN::SkinRGetTaxelPos(std::string name, std::string skin_part)
/*
    params: std::string name                    -- name of the selected skin reader 
            std::string skin_part               -- skin part to load the data for ("arm", "forearm", "hand")

    return: std::vector<std::vector<double>>    -- Vector containing taxel positions -> reference frame depending on skin part
*/
{
    if (tactile_reader.count(name)) {
        return tactile_reader[name]->GetTaxelPos(skin_part);
    } else {
        std::cerr << "[Skin Reader] " << name << ": This name is not defined." << std::endl;
        std::vector<std::vector<double>> empty;
        return empty;
    }
}

// close and clean skin reader
void iCubANN::SkinRClose(std::string name)
/*
    params: std::string name        -- name of the selected skin reader
*/
{
    if (tactile_reader.count(name)) {
        tactile_reader[name]->Close();
    } else {
        std::cerr << "[Skin Reader] " << name << ": This name is not defined." << std::endl;
    }
}

// Access to visual reader member functions //
// init Visual reader with given parameters for image resolution, field of view and eye selection
bool iCubANN::VisualRInit(char eye, double fov_width, double fov_height, int img_width, int img_height)
/*
    params: char eye            -- characteer representing the selected eye (l/L; r/R) 
            double fov_width    -- output field of view width in degree [0, 60] (input fov width: 60°) 
            double fov_height   -- output field of view height in degree [0, 48] (input fov height: 48°) 
            int img_width       -- output image width in pixel (input width: 320px) 
            int img_height      -- output image height in pixel (input height: 240px)

    return: bool                -- return True, if successful
*/
{
    return visual_input->Init(eye, fov_width, fov_height, img_width, img_height);
}

// start reading images from the iCub with YARP-RFModule
void iCubANN::VisualRStart(int argc, char *argv[])
/*
    params: int argc, char *argv[]  -- main function inputs from program call; can be used to configure RFModule; not implemented yet
*/
{
    visual_input->Start(argc, argv);
}

// stop reading images from the iCub, by terminating the RFModule
void iCubANN::VisualRStop() { visual_input->Stop(); }

// read image vector from the image buffer and remove it from the buffer
std::vector<double> iCubANN::VisualRReadFromBuf()
/*
    return: std::vector<double>     -- image (1D-vector) from the image buffer
*/
{
    return visual_input->ReadFromBuf();
}
