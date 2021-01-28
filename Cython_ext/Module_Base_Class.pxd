# distutils: language = c++
# cython: language_level = 3

"""
   Copyright (C) 2019-2021 Torsten Fietzek; Helge Ülo Dinkelbach

   Mod_BaseClass.pxd is part of the iCub ANNarchy interface

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   The iCub ANNarchy interface is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this headers. If not, see [http://www.gnu.org/licenses/].
 """

from libcpp.string cimport string
from libcpp cimport bool as bool_t

cdef extern from "Module_Base_Class.hpp":

    cdef cppclass Mod_BaseClass:
        Mod_BaseClass() except +    
        
        # Set values for type and part
        void setType(string, string)
        string getType()
        string getPart()

        # check if init function was called
        bool_t CheckInit()
        # Set value for dev_init
        void setDevInit(bool_t)
        # Get value for dev_init
        bool_t getDevInit()
        # Set value for registered
        void setRegister(bool_t)

cdef extern from "Module_Base_Class.hpp":
    pass