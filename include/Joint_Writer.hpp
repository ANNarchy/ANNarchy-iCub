/*
 *  Copyright (C) 2019-2020 Torsten Fietzek
 *
 *  Joint_Writer.hpp is part of the iCub ANNarchy interface
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

#include <yarp/dev/all.h>
#include <yarp/sig/all.h>

#include <string>
#include <vector>

/**
 * \brief Write the joint angles to the iCub robots joints to move them.
 */
class JointWriter {
 public:
    // Constructor
    JointWriter() = default;
    // Destructor
    ~JointWriter();

    /*** public methods for the user ***/

    /**
     * \brief Initialize the joint writer with given parameters
     * \param[in] part A string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso}.
     * \param[in] pop_size Number of neurons per population, encoding each one joint angle; only works if parameter "deg_per_neuron" is not set
     * \param[in] deg_per_neuron (default = 0.0) degree per neuron in the populations, encoding the joints angles; if set: population size depends on joint working range
     * \param[in] speed Velocity to set for the joint motions.
     * \param[in] ini_path Path to the "interface_param.ini"-file.
     * \return True, if the initializatiion was successful. False if an error occured. Additionally, an error message is written to the error stream (cerr).\n
     *          Typical errors:
     *              - arguments not valid: e.g. part string not correct or ini file not in given path
     *              - YARP-Server not running
     */
    bool Init(std::string part, int pop_size, double deg_per_neuron = 0.0, double speed = 10.0, std::string ini_path = "../data/");

    /**
     * \brief  Close joint writer with cleanup
     */
    void Close();

    /**
     * \brief  Return number of controlled joints
     * \return Number of joints, being controlled by the writer
     */
    int GetJointCount();

    /**
     * \brief  Return the resolution in degree of the populations encoding the joint angles.
     * \return Return a vector of double, containing the resolution for every joints population coding in degree. E.g. Joint 0 is coded with 1° resolution: vector[0] = 1.0.
     */
    std::vector<double> GetJointsDegRes();

    /**
     * \brief Return the size of the populations encoding the joint angles
     * \return Return vector, containing the population size for every joint. E.g. Angle of joint 0 is encoded in a population with 10 neurons: vector[0] = 10
     */
    std::vector<int> GetNeuronsPerJoint();

    bool MotionDone();

    /**
     * \brief Return the size of the populations encoding the joint angles
     * \param[in] speed Name of the selected joint writer
     * \param[in] joint (default -1) joint number of the robot part, default -1 for all joints
     * \return True, if set was successful. False if an error occured. Additionally, an error message is written to the error stream (cerr).\n
     *          Typical errors:
     *              - arguments not valid: e.g. joint index not valid for robot part
     *              - missing initialization
     */
    bool SetJointVelocity(double speed, int joint);

    /**
     * \brief Return the size of the populations encoding the joint angles
     * \param[in] control_mode Joint control mode eg. Position, Velocity
     * \param[in] joint (default -1) joint number of the robot part, default -1 for all joints
     * \return True, if set was successful. False if an error occured. Additionally, an error message is written to the error stream (cerr).\n
     *          Typical errors:
     *              - arguments not valid: e.g. joint index not valid for robot part
     *              - missing initialization
     */
    bool SetJointControlMode(std::string control_mode, int joint);

    /**
     * \brief Write all joints with double values.
     * \param[in] position Joint angles to write to the robot joints
     * \param[in] blocking if True, function waits for end of motion
     * \param[in] string to select the motion mode: possible are 'abs' for absolute joint angle positions and 'rel' for relative joint angles
     * \return True, if successful. False if an error occured. Additionally, an error message is written to the error stream (cerr).\n
     *          Typical errors:
     *              - arguments not valid: position array size does not fit joint count; positioning mode not valid
     *              - missing initialization
     */
    bool WriteDoubleAll(std::vector<double> position, bool blocking, std::string mode);

    /**
     * \brief Write all joints with double values.
     * \param[in] position Joint angles to write to the robot joints
     * \param[in] joint_selection Joint indizes of the joints, which should be moved (head: 3, 4, 5 -> all eye movements)
     * \param[in] blocking if True, function waits for end of motion
     * \param[in] string to select the motion mode: possible are 'abs' for absolute joint angle positions and 'rel' for relative joint angles
     * \return True, if successful. False if an error occured. Additionally, an error message is written to the error stream (cerr).\n
     *          Typical errors:
     *              - arguments not valid: position array size does not fit joint count; positioning mode not valid
     *              - missing initialization
     */
    bool WriteDoubleMultiple(std::vector<double> position, std::vector<int> joint_selection, bool blocking, std::string mode);

    /**
     * \brief Write one joint with double value.
     * \param[in] position Joint angle to write to the robot joint (in degree)
     * \param[in] joint Joint number of the robot part
     * \param[in] blocking if True, function waits for end of motion
     * \param[in] string to select the motion mode: possible are 'abs' for absolute joint angle positions and 'rel' for relative joint angles
     * \return True, if successful. False if an error occured. Additionally, an error message is written to the error stream (cerr).\n
     *          Typical errors:
     *              - arguments not valid: position out of joint limits; joint out of range; positioning mode not valid
     *              - missing initialization
     */
    bool WriteDoubleOne(double position, int joint, bool blocking, std::string mode);

    /**
     * \brief Write all joints with joint angles encoded in populations
     * \param[in] position_pops Populations encoding every joint angle for writing them to the associated robot part
     * \param[in] blocking if True, function waits for end of motion
     * \param[in] string to select the motion mode: possible are 'abs' for absolute joint angle positions and 'rel' for relative joint angles
     * \return True, if successful. False if an error occured. Additionally, an error message is written to the error stream (cerr).\n
     *          Typical errors:
     *              - arguments not valid: joints out of range; positioning mode not valid; position_pops size does not fit joint count
     *              - position decoding returned NaN
     *              - missing initialization
     */
    bool WritePopAll(std::vector<std::vector<double>> position_pops, bool blocking, std::string mode);

    /**
     * \brief Write all joints with joint angles encoded in populations
     * \param[in] position_pops Populations encoding every joint angle for writing them to the associated robot part
     * \param[in] joint_selection Joint indizes of the joints, which should be moved (head: 3, 4, 5 -> all eye movements)
     * \param[in] blocking if True, function waits for end of motion
     * \param[in] string to select the motion mode: possible are 'abs' for absolute joint angle positions and 'rel' for relative joint angles
     * \return True, if successful. False if an error occured. Additionally, an error message is written to the error stream (cerr).
     *          Typical errors:
     *              - arguments not valid: joints out of range; positioning mode not valid; position_pops size does not fit joint selection
     *              - position decoding returned NaN
     *              - missing initialization
     */
    bool WritePopMultiple(std::vector<std::vector<double>> position_pops, std::vector<int> joint_selection, bool blocking,
                          std::string mode);

    /**
     * \brief Write one joint with the joint angle encoded in a population.
     * \param[in] position_pop Population encoded joint angle for writing to the robot joint
     * \param[in] joint Joint number of the robot part
     * \param[in] blocking if True, function waits for end of motion
     * \param[in] string to select the motion mode: possible are 'abs' for absolute joint angle positions and 'rel' for relative joint angles
     * \return True, if successful. False if an error occured. Additionally, an error message is written to the error stream (cerr).\n
     *          Typical errors:
     *              - arguments not valid: joint out of range; positioning mode not valid
     *              - position decoding returned NaN
     *              - missing initialization
     */
    bool WritePopOne(std::vector<double> position_pop, int joint, bool blocking, std::string mode);

 private:
    /** configuration variables **/
    bool dev_init = false;                      // variable for initialization check
    double velocity_max = 100;                  // maximum joint velocity
    std::string icub_part;                      // string describing the part of the iCub
    std::vector<int32_t> joint_control_mode;    // string describing the active control mode

    std::vector<std::string> key_map{"head", "torso", "right_arm", "left_arm", "right_leg", "left_leg"};    // valid iCub part keys

    /*** population coding data structures ***/
    std::vector<double> joint_deg_res_abs;    // degree per neuron for the population coding, value per joint
    std::vector<double> joint_deg_res_rel;    // degree per neuron for the population coding, value per joint
    int joints;                               // number of joints

    std::vector<double> joint_min;                      // minimum possible joint angles
    std::vector<double> joint_max;                      // maximum possible joint angles
    std::vector<std::vector<double>> neuron_deg_abs;    // vector of vectors representing the degree values for the neuron populations
    std::vector<std::vector<double>> neuron_deg_rel;    // vector of vectors representing the degree values for the neuron populations

    /*** yarp data structures ***/
    yarp::sig::Vector joint_angles;       // yarp vector for reading all joint angles
    yarp::dev::PolyDriver driver;         // yarp driver, used to get control interfaces
    yarp::dev::IVelocityControl *ivel;    // iCub velocity control interface
    yarp::dev::IPositionControl *ipos;    // iCub position control interface
    yarp::dev::IEncoders *ienc;           // iCub joint encoder interface
    yarp::dev::IControlMode *icont;       // iCub joint control mode interface

    /*** auxilary methods ***/
    // check if init function was called
    bool CheckInit();
    // check if iCub part key is valid
    bool CheckPartKey(std::string key);
    // decode the population coded joint angle to double value
    double Decode(std::vector<double> position_pop, int joint, std::vector<std::vector<double>> neuron_deg);
};
