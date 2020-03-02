/*
 *  Copyright (C) 2019 Torsten Follak; Helge Ülo Dinkelbach
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
#include <memory>
#include <string>
#include <vector>

#include "Joint_Reader.hpp"
#include "Joint_Writer.hpp"
#include "Skin_Reader.hpp"
#include "Visual_Reader.hpp"

/**
 * \brief Interfaces the different modules (Reader/Writer) and handles the use of multiple module instances.
 */
struct iCubANN {
 private:
    std::unique_ptr<VisualReader> visual_input;             /** \brief associated visual reader (only one possible for left/right eye) */
    std::map<std::string, std::unique_ptr<JointReader>> parts_reader;  /** \brief associated joint readers (one for every robot part) */
    std::map<std::string, std::unique_ptr<JointWriter> > parts_writer;  /** \brief associated joint writers (one for every robot part) */
    std::map<std::string, std::unique_ptr<SkinReader>> tactile_reader; /** \brief associated skin reader */

 public:
    /***  Add intstances of the interface modules ***/
    /**
     * \brief Add an instance of the joint reader module. This has to be initialized with the init-method.
     * \param[in] name name for the added joint reader in the map, can be freely selected
     */
    void AddJointReader(std::string name);
    /**
     * \brief Add an instance of the joint writer module. This has to be initialized with the init-method.
     * \param[in] name name for the added joint writer in the map, can be freely selected
     */
    void AddJointWriter(std::string name);
    /**
     * \brief Add an instance of the skin reader module. This has to be initialized with the init-method.
     * \param[in] name name for the added skin reader in the map, can be freely selected
     */
    void AddSkinReader(std::string name);
    /**
     * \brief Add the instance of the visual reader module. This has to be initialized with the init-method.
     */
    void AddVisualReader();

    /***  Remove intstances of the interface modules ***/
    /**
     * \brief Remove the instance of the joint reader module.
     * \param[in] name name of the joint reader in the map
     */
    void RemoveJointReader(std::string name);
    /**
     * \brief Remove the instance of the joint writer module. 
     * \param[in] name name of the joint writer in the map
     */
    void RemoveJointWriter(std::string name);
    /**
     * \brief Remove the instance of the skin reader module. 
     * \param[in] name name of the skin reader in the map
     */
    void RemoveSkinReader(std::string name);
    /**
     * \brief Remove the instance of the visual reader module.
     */
    void RemoveVisualReader();

    // Access to joint reader member functions //
    /**
     * \brief Initialize the joint reader with given parameters
     * \param[in] name Name of the selected joint reader
     * \param[in] part A string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso}.
     * \param[in] sigma Standard deviation for the joints angles populations coding.
     * \param[in] pop_n Number of neurons per population, encoding each one joint angle; only works if parameter "deg_per_neuron" is not set
     * \param[in] deg_per_neuron (default = 0.0) degree per neuron in the populations, encoding the joints angles; if set: population size depends on joint working range
     * \return True, if the initializatiion was successful. False if an error occured. Additionally, an error message is written to the error stream (cerr).
     */
    bool JointRInit(std::string name, std::string part, double sigma, int pop_size, double deg_per_neuron);

    /**
     * \brief  Close joint reader with cleanup
     * \param[in] name Name of the selected joint reader
     */
    void JointRClose(std::string name);

    /**
     * \brief  Return number of controlled joints
     * \param[in] name Name of the selected joint reader
     * \return Number of joints, being controlled by the reader
     */
    int JointRGetJointCount(std::string name);

    /**
     * \brief  Return the resolution in degree of the populations encoding the joint angles.
     * \param[in] name Name of the selected joint reader
     * \return Return a vector of double, containing the resolution for every joints population coding in degree. E.g. Joint 0 is coded with 1° resolution: vector[0] = 1.0. 
     */
    std::vector<double> JointRGetJointsDegRes(std::string name);

    /**
     * \brief Return the size of the populations encoding the joint angles
     * \param[in] name Name of the selected joint reader
     * \return Return vector, containing the population size for every joint. E.g. Angle of joint 0 is encoded in a population with 10 neurons: vector[0] = 10
     */
    std::vector<int> JointRGetNeuronsPerJoint(std::string name);

    /**
     * \brief Read one joint and return joint angle directly in degree as double value
     * \param[in] name Name of the selected joint reader
     * \param[in] joint joint number of the robot part
     * \return Joint angle read from the robot in degree.
     */
    double JointRReadDouble(std::string name, int joint);

    /**
     * \brief Read all joints and return the joint angles encoded in populations.
     * \param[in] name Name of the selected joint reader
     * \return Population vectors encoding every joint angle from associated robot part.
     */
    std::vector<std::vector<double>> JointRReadPopAll(std::string name);

    /**
     * \brief Read one joint and return the joint angle encoded in a population.
     * \param[in] name Name of the selected joint reader
     * \param[in] joint joint number of the robot part
     * \return Population vector encoding the joint angle.
     */
    std::vector<double> JointRReadPopOne(std::string name, int joint);

    // Access to joint writer member functions //
    /**
     * \brief Initialize the joint writer with given parameters
     * \param[in] name Name of the selected joint writer
     * \param[in] part A string representing the robot part, has to match iCub part naming {left_(arm/leg), right_(arm/leg), head, torso}.
     * \param[in] pop_size Number of neurons per population, encoding each one joint angle; only works if parameter "deg_per_neuron" is not set
     * \param[in] deg_per_neuron (default = 0.0) degree per neuron in the populations, encoding the joints angles; if set: population size depends on joint working range
     * \param[in] speed Velocity to set for the joint movements.
     * \return True, if the initializatiion was successful. False if an error occured. Additionally, an error message is written to the error stream (cerr).
     */
    bool JointWInit(std::string name, std::string part, int pop_size, double deg_per_neuron, double speed);

    /**
     * \brief  Close joint writer with cleanup
     * \param[in] name Name of the selected joint writer
     */
    void JointWClose(std::string name);

    /**
     * \brief  Return number of controlled joints
     * \param[in] name Name of the selected joint writer
     * \return Number of joints, being controlled by the writer
     */
    int JointWGetJointCount(std::string name);

    /**
     * \brief  Return the resolution in degree of the populations encoding the joint angles.
     * \param[in] name Name of the selected joint writer
     * \return Return a vector of double, containing the resolution for every joints population coding in degree. E.g. Joint 0 is coded with 1° resolution: vector[0] = 1.0. 
     */
    std::vector<double> JointWGetJointsDegRes(std::string name);

    /**
     * \brief Return the size of the populations encoding the joint angles
     * \param[in] name Name of the selected joint writer
     * \return Return vector, containing the population size for every joint. E.g. Angle of joint 0 is encoded in a population with 10 neurons: vector[0] = 10
     */
    std::vector<int> JointWGetNeuronsPerJoint(std::string name);

    /**
     * \brief Return the size of the populations encoding the joint angles
     * \param[in] name Name of the selected joint writer
     * \param[in] speed Name of the selected joint writer
     * \param[in] joint (default -1) joint number of the robot part, default -1 for all joints
     * \return True, if set was successful. False if an error occured. Additionally, an error message is written to the error stream (cerr).
     */
    bool JointWSetJointVelocity(std::string name, double speed, int joint);

    /**
     * \brief Write all joints with double values.
     * \param[in] name Name of the selected joint writer
     * \param[in] position Joint angles to write to the robot joints
     * \param[in] blocking if True, function waits for end of movement
     * \param[in] string to select the motion mode: possible are 'abs' for absolute joint angle positions and 'rel' for relative joint angles
     * \return True, if successful. False if an error occured. Additionally, an error message is written to the error stream (cerr).
     */
    bool JointWWriteDoubleAll(std::string name, std::vector<double> position, bool blocking, std::string mode);

    /**
     * \brief Write all joints with double values.
     * \param[in] name Name of the selected joint writer
     * \param[in] position Joint angles to write to the robot joints
     * \param[in] joint_selection Joint indizes of the joints, which should be moved (head: [3, 4, 5] -> all eye movements)
     * \param[in] blocking if True, function waits for end of motion
     * \param[in] string to select the motion mode: possible are 'abs' for absolute joint angle positions and 'rel' for relative joint angles
     * \return True, if successful. False if an error occured. Additionally, an error message is written to the error stream (cerr).
     */
    bool JointWWriteDoubleMultiple(std::string name, std::vector<double> position, std::vector<int> joint_selection, bool blocking,
                                   std::string mode);

    /**
     * \brief Write one joint with double value.
     * \param[in] name Name of the selected joint writer
     * \param[in] position Joint angle to write to the robot joint (in degree)
     * \param[in] joint Joint number of the robot part
     * \param[in] blocking if True, function waits for end of movement
     * \param[in] string to select the motion mode: possible are 'abs' for absolute joint angle positions and 'rel' for relative joint angles
     * \return True, if successful. False if an error occured. Additionally, an error message is written to the error stream (cerr).
     */
    bool JointWWriteDoubleOne(std::string name, double position, int joint, bool blocking, std::string mode);

    /**
     * \brief Write all joints with joint angles encoded in populations
     * \param[in] name Name of the selected joint writer
     * \param[in] position_pops Populations encoding every joint angle for writing them to the associated robot part 
     * \param[in] blocking if True, function waits for end of movement
     * \param[in] string to select the motion mode: possible are 'abs' for absolute joint angle positions and 'rel' for relative joint angles
     * \return True, if successful. False if an error occured. Additionally, an error message is written to the error stream (cerr).
     */
    bool JointWWritePopAll(std::string name, std::vector<std::vector<double>> position_pops, bool blocking, std::string mode);

    /**
     * \brief Write all joints with joint angles encoded in populations
     * \param[in] name Name of the selected joint writer
     * \param[in] position_pops Populations encoding every joint angle for writing them to the associated robot part 
     * \param[in] joint_selection Joint indizes of the joints, which should be moved (head: [3, 4, 5] -> all eye movements)
     * \param[in] blocking if True, function waits for end of motion
     * \param[in] string to select the motion mode: possible are 'abs' for absolute joint angle positions and 'rel' for relative joint angles
     * \return True, if successful. False if an error occured. Additionally, an error message is written to the error stream (cerr).
     */
    bool JointWWritePopMultiple(std::string name, std::vector<std::vector<double>> position_pops, std::vector<int> joint_selection,
                                bool blocking, std::string mode);

    /**
     * \brief Write one joint with the joint angle encoded in a population.
     * \param[in] name Name of the selected joint writer
     * \param[in] position_pop Population encoded joint angle for writing to the robot joint 
     * \param[in] joint Joint number of the robot part 
     * \param[in] blocking if True, function waits for end of movement
     * \param[in] string to select the motion mode: possible are 'abs' for absolute joint angle positions and 'rel' for relative joint angles
     * \return True, if successful. False if an error occured. Additionally, an error message is written to the error stream (cerr).
     */
    bool JointWWritePopOne(std::string name, std::vector<double> position_pop, int joint, bool blocking, std::string mode);

    // Access to skin reader member functions //
    /**
     * \brief Initialize skin reader with given parameters.
     * \param[in] name Name of the selected skin reader
     * \param[in] arm character to choose the arm side (r/R for right; l/L for left)
     * \param[in] norm_data if True, data is normalized from 0..255 to 0..1.0
     * \return True, if the initializatiion was successful. False if an error occured. Additionally, an error message is written to the error stream (cerr).
     */
    bool SkinRInit(std::string name, char arm, bool norm_data);

    /**
     * \brief  Close and clean skin reader
     * \param[in] name Name of the selected skin reader
     */
    void SkinRClose(std::string name);

    /**
     * \brief Return tactile data for upper arm skin.
     * \param[in] name Name of the selected skin reader
     * \return vector, containing the tactile data of the upper arm for the last time steps
     */
    std::vector<std::vector<double>> SkinRGetTactileArm(std::string name);

    /**
     * \brief Return tactile data for forearm skin.
     * \param[in] name Name of the selected skin reader
     * \return vector, containing the tactile data of the upper arm for the last time steps
     */
    std::vector<std::vector<double>> SkinRGetTactileForearm(std::string name);

    /**
     * \brief Return tactile data for hand skin.
     * \param[in] name Name of the selected skin reader
     * \return vector, containing the tactile data of the upper arm for the last time steps
     */
    std::vector<std::vector<double>> SkinRGetTactileHand(std::string name);

    /**
     * \brief Return the taxel positions given by the ini files.
     * \param[in] name Name of the selected skin reader
     * \param[in] skin_part Skin part to load the data for ("arm", "forearm", "hand")
     * \return Vector containing taxel positions -> reference frame depending on skin part
     */
    std::vector<std::vector<double>> SkinRGetTaxelPos(std::string name, std::string skin_part);

    /**
     * \brief The sensor data is read and buffered inside. It can be accessed through #SkinRGetTactileArm, #SkinRGetTactileForearm and #SkinRGetTactileHand.
     * \param[in] name Name of the selected skin reader
     * \return True, if successful. False if an error occured. Additionally, an error message is written to the error stream (cerr).
     */
    bool SkinRReadTactile(std::string name);

    // Access to visual reader member functions //

    /**
     * \brief Init Visual reader with given parameters for image resolution, field of view and eye selection.
     * \param[in] eye character representing the selected eye (l/L; r/R) or b/B for binocular mode (right and left eye image are stored in the same buffer)
     * \param[in] fov_width output field of view width in degree [0, 60] (input fov width: 60°) 
     * \param[in] fov_height output field of view height in degree [0, 48] (input fov height: 48°) 
     * \param[in] img_width output image width in pixel (input width: 320px) 
     * \param[in] img_height output image height in pixel (input height: 240px)
     * \param[in] fast_filter flag to select the filter for image upscaling; True for a faster filter
     * \return True, if the initializatiion was successful. False if an error occured. Additionally, an error message is written to the error stream (cerr).
     */
    bool VisualRInit(char eye, double fov_width, double fov_height, int img_width, int img_height, bool fast_filter);

    /**
     * \brief Read image vector from the image buffer and remove it from the internal buffer. Call twice in binocular mode (first right eye image second left eye image)
     * \return image (1D-vector) from the image buffer
     */
    std::vector<double> VisualRReadFromBuf();

    /**
     * \brief Start reading images from the iCub with YARP-RFModule.
     * \param[in] argc main function inputs from program call; can be used to configure RFModule; not implemented yet
     * \param[in] argv main function inputs from program call; can be used to configure RFModule; not implemented yet
     * \return True, if successful. False if an error occured. Additionally, an error message is written to the error stream (cerr).
     */
    bool VisualRStart(int argc, char *argv[]);

    /**
     * \brief Stop reading images from the iCub, by terminating the RFModule.
     */
    void VisualRStop();
};

extern iCubANN my_interface;
