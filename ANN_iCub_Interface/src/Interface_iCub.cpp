/*
 *  Copyright (C) 2019-2022 Torsten Fietzek; Helge Ülo Dinkelbach
 *
 *  Interface_iCub.cpp is part of the ANNarchy iCub interface
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

#include "Interface_iCub.hpp"

ANNiCub my_interface;

// Destructor
ANNiCub::~ANNiCub() { Yarp.fini(); }
