
#include <string>

#include "Interface_iCub.hpp"

#include "Joint_Reader.hpp"
#include "Joint_Writer.hpp"
#include "Skin_Reader.hpp"
#include "Visual_Reader.hpp"

iCub_ANN my_interface;

// add an instance of joint reader
void iCub_ANN::add_jointReader(std::string name)
/*
    params: std::string name        -- name for the added joint reader in the map, can be freely selected
*/
{
    if (parts_reader.count(name) == 0)
        {
            parts_reader[name] = new Joint_Reader();
        }
    else
        {
            std::cerr << "[Joint Reader] Name \"" + name + "\" is already used.\n";
        }
}

// add an instance of joint writer
void iCub_ANN::add_jointWriter(std::string name)
/*
    params: std::string name        -- name for the added joint writer in the map, can be freely selected
*/
{
    if (parts_writer.count(name) == 0)
        {
            parts_writer[name] = new Joint_Writer();
        }
    else
        {
            std::cerr << "[Joint Writer] Name \"" + name + "\" is already used.\n";
        }
}

// add an instance of skin reader
void iCub_ANN::add_skinReader(std::string name)
/*
    params: std::string name        -- name for the added skin reader in the map, can be freely selected
*/
{
    if (tactile_reader.count(name) == 0)
        {
            tactile_reader[name] = new Skin_Reader();
        }
    else
        {
            std::cerr << "[Skin Reader] Name \"" + name + "\" is already used.\n";
        }
}

// add an instance of visual reader
void iCub_ANN::add_visualReader()
/*
    params: std::string name        -- name for the added visual reader in the map, can be freely selected
*/
{
    if (visual_input == NULL)
        {
            visual_input = new Visual_Reader();
        }
    else
        {
            std::cerr << "Visual Reader is already defined.\n";
        }
}

// Access to visual reader member functions //
// init Visual reader with given parameters for image resolution, field of view and eye selection
bool iCub_ANN::visualR_init(char eye, double fov_width, double fov_height, int img_width, int img_height)
/*
    params: char eye            -- characteer representing the selected eye (l/L; r/R)
            double fov_width    -- output field of view width in degree [0, 60] (input fov width: 60°)
            double fov_height   -- output field of view height in degree [0, 48] (input fov height: 48°)
            int img_width       -- output image width in pixel (input width: 320px)
            int img_height      -- output image height in pixel (input height: 240px)

    return: bool                -- return True, if successful
*/
{
    return visual_input->init(eye, fov_width, fov_height, img_width, img_height);
}
// start reading images from the iCub with YARP-RFModule
void iCub_ANN::visualR_start(int argc, char *argv[])
/*
    params: int argc, char *argv[]  -- main function inputs from program call; can be used to configure RFModule; not implemented yet
*/
{
    visual_input->start(argc, argv);
}
// stop reading images from the iCub, by terminating the RFModule
void iCub_ANN::visualR_stop() { visual_input->stop(); }
// read image vector from the image buffer and remove it from the buffer
std::vector<double> iCub_ANN::visualR_read_fromBuf()
/*
    return: std::vector<double>     -- image (1D-vector) from the image buffer
*/
{
    return visual_input->read_fromBuf();
}

// Access to joint reader member functions //
// initialize the joint reader with given parameters
bool iCub_ANN::jointR_init(std::string name, std::string part, double sigma, int pop_size, double deg_per_neuron)
/*
    params: std::string name        -- name of the selected joint reader
            std::string part        -- string representing the robot part, has to match iCub part naming
                                        {left_(arm/leg), right_(arm/leg), head, torso}
            sigma                   -- sigma for the joints angles populations coding
            int pop_size            -- number of neurons per population, encoding each one joint angle;
                                        only works if parameter "deg_per_neuron" is not set
            double deg_per_neuron   -- degree per neuron in the populations, encoding the joints angles;
                                        if set: population size depends on joint working range

    return: bool                    -- return True, if successful
*/
{
    return parts_reader[name]->init(part, sigma, pop_size, deg_per_neuron);
}
// get the size of the populations encoding the joint angles
std::vector<int> iCub_ANN::jointR_get_neurons_per_joint(std::string name)
/*
    params: std::string name        -- name of the selected joint reader

    return: std::vector<int>        -- return vector, containing the population size for every joint
*/
{
    return parts_reader[name]->get_neurons_per_joint();
}
// get the resolution in degree of the populations encoding the joint angles
std::vector<double> iCub_ANN::jointR_get_joints_deg_res(std::string name)
/*
    params: std::string name        -- name of the selected joint reader

    return: std::vector<double>     -- return vector, containing the resolution for every joints population codimg in degree
*/
{
    return parts_reader[name]->get_joints_deg_res();
}
// read one joint and return joint angle directly as double value
double iCub_ANN::jointR_read_double(std::string name, int joint)
/*
    params: std::string name    -- name of the selected joint reader
            int joint           -- joint number of the robot part

    return: double              -- joint angle read from the robot
*/
{
    return parts_reader[name]->read_double(joint);
}
// read one joint and return the joint angle encoded in a vector
std::vector<double> iCub_ANN::jointR_read_one(std::string name, int joint)
/*
    params: std::string name        -- name of the selected joint reader
            int joint               -- joint number of the robot part

    return: std::vector<double>     -- population vector encoding the joint angle
*/
{
    return parts_reader[name]->read_one(joint);
}
// read all joints and return the joint angles encoded in vectors
std::vector<std::vector<double>> iCub_ANN::jointR_read_all(std::string name)
/*
    params: std::string name                    -- name of the selected joint reader

    return: std::vector<std::vector<double>>    -- population vectors encoding every joint angle from associated robot part
*/
{
    return parts_reader[name]->read_all();
}
// close joint reader with cleanup
void iCub_ANN::jointR_close(std::string name)
/*
    params: std::string name        -- name of the selected joint reader
*/
{
    parts_reader[name]->close();
}

// Access to joint writer member functions //
// initialize the joint writer with given parameters
bool iCub_ANN::jointW_init(std::string name, std::string part, int pop_size, double deg_per_neuron)
/*
    params: std::string name        -- name of the selected joint writer
            std::string part        -- string representing the robot part, has to match iCub part naming
                                        {left_(arm/leg), right_(arm/leg), head, torso}
            int pop_size            -- number of neurons per population, encoding each one joint angle;
                                        only works if parameter "deg_per_neuron" is not set
            double deg_per_neuron   -- degree per neuron in the populations, encoding the joints angles;
                                        if set: population size depends on joint working range

    return: bool                    -- return True, if successful
*/
{
    return parts_writer[name]->init(part, pop_size, deg_per_neuron);
}
// get the size of the populations encoding the joint angles
std::vector<int> iCub_ANN::jointW_get_neurons_per_joint(std::string name)
/*
    params: std::string name        -- name of the selected joint writer

    return: std::vector<int>        -- return vector, containing the population size for every joint
*/
{
    return parts_writer[name]->get_neurons_per_joint();
}
// get the resolution in degree of the populations encoding the joint angles
std::vector<double> iCub_ANN::jointW_get_joints_deg_res(std::string name)
/*
    params: std::string name        -- name of the selected joint writer

    return: std::vector<double>     -- return vector, containing the resolution for every joints population codimg in degree
*/
{
    return parts_writer[name]->get_joints_deg_res();
}
// write one joint as double value
bool iCub_ANN::jointW_write_double(std::string name, double position, int joint, bool blocking)
/*
    params: std::string name    -- name of the selected joint writer
            double position     -- joint angle to write to the robot joint
            int joint           -- joint number of the robot part
            bool blocking       -- if True, function waits for end of movement

    return: bool                -- return True, if successful
*/
{
    return parts_writer[name]->write_double(position, joint, blocking);
}
// write one joint with the joint angle encoded in a population
bool iCub_ANN::jointW_write_one(std::string name, std::vector<double> position_pop, int joint, bool blocking)
/*
    params: std::string name        -- name of the selected joint writer
            std::vector<double>     -- population encoded joint angle for writing to the robot joint
            int joint               -- joint number of the robot part
            bool blocking           -- if True, function waits for end of movement

    return: bool                    -- return True, if successful
*/
{
    return parts_writer[name]->write_one(position_pop, joint, blocking);
}
// write all joints with joint angles encoded in populations
bool iCub_ANN::jointW_write_all(std::string name, std::vector<std::vector<double>> position_pops, bool blocking)
/*
    params: std::string name                    -- name of the selected joint writer
            std::vector<std::vector<double>>    -- populations encoding every joint angle for writing them to the associated robot part
            bool blocking                       -- if True, function waits for end of movement

    return: bool                                -- return True, if successful
*/
{
    return parts_writer[name]->write_all(position_pops, blocking);
}
// close joint reader with cleanup
void iCub_ANN::jointW_close(std::string name)
/*
    params: std::string name        -- name of the selected joint writer
*/
{
    return parts_writer[name]->close();
}

// Access to skin reader member functions //
// init skin reader with given parameters
bool iCub_ANN::skinR_init(std::string name, char arm)
/*
    params: std::string name        -- name of the selected skin reader
            char arm                -- string representing the robot part, has to match iCub part naming

    return: bool                    -- return True, if successful
*/
{
    tactile_reader[name]->init(arm);
}
// read sensor data
void iCub_ANN::skinR_read_tactile(std::string name)
/*
    params: std::string name        -- name of the selected skin reader
*/
{
    tactile_reader[name]->read_tactile();
}
// return tactile data for hand skin
std::vector<double> iCub_ANN::skinR_get_tactile_hand(std::string name)
/*
    params: std::string name        -- name of the selected skin reader
*/
{
    return tactile_reader[name]->get_tactile_hand();
}
// return tactile data for forearm skin
std::vector<double> iCub_ANN::skinR_get_tactile_forearm(std::string name)
/*
    params: std::string name        -- name of the selected skin reader
*/
{
    return tactile_reader[name]->get_tactile_forearm();
}
// return tactile data for upper arm skin
std::vector<double> iCub_ANN::skinR_get_tactile_arm(std::string name)
/*
    params: std::string name        -- name of the selected skin reader
*/
{
    return tactile_reader[name]->get_tactile_arm();
}
// return the taxel positions given by the ini files
std::vector<std::vector<double>> iCub_ANN::skinR_get_taxel_pos(std::string name, std::string skin_part)
/*
    params: std::string name                    -- name of the selected skin reader
            std::string skin_part               -- skin part to load the data for ("arm", "forearm", "hand")

    return: std::vector<std::vector<double>>    -- Vector containing taxel positions -> reference frame depending on skin part
*/
{
    return tactile_reader[name]->get_taxel_pos(skin_part);
}
// close and clean skin reader
void iCub_ANN::skinR_close(std::string name)
/*
    params: std::string name        -- name of the selected skin reader
*/
{
    tactile_reader[name]->close();
}