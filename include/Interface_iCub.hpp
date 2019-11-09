/*
 *  Copyright (C) 2019 Torsten Follak
 *
 *  Interface_iCub.hpp is part of the iCub ANNarchy interface
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

#include <map>
#include <string>

#include "Joint_Reader.hpp"
#include "Joint_Writer.hpp"
#include "Skin_Reader.hpp"
#include "Visual_Reader.hpp"

struct iCub_ANN
{
    Visual_Reader *visual_input;                         // associated visual reader (only one possible for left/right eye)
    std::map<std::string, Joint_Reader *> parts_reader;  // associated joint readers (one for every robot part)
    std::map<std::string, Joint_Writer *> parts_writer;  // associated joint writers (one for every robot part)
    std::map<std::string, Skin_Reader *> tactile_reader; // associated skin reader

    // add an instance of joint reader
    void AddJointReader(std::string name);
    // add an instance of joint writer
    void AddJointWriter(std::string name);
    // add an instance of skin reader
    void AddSkinReader(std::string name);
    // add an instance of visual reader
    void AddVisualReader();

    // Access to visual reader member functions //
    // init Visual reader with given parameters for image resolution, field of view and eye selection
    bool VisualRInit(char eye, double fov_width, double fov_height, int img_width, int img_height);
    // start reading images from the iCub with YARP-RFModule
    void VisualRStart(int argc, char *argv[]);
    // stop reading images from the iCub, by terminating the RFModule
    void VisualRStop();
    // read image vector from the image buffer and remove it from the buffer
    std::vector<double> VisualRReadFromBuf();

    // Access to joint reader member functions //
    // initialize the joint reader with given parameters
    bool JointRInit(std::string name, std::string part, double sigma, int pop_size, double deg_per_neuron);
    // get the size of the populations encoding the joint angles
    std::vector<int> JointRGetNeuronsPerJoint(std::string name);
    // get the resolution in degree of the populations encoding the joint angles
    std::vector<double> JointRGetJointsDegRes(std::string name);
    // close joint reader with cleanup
    void JointRClose(std::string name);
    // read one joint and return joint angle directly as double value
    double JointRReadDouble(std::string name, int joint);
    // read one joint and return the joint angle encoded in a vector
    std::vector<double> JointRReadOne(std::string name, int joint);
    // read all joints and return the joint angles encoded in vectors
    std::vector<std::vector<double>> JointRReadAll(std::string name);

    // Access to joint writer member functions //
    // initialize the joint writer with given parameters
    bool JointWInit(std::string name, std::string part, int pop_size, double deg_per_neuron);
    // get the size of the populations encoding the joint angles
    std::vector<int> JointWGetNeuronsPerJoint(std::string name);
    // get the resolution in degree of the populations encoding the joint angles
    std::vector<double> JointWGetJointsDegRes(std::string name);
    // close joint reader with cleanup
    void JointWClose(std::string name);
    // write one joint as double value
    bool JointWWriteDouble(std::string name, double position, int joint, bool blocking);
    // write one joint with the joint angle encoded in a population
    bool JointWWriteOne(std::string name, std::vector<double> position_pop, int joint, bool blocking);
    // write all joints with joint angles encoded in populations
    bool JointWWriteAll(std::string name, std::vector<std::vector<double>> position_pops, bool blocking);

    // Access to skin reader member functions //
    // init skin reader with given parameters
    bool SkinRInit(std::string name, char arm);
    // read sensor data
    void SkinRReadTactile(std::string name);
    // return tactile data for hand skin
    std::vector<double> SkinRGetTactileHand(std::string name);
    // return tactile data for forearm skin
    std::vector<double> SkinRGetTactileForearm(std::string name);
    // return tactile data for upper arm skin
    std::vector<double> SkinRGetTactileArm(std::string name);
    // return the taxel positions given by the ini files
    std::vector<std::vector<double>> SkinRGetTaxelPos(std::string name, std::string skin_part);
    // close and clean skin reader
    void SkinRClose(std::string name);
};

extern iCub_ANN my_interface;
