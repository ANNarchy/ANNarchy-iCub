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

#include <iostream>
#include <map>
#include <string>
#include <vector>

/**
 * \brief Base class for the sensor/actor reader/writer modules
 */
class Mod_BaseClass {
 private:
    bool registered = false;

 protected:
    // check if init function was called
    bool CheckInit();
    // Set value for dev_init
    bool dev_init = false;         // variable for initialization check
    bool dev_init_grpc = false;    // variable for gRPC initialization check
    std::string type;              // Module type e.g. Joint Reader
    std::string icub_part;         //
    std::map<std::string, std::string> init_param;

 public:
    // Constructor
    Mod_BaseClass() = default;
    // Destructor
    ~Mod_BaseClass();

    // Set value for registered
    void setRegister(bool value);
    bool getRegister();

    std::string get_identifier();
    std::map<std::string, std::string> getParameter();

    // template function for close method
    virtual void Close() = 0;

    virtual std::vector<double> provideData();
    virtual std::vector<double> provideData(int value, bool enc);
    virtual std::vector<double> provideData(std::vector<int> value, bool enc);
    virtual std::vector<double> provideData(bool enc);
    virtual std::vector<double> provideData(int value);
};
