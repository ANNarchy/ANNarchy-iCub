"""
Created on 

@author: Torsten Fietzek, Helge Uelo Dinkelbach

setup file for the package compilation process
"""

import os
import subprocess
import sys

from make_config import *

# setuptools
try:
    from setuptools import Extension, find_packages, setup
    print('Checking for setuptools... OK')
except:
    print('Checking for setuptools... NO')
    print('Error : Python package "setuptools" is required.')
    print('You can install it from pip or: http://pypi.python.org/pypi/setuptools')
    exit(0)
from Cython.Build import cythonize

# numpy
try:
    import numpy
    print('Checking for numpy... OK')
except:
    print('Checking for numpy... NO')
    print('Error : Python package "numpy" is required.')
    print('You can install it from pip or: http://www.numpy.org')
    exit(0)

# test ANNarchy
try:
    import ANNarchy
    print('Checking for ANNarchy... OK')
except:
    print('Checking for ANNarchy... NO')
    print('Error : Python package "ANNarchy" is required.')
    exit(0)

root_path = os.path.abspath("./")

grpc_include_dir = []
grpc_libs = []
grpc_lib_dir = []
grpc_package_data = []

if use_grpc:
    # protobuf, grpc
    grpc_avaiable = True

    if os.system("protoc --version") == 0:
        print('Checking for protoc ... OK')
    else:
        print('Checking for protoc ... OK')
        print("Protobuf C-compiler (protoc) not found")
        grpc_avaiable = False

    # try:
    #     import grpc     # includes grpc
    #     print('Checking for grpc ... OK')
    # except:
    #     print('Checking for grpc (required for mpi) ... NO')
    #     print("You can install grpcio from pip ")
    #     grpc_avaiable = False

    # build the interface gRPC definitions
    if grpc_avaiable:
        grpc_cpp_plugin = subprocess.check_output(["which", "grpc_cpp_plugin"]).strip().decode(sys.stdout.encoding)
        # grpc_python_plugin = subprocess.check_output(["which", "grpc_python_plugin"]).strip().decode(sys.stdout.encoding)
        os.system("protoc -I=. --cpp_out=. --grpc_out=. --plugin=protoc-gen-grpc="+grpc_cpp_plugin+" iCub_ANN_Interface/grpc/icub.proto")
        # os.system("protoc -I=. --python_out=. --grpc_out=. --plugin=protoc-gen-grpc="+grpc_python_plugin+" iCub_ANN_Interface/grpc/icub.proto")
    else:
        print("grpcio and/or protobuf c-compiler is missing ... abort")
        exit()

    # build grpc proto related sourcefile to library
    print("Build grpc->proto files in seperated library")
    os.system("cd iCub_ANN_Interface/grpc/ && make EXTFLAGS=\"-I"+os.path.abspath("./")+"\"")
 
    grpc_include_dir.append("iCub_ANN_Interface/grpc")
    grpc_libs += ["protobuf", "grpc++", "grpc++_reflection", "iCub_ANN_grpc"]
    grpc_lib_dir += [root_path+"/iCub_ANN_Interface/grpc"]
    grpc_package_data = ['ANNarchy_iCub_Populations/__init__.py', 'grpc/*.so']

# Python Version info
py_major = sys.version_info[0]
py_minor = sys.version_info[1]
py_version = str(py_major) + "." + str(py_minor)


# find YARP include path
if yarp_prefix == "default":
    yarp_prefix = set_yarp_prefix()
else:
    if not os.path.isdir(yarp_prefix + "/include/yarp"):
        sys.exit("Did not find YARP in given path! Please correct yarp_prefix in make_config.py!")


# find OpenCV include path
if cv_include == "default":
    cv_include = set_opencv_prefix()
else:
    if not os.path.isdir(cv_include + "/opencv2"):
        sys.exit("Did not find OpenCV in given path! Please correct cv_include in make_config.py!")


# Setup lists with lib/include directories and names
include_dir = ["/usr/include", "iCub_ANN_Interface/include", "./", yarp_prefix + "/include", cv_include, numpy.get_include()] + grpc_include_dir

libs = ["opencv_core", "opencv_imgproc",
        "YARP_dev", "YARP_init", "YARP_math", "YARP_name", "YARP_os", "YARP_run", "YARP_sig"] + grpc_libs

lib_dirs=["/usr/lib", "/usr/local/lib", yarp_prefix + "/lib"] + grpc_lib_dir


# Prefixes for Cython and C++ based code
prefix_cy = "iCub_ANN_Interface/"
prefix_cpp = "iCub_ANN_Interface/src/"

# Sourcefiles lists
sources = ["iCub_ANN_Interface/include/INI_Reader/INIReader.cpp", "iCub_ANN_Interface/include/INI_Reader/ini.cpp", prefix_cpp + "Module_Base_Class.cpp"]
sources1 = [prefix_cpp + "Joint_Reader.cpp", prefix_cpp + "Joint_Writer.cpp", prefix_cpp + "Skin_Reader.cpp", prefix_cpp + "Visual_Reader.cpp"]

package_data = ['__init__.py',
                'iCub/*.pxd',
                'iCub/*.pyx',
                'iCub/__init__.py',
                'Sync/*.pyx',
                'Sync/__init__.py'
                ] + grpc_package_data

# set compile arguments
extra_compile_args = ["-g", "-fPIC", "-std=c++17", "--shared", "-O2", "-march=native", "-Wall"] # , "-fpermissive" nicht als default; macht den Compiler relaxter; "-march=native" ermöglicht direkter Plattformabhängige Optimierung
if verbose:
    extra_compile_args.append("--verbose")
if pedantic:
    extra_compile_args.append("-pedantic")
if use_grpc:
    extra_compile_args += ["-Wl,-rpath,"+root_path+"/iCub_ANN_Interface/grpc/", "-D_USE_GRPC"]
if double_precision:
    extra_compile_args.append("-D_DOUBLE_PRECISION")
else:
    extra_compile_args.append("-D_SINGLE_PRECISION")

# define extensions for the cython-based modules
extensions = [
    Extension("iCub_ANN_Interface.iCub.Joint_Reader", [prefix_cy + "iCub/Joint_Reader.pyx", prefix_cpp + "Joint_Reader.cpp"] + sources,
        include_dirs=include_dir,
        libraries=libs,
        library_dirs=lib_dirs,
        language="c++",
        extra_compile_args=extra_compile_args,
        extra_link_args=["-L"+root_path+"/iCub_ANN_Interface/grpc", "-Wl,-rpath,"+root_path+"/iCub_ANN_Interface/grpc/"]
        ),

    Extension("iCub_ANN_Interface.iCub.Joint_Writer", [prefix_cy + "iCub/Joint_Writer.pyx", prefix_cpp + "Joint_Writer.cpp"] + sources,
        include_dirs=include_dir,
        libraries=libs,
        library_dirs=lib_dirs,
        language="c++",
        extra_compile_args=extra_compile_args,
        extra_link_args=["-L"+root_path+"/iCub_ANN_Interface/grpc", "-Wl,-rpath,"+root_path+"/iCub_ANN_Interface/grpc/"]
        ),

    Extension("iCub_ANN_Interface.iCub.Skin_Reader", [prefix_cy + "iCub/Skin_Reader.pyx", prefix_cpp + "Skin_Reader.cpp"] + sources,
        include_dirs=include_dir,
        libraries=libs,
        library_dirs=lib_dirs,
        language="c++",
        extra_compile_args=extra_compile_args,
        extra_link_args=["-L"+root_path+"/iCub_ANN_Interface/grpc", "-Wl,-rpath,"+root_path+"/iCub_ANN_Interface/grpc/"]
        ),

    Extension("iCub_ANN_Interface.iCub.Visual_Reader", [prefix_cy + "iCub/Visual_Reader.pyx", prefix_cpp + "Visual_Reader.cpp"] + sources,
        include_dirs=include_dir,
        libraries=libs,
        library_dirs=lib_dirs,
        language="c++",
        extra_compile_args=extra_compile_args,
        extra_link_args=["-L"+root_path+"/iCub_ANN_Interface/grpc", "-Wl,-rpath,"+root_path+"/iCub_ANN_Interface/grpc/"]
        ),

    Extension("iCub_ANN_Interface.iCub.iCub_Interface", [prefix_cy + "iCub/iCub_Interface.pyx", prefix_cpp + "Interface_iCub.cpp"] + sources + sources1,
        include_dirs=include_dir,
        libraries=libs,
        library_dirs=lib_dirs,
        language="c++",
        extra_compile_args=extra_compile_args,
        extra_link_args=["-L"+root_path+"/iCub_ANN_Interface/grpc", "-Wl,-rpath,"+root_path+"/iCub_ANN_Interface/grpc/"]
        ),

    Extension("iCub_ANN_Interface.Sync.Master_Clock", [prefix_cy + "Sync/Master_Clock.pyx"],
        include_dirs=include_dir,
        libraries=libs,
        library_dirs=lib_dirs,
        language="c++",
        extra_compile_args=extra_compile_args
        )
]

# python dependencies
dependencies = [
    'numpy',
    'scipy',
    'matplotlib',
    'cython',
    'sympy'
]

version="1.0"
filename = './iCub_ANN_Interface/version.py'
with open(filename, 'w') as file_object:
    file_object.write("# automatically generated in setup.py\n")
    file_object.write("__version__ = \"" + version + "\"")

filename = './iCub_ANN_Interface/use_grpc.py'
with open(filename, 'w') as file_object:
    file_object.write("# automatically generated in setup.py\n")
    file_object.write("__use_grpc__ = " + str(use_grpc))

setup(
    name="iCub_ANN_Interface",
    packages=find_packages(),
    ext_modules=cythonize(extensions, language_level=int(sys.version_info[0])),
    description="Interface for iCub robot and ANNarchy neuro-simulator",
    long_description="""This program is an interface between the Neurosimulator ANNarchy and the iCub robot (tested with the iCub simulator and partly with gazebo). It is written in C++ with a Cython wrapping to Python.""",
    version=version,
    author="Torsten Fietzek, Helge Uelo Dinkelbach",
    author_email="torsten.fietzek@informatik.tu-chemnitz.de",
    license="GPLv2+",
    platforms='GNU/Linux; MacOSX',
    zip_safe=False,
    package_data={'iCub_ANN_Interface': package_data},
    install_requires=dependencies
)

