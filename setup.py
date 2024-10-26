"""
    Copyright (C) 2019-2024 Torsten Fietzek; Helge Ülo Dinkelbach

    setup.py is part of the ANNarchy iCub interface

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    The ANNarchy iCub interface is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this headers. If not, see [http://www.gnu.org/licenses/].
"""

import os
import subprocess
import sys
from pathlib import Path
import tomlkit

# setuptools
try:
    from setuptools import Extension, find_packages, setup
    print('Checking for setuptools... OK')
except Exception:
    print('Checking for setuptools... NO')
    print('Error : Python package "setuptools" is required.')
    print('You can install it from pip or: http://pypi.python.org/pypi/setuptools')
    exit(0)

# cython
try:
    from Cython.Build import cythonize
    print('Checking for Cython... OK')
except Exception:
    print('Checking for Cython... NO')
    print('Error : Python package "Cython" is required.')
    print('You can install it from pip')
    exit(0)

# numpy
try:
    import numpy
    print('Checking for numpy... OK')
except Exception:
    print('Checking for numpy... NO')
    print('Error : Python package "numpy" is required.')
    print('You can install it from pip or: http://www.numpy.org')
    exit(0)


# Helper functions to determine the OpenCV and YARP include paths
def set_yarp_prefix():
    # Yarp install direction
    yarp_prefix = None
    if subprocess.check_output(["which", "yarp"]):
        yarp_bin = subprocess.check_output(["which", "yarp"]).strip().decode(sys.stdout.encoding)
        yarp_prefix = str(Path(yarp_bin).resolve().parents[1]) + "/"
    elif "ROBOTOLOGY_SUPERBUILD_INSTALL_PREFIX" in os.environ:
        yarp_prefix = os.environ["ROBOTOLOGY_SUPERBUILD_INSTALL_PREFIX"]
    elif os.path.isdir("/usr/local/packages/yarp"):
        yarp_prefix = "/usr/local/packages/yarp"
    elif "YARP_DATA_DIRS" in os.environ:
        yarp_data = os.environ['YARP_DATA_DIRS'].split(':')[0].split('/')
        if yarp_data[-1] == "iCub" or yarp_data[-1] == "yarp":
            yarp_prefix = "/".join(yarp_data[:-3])
        else:
            yarp_prefix = "/".join(yarp_data[:-2])
    elif os.path.isdir("/usr/local/include/yarp"):
        yarp_prefix = "/usr/local"
    elif os.path.isdir("/usr/include/yarp"):
        yarp_prefix = "/usr"
    else:
        if yarp_prefix == None:
            print("Did not find YARP include path! Please set yarp_prefix manually!")
            print("Please type the YARP prefix in the form /path/to/include/and/lib:")
            yarp_prefix = input()
            if not os.path.isdir(yarp_prefix + "/include/yarp"):
                sys.exit("Did not find YARP in given path! Please set yarp_prefix manually in build_config.toml or retry!")
    return yarp_prefix


def set_opencv_prefix():
    # OpenCV direction
    cv_include = None
    try:
        import cv2
        cvpath = cv2.__file__
        path_list = cvpath.split("/")
        if not ("usr" in path_list or ".local" in path_list):
            cv_include = "/".join(path_list[:path_list.index("lib")] + ["include",])
            if os.path.isdir(cv_include + "/opencv4"):
                cv_include += "/opencv4"
    except:
        pass
    if cv_include == None:
        if os.path.isdir("/usr/include/opencv2"):
            cv_include = "/usr/include"
        elif os.path.isdir("/usr/include/opencv4"):
            cv_include = "/usr/include/opencv4"
        elif os.path.isdir("/usr/local/include/opencv2"):
            cv_include = "/usr/local/include"
        elif os.path.isdir("/usr/local/include/opencv4"):
            cv_include = "/usr/local/include/opencv4"
        else:
            if cv_include == None:
                print("Did not find OpenCV include path! Please set cv_include manually!")
                print("Please type the OpenCV prefix e.g. /usr/include for /usr/include/opencv2:")
                cv_include = input()
                if not os.path.isdir(cv_include + "/opencv2"):
                    sys.exit("Did not find OpenCV in given path! Please set cv_include manually in make_config.py or retry!")
    return cv_include

####


# Interface path
root_path = os.path.abspath("./")

# Load build config
with open(root_path + "/build_config.toml", mode="rt", encoding="utf-8") as fp:
    config = tomlkit.load(fp)

# Collect data to include gRPC in the compile process and precompile the gRPC-connection infrastructure
grpc_include_dir = []
grpc_libs = []
grpc_lib_dir = []
grpc_package_data = []
grpc_link_args = []

if config['module_conf']['use_grpc']:
    # test ANNarchy
    try:
        import ANNarchy
        print('Checking for ANNarchy... OK')
    except Exception:
        print('Checking for ANNarchy... NO')
        print('Warning : Python package "ANNarchy" is required at runtime.')

    # protobuf, grpc
    grpc_avaiable = True

    if os.system("protoc --version") == 0:
        print('Checking for protoc ... OK')
    else:
        print('Checking for protoc ... OK')
        print("Protobuf C-compiler (protoc) not found")
        grpc_avaiable = False

    if grpc_avaiable:
        grpc_cpp_plugin = subprocess.check_output(["which", "grpc_cpp_plugin"]).strip().decode(sys.stdout.encoding)
        grpc_path = str(Path(grpc_cpp_plugin).resolve().parents[1]) + "/"
        grpc_include_path = grpc_path + "include/"
        grpc_lib_path = grpc_path + "lib/"
        grpc_bin_path = grpc_path + "bin/"

        protoc = subprocess.check_output(["which", "protoc"]).strip().decode(sys.stdout.encoding)
        protoc_path = str(Path(protoc).resolve().parents[1]) + "/"
        protoc_lib_path = protoc_path + "lib/"

        grpc_include_dir += ["ANN_iCub_Interface/grpc", grpc_include_path]
        grpc_libs += ["protobuf", "grpc++", "grpc++_reflection", "iCub_ANN_grpc"]
        grpc_lib_dir += [root_path+"/ANN_iCub_Interface/grpc", grpc_lib_path]
        grpc_package_data = ['ANNarchy_iCub_Populations/__init__.py', 'grpc/*.so', 'grpc/*.h']
        grpc_link_args += [f"-L{root_path}/ANN_iCub_Interface/grpc", f"-Wl,-rpath,{root_path}/ANN_iCub_Interface/grpc/", f"-Wl,-rpath,{grpc_lib_path}"]

        # build grpc proto related sourcefiles to library
        if os.path.isfile("./ANN_iCub_Interface/grpc/libiCub_ANN_grpc.so") and (not config['build']['rebuild_grpc']):
            print("Skip gRPC build process")
        else:
            # build the interface gRPC definitions
            os.system(f"protoc -I=. --cpp_out=. --grpc_out=. --plugin=protoc-gen-grpc={grpc_cpp_plugin} ANN_iCub_Interface/grpc/icub.proto")

            print("Build grpc->proto files in seperated library")
            curpath = os.path.abspath("./")
            os.system(f"cd ANN_iCub_Interface/grpc/ && make EXTFLAGS=\"-I{curpath} -I{grpc_include_path} -L{protoc_lib_path} -L{grpc_lib_path} -Wl,-rpath,{grpc_lib_path}\"")
    else:
        sys.exit("grpc and/or protobuf c-compiler is missing ... abort")

# Python Version info
py_major = sys.version_info[0]
py_minor = sys.version_info[1]
py_version = str(py_major) + "." + str(py_minor)

# Find YARP include path
special_include = []
special_lib = []
special_link_args = []
if config['path']['yarp_prefix'] == "default":
    yarp_prefix = set_yarp_prefix()
elif config['path']['yarp_prefix'] == "icub":
    yarp_prefix = "/usr/local/src/robot/yarp/build"
    include_prefix = "/usr/local/src/robot/yarp/src/"
    special_include = [ include_prefix + "libYARP_os/src", include_prefix + "libYARP_dev/src", include_prefix + "libYARP_sig/src", 
                        include_prefix + "libYARP_init/src", include_prefix + "libYARP_math/src", include_prefix + "libYARP_run/src", 
                        include_prefix + "libYARP_cv/src",
                        "/usr/local/src/robot/yarp/build/src/libYARP_conf/src",
                        "/usr/local/src/robot/yarp/src/libYARP_dev/src/idl_generated_code",
                        "/usr/local/src/robot/icub-main/src/libraries/iKin/include",
                        "/usr/local/src/robot/icub-main/src/libraries/ctrlLib/include"]
    special_lib = ["/usr/local/src/robot/icub-main/build/lib"]
else:
    if os.path.isdir(config['path']['yarp_prefix'] + "/include/yarp"):
        yarp_prefix = config['path']['yarp_prefix']
    else:
        sys.exit("Did not find YARP in given path! Please correct yarp_prefix in build_config.toml!")


yarp_version = subprocess.check_output(["yarp", "version"]).strip().decode(sys.stdout.encoding).replace("YARP version ", "")
yarp_version_major = int(yarp_version[0])
yarp_version_minor = int(yarp_version[2])
log_define = False
if yarp_version_major >= 3 and yarp_version_minor >= 4:
    log_define = True

# Find OpenCV include path
if config['path']['cv_include'] == "default":
    cv_include = set_opencv_prefix()
else:
    if not os.path.isdir(config['path']['cv_include'] + "/opencv2"):
        sys.exit("Did not find OpenCV in given path! Please correct cv_include in make_config.py!")

# Lists with lib/include directories and names
include_dir = ["ANN_iCub_Interface/include", "./", yarp_prefix + "/include", cv_include, numpy.get_include()] + grpc_include_dir + special_include
libs = ["opencv_core", "opencv_imgproc",
        "YARP_dev", "YARP_init", "YARP_math", "YARP_name", "YARP_os", "YARP_run", "YARP_sig"] + grpc_libs

lib_dirs = [yarp_prefix + "/lib"] + grpc_lib_dir + special_lib

# Prefixes for Cython and C++ based code
prefix_cy = "ANN_iCub_Interface/"
prefix_cpp = "ANN_iCub_Interface/src/"

# Sourcefile lists
sources = ["ANN_iCub_Interface/include/INI_Reader/INIReader.cpp", "ANN_iCub_Interface/include/INI_Reader/ini.cpp", prefix_cpp + "Module_Base_Class.cpp"]

package_data = ['__init__.py',
                'iCub/__init__.py',
                'iCub/include/*.hpp',
                'Sync/__init__.py',
                '*/*.pyi',
                'py.typed',
                'iCub/*.pxd'
                ] + grpc_package_data

# Set compile arguments
extra_compile_args = ["-g", "-fPIC", "-std=c++17", "--shared", "-O3", "-march=native", "-Wall", "-pthread"]
# , "-fpermissive" nicht als default; macht den Compiler relaxter;
# "-march=native" ermöglicht direkter Plattformabhängige Optimierung

if config['compiler']['verbose']:
    extra_compile_args.append("--verbose")
if config['compiler']['pedantic']:
    extra_compile_args.append("-pedantic")
if config['module_conf']['use_grpc']:
    extra_compile_args += ["-Wl,-rpath,"+root_path+"/ANN_iCub_Interface/grpc/", "-D_USE_GRPC"]
if config['module_conf']['double_precision']:
    extra_compile_args.append("-D_DOUBLE_PRECISION")
if log_define:
    extra_compile_args.append("-D_USE_LOG_QUIET")

# Define extensions for the cython-based modules
extensions = [
    Extension("ANN_iCub_Interface.iCub.Module_Base_Class", [prefix_cy + "iCub/Module_Base_Class.pyx"] + sources,
              include_dirs=include_dir,
              libraries=libs,
              library_dirs=lib_dirs,
              language="c++",
              extra_compile_args=extra_compile_args,
              extra_link_args=[] + grpc_link_args
              ),
    Extension("ANN_iCub_Interface.iCub.iCub_Interface", [prefix_cy + "iCub/iCub_Interface.pyx", prefix_cpp + "Interface_iCub.cpp"] + sources,
              include_dirs=include_dir,
              libraries=libs,
              library_dirs=lib_dirs,
              language="c++",
              extra_compile_args=extra_compile_args,
              extra_link_args=[] + grpc_link_args
              ),
    Extension("ANN_iCub_Interface.iCub.Joint_Reader", [prefix_cy + "iCub/Joint_Reader.pyx", prefix_cpp + "Joint_Reader.cpp"] + sources,
              include_dirs=include_dir,
              libraries=libs,
              library_dirs=lib_dirs,
              language="c++",
              extra_compile_args=extra_compile_args,
              extra_link_args=[] + grpc_link_args
              ),

    Extension("ANN_iCub_Interface.iCub.Joint_Writer", [prefix_cy + "iCub/Joint_Writer.pyx", prefix_cpp + "Joint_Writer.cpp"] + sources,
              include_dirs=include_dir,
              libraries=libs,
              library_dirs=lib_dirs,
              language="c++",
              extra_compile_args=extra_compile_args,
              extra_link_args=[] + grpc_link_args
              ),

    Extension("ANN_iCub_Interface.iCub.Skin_Reader", [prefix_cy + "iCub/Skin_Reader.pyx", prefix_cpp + "Skin_Reader.cpp"] + sources,
              include_dirs=include_dir,
              libraries=libs + ["iKin", "ctrlLib", "optimization"],
              library_dirs=lib_dirs,
              language="c++",
              extra_compile_args=extra_compile_args,
              extra_link_args=[] + grpc_link_args
              ),

    Extension("ANN_iCub_Interface.iCub.Visual_Reader", [prefix_cy + "iCub/Visual_Reader.pyx", prefix_cpp + "Visual_Reader.cpp"] + sources,
              include_dirs=include_dir,
              libraries=libs,
              library_dirs=lib_dirs,
              language="c++",
              extra_compile_args=extra_compile_args,
              extra_link_args=[] + grpc_link_args
              ),

    Extension("ANN_iCub_Interface.iCub.Kinematic_Reader", [prefix_cy + "iCub/Kinematic_Reader.pyx", prefix_cpp + "Kinematic_Reader.cpp"] + sources,
              include_dirs=include_dir,
              libraries=libs + ["iKin", "ctrlLib", "optimization"],
              library_dirs=lib_dirs,
              language="c++",
              extra_compile_args=extra_compile_args,
              extra_link_args=[] + grpc_link_args
              ),

    Extension("ANN_iCub_Interface.iCub.Kinematic_Writer", [prefix_cy + "iCub/Kinematic_Writer.pyx", prefix_cpp + "Kinematic_Writer.cpp"] + sources,
              include_dirs=include_dir,
              libraries=libs + ["iKin", "ctrlLib", "optimization", "ipopt"],
              library_dirs=lib_dirs,
              language="c++",
              extra_compile_args=extra_compile_args,
              extra_link_args=[] + grpc_link_args
              ),

    Extension("ANN_iCub_Interface.Sync.Master_Clock", [prefix_cy + "Sync/Master_Clock.pyx"],
              include_dirs=include_dir,
              libraries=libs,
              library_dirs=lib_dirs,
              language="c++",
              extra_compile_args=extra_compile_args
              )
]

# Set interface version
fileversion = './ANN_iCub_Interface/_version.txt'
with open(fileversion, 'r') as file_object:
    version = file_object.readlines()[0].rstrip()
fileversion_py = './ANN_iCub_Interface/_version.py'
with open(fileversion_py, 'w') as file_object:
    file_object.write("# automatically generated in setup.py\n")
    file_object.write("__version__ = \"" + version + "\"\n")

# Test if gRPC is already used -> need new cythonizing if prior build was without gRPC
try:
    from ANN_iCub_Interface._use_grpc import __use_grpc__ as used_grpc
except Exception:
    used_grpc = False

filegrpc = './ANN_iCub_Interface/_use_grpc.py'
with open(filegrpc, 'w') as file_object:
    file_object.write("# automatically generated in setup.py\n")
    file_object.write("__use_grpc__ = " + str(config['module_conf']['use_grpc']) + "\n")

force_rebuild = (config['module_conf']['use_grpc'] !=
                 used_grpc) or config['build']['rebuild_grpc'] or config['build']['rebuild_cython']

setup(
    packages=find_packages(),
    ext_modules=cythonize(extensions, nthreads=config['build']['num_threads'], language_level=int(sys.version_info[0]), force=force_rebuild),
    package_data={"ANN_iCub_Interface": package_data},
)
