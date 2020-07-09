/*
 *  Copyright (C) 2019-2020 Torsten Follak; Helge Ülo Dinkelbach
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

#include <yarp/os/all.h>

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
class iCubANN {
 private:
    yarp::os::Network Yarp;

 public:
    // Constructor
    iCubANN() = default;
    // Destructor
    ~iCubANN();

    /** \brief associated visual reader (only one possible for left/right eye) */
    std::shared_ptr<VisualReader> visual_input;
    /** \brief associated joint readers (one for every robot part) */
    std::map<std::string, std::shared_ptr<JointReader>> parts_reader;
    /** \brief associated joint writers (one for every robot part) */
    std::map<std::string, std::shared_ptr<JointWriter>> parts_writer;
    /** \brief associated skin reader */
    std::map<std::string, std::shared_ptr<SkinReader>> tactile_reader;

    /***  Add intstances of the interface modules ***/
    /**
     * \brief Add an instance of the joint reader module. This has to be initialized with the init-method.
     * \param[in] name name for the added joint reader in the map, can be freely selected
     * \return True, if successful. False if an error occured. Additionally, an error message is written to the error stream (cerr).\n
     *          Typical errors:
     *              - Name already used
     */
    bool AddJointReader(std::string name);
    /**
     * \brief Add an instance of the joint writer module. This has to be initialized with the init-method.
     * \param[in] name name for the added joint writer in the map, can be freely selected
     * \return True, if successful. False if an error occured. Additionally, an error message is written to the error stream (cerr).\n
     *          Typical errors:
     *              - Name already used
     */
    bool AddJointWriter(std::string name);
    /**
     * \brief Add an instance of the skin reader module. This has to be initialized with the init-method.
     * \param[in] name name for the added skin reader in the map, can be freely selected
     * \return True, if successful. False if an error occured. Additionally, an error message is written to the error stream (cerr).\n
     *          Typical errors:
     *              - Name already used
     */
    bool AddSkinReader(std::string name);
    /**
     * \brief Add the instance of the visual reader module. This has to be initialized with the init-method.
     * \return True, if successful. False if an error occured. Additionally, an error message is written to the error stream (cerr).\n
     *          Typical errors:
     *              - Name already used
     */
    bool AddVisualReader();

    /***  Remove intstances of the interface modules ***/
    /**
     * \brief Remove the instance of the joint reader module.
     * \param[in] name name of the joint reader in the map
     * \return True, if successful. False if an error occured. Additionally, an error message is written to the error stream (cerr).
     */
    bool RemoveJointReader(std::string name);
    /**
     * \brief Remove the instance of the joint writer module.
     * \param[in] name name of the joint writer in the map
     * \return True, if successful. False if an error occured. Additionally, an error message is written to the error stream (cerr).
     */
    bool RemoveJointWriter(std::string name);
    /**
     * \brief Remove the instance of the skin reader module.
     * \param[in] name name of the skin reader in the map
     * \return True, if successful. False if an error occured. Additionally, an error message is written to the error stream (cerr).
     */
    bool RemoveSkinReader(std::string name);
    /**
     * \brief Remove the instance of the visual reader module.
     * \return True, if successful. False if an error occured. Additionally, an error message is written to the error stream (cerr).
     */
    bool RemoveVisualReader();
};

extern iCubANN my_interface;
