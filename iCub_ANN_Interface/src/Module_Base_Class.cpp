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
#include <string>

// Destructor
Mod_BaseClass::~Mod_BaseClass() {}

bool Mod_BaseClass::CheckInit() {
    /*
        Check if the init function was called and module is registered at the main Interface
    */
    if (!dev_init) {
        std::cerr << "[" << type << "] Error: Device is not initialized!" << std::endl;
    } else if (!registered) {
        std::cerr << "[" << type << ": " << icub_part << "] Error: Device is not registered!" << std::endl;
    }
    return dev_init & registered;
}

void Mod_BaseClass::setRegister(bool value) { this->registered = value; }
bool Mod_BaseClass::getRegister() { return registered; }

std::string Mod_BaseClass::get_identifier() { return type + ": " + icub_part; }

std::vector<double> Mod_BaseClass::provideData() {
    std::cerr << "[" << type << "] Error: provideData method not implemented!" << std::endl;
    return std::vector<double>();
}

std::vector<double> Mod_BaseClass::provideData(int value, bool enc) {
    std::cerr << "[" << type << "] Error: provideData method not implemented!" << std::endl;
    return std::vector<double>();
}

std::vector<double> Mod_BaseClass::provideData(std::vector<int> value, bool enc) {
    std::cerr << "[" << type << "] Error: provideData method not implemented!" << std::endl;
    return std::vector<double>();
}

std::vector<double> Mod_BaseClass::provideData(bool enc) {
    std::cerr << "[" << type << "] Error: provideData method not implemented!" << std::endl;
    return std::vector<double>();
}

std::vector<double> Mod_BaseClass::provideData(int value) {
    std::cerr << "[" << type << "] Error: provideData method not implemented!" << std::endl;
    return std::vector<double>();
}