#pragma once

#include <opencv2/opencv.hpp>
#include <string>

#include <iCub/iKin/iKinFwd.h> // iCub forward Kinematics
#include <yarp/os/all.h>
#include <yarp/sig/all.h>

struct taxel_data
{
    std::vector<int> idx;
    std::vector<std::vector<double>> arr;
};

class Skin_Reader
{
  public:
    // Constructor
    Skin_Reader();
    // Destructor
    ~Skin_Reader();
    // init skin reader with given parameters
    bool init(char arm);
    // read sensor data
    void read_tactile();

    // return tactile data for hand skin
    std::vector<double> get_tactile_hand();
    // return tactile data for forearm skin
    std::vector<double> get_tactile_forearm();
    // return tactile data for upper arm skin
    std::vector<double> get_tactile_arm();
    // return the taxel positions given by the ini files
    std::vector<std::vector<double>> get_taxel_pos(std::string skin_part);

    // close and clean skin reader
    void close();

  private:
    yarp::os::BufferedPort<yarp::sig::Vector> PortHand;    // port for the hand
    yarp::os::BufferedPort<yarp::sig::Vector> PortForearm; // port for the forearm
    yarp::os::BufferedPort<yarp::sig::Vector> PortArm;     // port for the arm

    yarp::sig::Vector *tactile_hand;    // YARP Vector for hand sensor data
    yarp::sig::Vector *tactile_forearm; // YARP Vector for forearm sensor data
    yarp::sig::Vector *tactile_arm;     // YARP Vector for upper arm sensor data

    std::vector<double> hand_data;    // Vector for sorted and cleaned hand sensor data
    std::vector<double> forearm_data; // Vector for sorted and cleaned forearm sensor data
    std::vector<double> arm_data;     // Vector for sorted and cleaned upper arm sensor data

    std::string side;      // containing information about selected arm (right/left)
    bool dev_init = false; // variable for initialization check

    std::map<std::string, taxel_data> taxel_pos_data;          // contains taxel position data for different skin parts
    std::map<std::string, iCub::iKin::iKinChain *> kin_chains; // contains taxel position data for different skin parts

    bool read_taxel_pos(std::string filename_idx, std::string filename_pos, std::string part);

    // auxilary functions //
    // check if init function was called
    bool check_init();
};
