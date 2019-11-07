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
    void add_jointReader(std::string name);
    // add an instance of joint writer
    void add_jointWriter(std::string name);
    // add an instance of skin reader
    void add_skinReader(std::string name);
    // add an instance of visual reader
    void add_visualReader();

    // Access to visual reader member functions //
    // init Visual reader with given parameters for image resolution, field of view and eye selection
    bool visualR_init(char eye, double fov_width, double fov_height, int img_width, int img_height);
    // start reading images from the iCub with YARP-RFModule
    void visualR_start(int argc, char *argv[]);
    // stop reading images from the iCub, by terminating the RFModule
    void visualR_stop();
    // read image vector from the image buffer and remove it from the buffer
    std::vector<double> visualR_read_fromBuf();

    // Access to joint reader member functions //
    // initialize the joint reader with given parameters
    bool jointR_init(std::string name, std::string part, double sigma, int pop_size, double deg_per_neuron);
    // get the size of the populations encoding the joint angles
    std::vector<int> jointR_get_neurons_per_joint(std::string name);
    // get the resolution in degree of the populations encoding the joint angles
    std::vector<double> jointR_get_joints_deg_res(std::string name);
    // close joint reader with cleanup
    void jointR_close(std::string name);
    // read one joint and return joint angle directly as double value
    double jointR_read_double(std::string name, int joint);
    // read one joint and return the joint angle encoded in a vector
    std::vector<double> jointR_read_one(std::string name, int joint);
    // read all joints and return the joint angles encoded in vectors
    std::vector<std::vector<double>> jointR_read_all(std::string name);

    // Access to joint writer member functions //
    // initialize the joint writer with given parameters
    bool jointW_init(std::string name, std::string part, int pop_size, double deg_per_neuron);
    // get the size of the populations encoding the joint angles
    std::vector<int> jointW_get_neurons_per_joint(std::string name);
    // get the resolution in degree of the populations encoding the joint angles
    std::vector<double> jointW_get_joints_deg_res(std::string name);
    // close joint reader with cleanup
    void jointW_close(std::string name);
    // write one joint as double value
    bool jointW_write_double(std::string name, double position, int joint, bool blocking);
    // write one joint with the joint angle encoded in a population
    bool jointW_write_one(std::string name, std::vector<double> position_pop, int joint, bool blocking);
    // write all joints with joint angles encoded in populations
    bool jointW_write_all(std::string name, std::vector<std::vector<double>> position_pops, bool blocking);

    // Access to skin reader member functions //
    // init skin reader with given parameters
    bool skinR_init(std::string name, char arm);
    // read sensor data
    void skinR_read_tactile(std::string name);
    // return tactile data for hand skin
    std::vector<double> skinR_get_tactile_hand(std::string name);
    // return tactile data for forearm skin
    std::vector<double> skinR_get_tactile_forearm(std::string name);
    // return tactile data for upper arm skin
    std::vector<double> skinR_get_tactile_arm(std::string name);
    // return the taxel positions given by the ini files
    std::vector<std::vector<double>> skinR_get_taxel_pos(std::string name, std::string skin_part);
    // close and clean skin reader
    void skinR_close(std::string name);
};

extern iCub_ANN my_interface;
