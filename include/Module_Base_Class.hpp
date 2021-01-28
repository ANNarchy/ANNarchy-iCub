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

#pragma once

#include <string>

/**
 * \brief Base class for the sensor/actor reader/writer modules
 */
class Mod_BaseClass {
 private:
    bool registered = false;
    bool dev_init = false;    // variable for initialization check
    std::string type;
    std::string part;

 protected:
    // check if init function was called
    bool CheckInit();
    // Set value for dev_init
    void setDevInit(bool value);
    // Get value for dev_init
    bool getDevInit();
    // Set value for registered
    void setRegister(bool value);

 public:
    // Constructor
    Mod_BaseClass() = default;
    // Destructor
    ~Mod_BaseClass();

    // template function for close method
    virtual void Close();

    // Set values for type and part
    void setType(std::string value_type, std::string value_part);
    std::string getType();
    std::string getPart();
};
