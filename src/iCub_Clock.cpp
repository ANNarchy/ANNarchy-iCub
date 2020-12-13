/*
 *  Copyright (C) 2019-2020 Torsten Follak; Helge Ülo Dinkelbach
 *
 *  Interface_iCub.cpp is part of the iCub ANNarchy interface
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

#include "iCub_Clock.hpp"

#include <chrono>
#include <thread>

// void iCubClock::delay(double seconds) { std::this_thread::sleep_for(std::chrono::duration<double>(seconds)); }
void iCubClock::delay(double seconds) {
    double time_stop = time + seconds;
    while (time < time_stop) {
        std::this_thread::sleep_for(std::chrono::duration<double>(0.1));
    }
}

bool iCubClock::isValid() const {
    if (time > 0.0)
        return true;
    else
        return false;
}

double iCubClock::now() { return time; }

void iCubClock::setTime(double seconds) { time = seconds; }
