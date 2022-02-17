/*
 *  Copyright (C) 2019-2022 Torsten Fietzek; Helge Ülo Dinkelbach
 *
 *  Interface_iCub.hpp is part of the ANNarchy iCub interface
 *
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  The ANNarchy iCub interface is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this headers. If not, see <http://www.gnu.org/licenses/>.
 */

#pragma once

#include <yarp/os/all.h>


/**
 * \brief Interfaces the different modules (Reader/Writer) and handles the use of multiple module instances.
 */
class ANNiCub {
 private:
    yarp::os::Network Yarp;

 public:
    // Constructor
    ANNiCub() = default;
    // Destructor
    ~ANNiCub();


};

extern ANNiCub my_interface;
