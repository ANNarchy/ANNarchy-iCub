#pragma once

#include <string>

#include <yarp/dev/all.h>
#include <yarp/sig/all.h>


class Joint_Writer
{
  public:
    // Constructor
    Joint_Writer();
    // Destructor
    ~Joint_Writer();

    // initialize the joint writer with given parameters
    bool init(std::string part, int pop_size, double deg_per_neuron = 0.0);
    // get the size of the populations encoding the joint angles
    std::vector<int> get_neurons_per_joint();
    // get the resolution in degree of the populations encoding the joint angles
    std::vector<double> get_joints_deg_res();
    // close joint reader with cleanup
    void close();

    // write one joint as double value
    bool write_double(double position, int joint, bool blocking);
    // write one joint with the joint angle encoded in a population
    bool write_one(std::vector<double> position_pop, int joint, bool blocking);
    // write all joints with joint angles encoded in populations
    bool write_all(std::vector<std::vector<double>> position_pops, bool blocking);

  private:
    bool dev_init = false; // variable for initialization check
    std::string iCub_part;             // string describing the part of the iCub
    
    int joint_res;                     // neuron count for the population coding, if degree per neuron is set by argument
    std::vector<double> joint_deg_res; // degree per neuron for the population coding, value per joint; if neuron count is set by argument
    int joints;                        // number of joints

    std::vector<double> joint_min;               // minimum possible joint angles
    std::vector<double> joint_max;               // maximum possible joint angles
    std::vector<std::vector<double>> neuron_deg; // vector of vectors representing the degree values for the neuron populations

    yarp::sig::Vector joint_angles;    // yarp vector for reading all joint angles
    yarp::dev::PolyDriver driver;      // yarp driver needed for reading joint encoders
    yarp::dev::IPositionControl *iPos; // iCub position control interface

    // auxilary functions //
    // check if init function was called
    bool check_init();
    // decode the population coded joint angle to double value
    double decode(std::vector<double> position_pop, int joint);
};
