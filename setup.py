

import os
import sys

from setuptools import Extension, setup, find_packages
from Cython.Build import cythonize

from make_config import yarp_prefix, cv_include
from make import set_opencv_prefix, set_yarp_prefix

# Python Version info
py_major = sys.version_info[0]
py_minor = sys.version_info[1]
py_version = str(py_major) + "." + str(py_minor)

if yarp_prefix == "default":
    yarp_prefix = set_yarp_prefix()
else:
    if not os.path.isdir(yarp_prefix + "/include/yarp"):
        sys.exit("Did not find YARP in given path! Please correct yarp_prefix in make_config.py!")

if cv_include == "default":
    cv_include = set_opencv_prefix()
else:
    if not os.path.isdir(cv_include + "/opencv2"):
        sys.exit("Did not find OpenCV in given path! Please correct cv_include in make_config.py!")

include_dir = ["iCub_ANN_Interface/include", yarp_prefix + "/include", cv_include]

libs = ["opencv_core", "opencv_imgproc",
        "YARP_dev", "YARP_init", "YARP_math", "YARP_name", "YARP_os", "YARP_run", "YARP_sig"]

lib_dirs=["/usr/lib", "/usr/local/lib", yarp_prefix + "/lib"]


prefix_cy = "iCub_ANN_Interface/"
prefix_cpp = "iCub_ANN_Interface/src/"

sources = ["iCub_ANN_Interface/include/INI_Reader/INIReader.cpp", "iCub_ANN_Interface/include/INI_Reader/ini.cpp", prefix_cpp + "Module_Base_Class.cpp"]
sources1 = [prefix_cpp + "Joint_Reader.cpp", prefix_cpp + "Joint_Writer.cpp", prefix_cpp + "Skin_Reader.cpp", prefix_cpp + "Visual_Reader.cpp"]

package_data = ['__init__.py', 
                'iCub/*pxd',
                'iCub/*pyx',
                'iCub/__init__.py',
                'Sync/*pyx',
                'Sync/__init__.py',
                ]

extra_compile_args = ["-g", "-fPIC", "-std=c++17", "--shared", "-O2", "-w"]

extensions = [
    Extension("iCub_ANN_Interface.iCub.Joint_Reader", [prefix_cy + "iCub/Joint_Reader.pyx", prefix_cpp + "Joint_Reader.cpp"] + sources,
        include_dirs=include_dir,
        libraries=libs,
        library_dirs=lib_dirs,
        language="c++",
        extra_compile_args=extra_compile_args
        ),

    Extension("iCub_ANN_Interface.iCub.Joint_Writer", [prefix_cy + "iCub/Joint_Writer.pyx", prefix_cpp + "Joint_Writer.cpp"] + sources,
        include_dirs=include_dir,
        libraries=libs,
        library_dirs=lib_dirs,
        language="c++",
        extra_compile_args=extra_compile_args
        ),

    Extension("iCub_ANN_Interface.iCub.Skin_Reader", [prefix_cy + "iCub/Skin_Reader.pyx", prefix_cpp + "Skin_Reader.cpp"] + sources,
        include_dirs=include_dir,
        libraries=libs,
        library_dirs=lib_dirs,
        language="c++",
        extra_compile_args=extra_compile_args
        ),

    Extension("iCub_ANN_Interface.iCub.Visual_Reader", [prefix_cy + "iCub/Visual_Reader.pyx", prefix_cpp + "Visual_Reader.cpp"] + sources,
        include_dirs=include_dir,
        libraries=libs,
        library_dirs=lib_dirs,
        language="c++",
        extra_compile_args=extra_compile_args
        ),

    Extension("iCub_ANN_Interface.iCub.iCub_Interface", [prefix_cy + "iCub/iCub_Interface.pyx", prefix_cpp + "Interface_iCub.cpp"] + sources + sources1,
        include_dirs=include_dir,
        libraries=libs,
        library_dirs=lib_dirs,
        language="c++",
        extra_compile_args=extra_compile_args
        ),

    Extension("iCub_ANN_Interface.Sync.Master_Clock", [prefix_cy + "Sync/Master_Clock.pyx"],
        include_dirs=include_dir,
        libraries=libs,
        library_dirs=lib_dirs,
        language="c++",
        extra_compile_args=extra_compile_args
        )
]

setup(
    name="iCub_ANN_Interface",
    packages=find_packages(),
    ext_modules=cythonize(extensions, language_level=int(sys.version_info[0])),
    description="Interface for iCub robot and ANNarchy neuro-simulator",
    long_description="""This program is an interface between the Neurosimulator ANNarchy and the iCub robot (tested with the iCub simulator and partly with gazebo). It is written in C++ with a Cython wrapping to Python.""",
    version="1.0",
    author="Torsten Fietzek",
    author_email="torsten.fietzek@informatik.tu-chemnitz.de",
    license="GPLv2+",
    zip_safe=False,
    package_data={'iCub_ANN_Interface': package_data},
    install_requires=[
        'numpy',
        'cython'
    ]
)

