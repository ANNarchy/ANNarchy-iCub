# distutils: language = c++
# cython: language_level = 3
# cython: profile=True
# cython: binding=True

"""
   Copyright (C) 2019-2022 Torsten Fietzek; Helge Ülo Dinkelbach

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


from .Module_Base_Class cimport PyModuleBase

cdef class PyModuleBase:

    # init method
    def __cinit__(self):
        pass
        # print("Initialize Module_base.")

    # close method
    # def __dealloc__(self):
        # print("Close Module_base.")
