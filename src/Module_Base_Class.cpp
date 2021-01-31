/*
 *  Copyright (C) 2019-2021 Torsten Fietzek; Helge Ülo Dinkelbach
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

#include "Module_Base_Class.hpp"

#include <iostream>

// Destructor
Mod_BaseClass::~Mod_BaseClass() {}

bool Mod_BaseClass::CheckInit() {
    /*
        Check if the init function was called and module is registered at the main Interface
    */
    if (!dev_init) {
        std::cerr << "[" << type << "]"
                  << " Error: Device is not initialized!" << std::endl;
    }
    if (!registered) {
        std::cerr << "[" << type << " " << icub_part << "]"
                  << " Error: Device is not registered!" << std::endl;
    }
    return dev_init & registered;
}

void Mod_BaseClass::setRegister(bool value) { this->registered = value; }
bool Mod_BaseClass::getRegister() { return registered; }
