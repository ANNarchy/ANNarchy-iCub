

import os
import sys

from setuptools import Extension, setup
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

include_dir = ["./include", yarp_prefix + "/include", cv_include]

libs = ["opencv_core", "opencv_imgproc",
        "YARP_dev", "YARP_init", "YARP_math", "YARP_name", "YARP_os", "YARP_run", "YARP_sig"]

lib_dirs=["/usr/lib", "/usr/local/lib", yarp_prefix + "/lib"]

sources = ["include/INI_Reader/INIReader.cpp", "include/INI_Reader/ini.cpp", "src/Module_Base_Class.cpp"]
sources1 = ["src/Joint_Reader.cpp", "src/Joint_Writer.cpp", "src/Skin_Reader.cpp", "src/Visual_Reader.cpp"]

extensions = [
    Extension("Joint_Reader", ["Cython_ext/Joint_Reader.pyx", "src/Joint_Reader.cpp"] + sources,
        include_dirs=include_dir,
        libraries=libs,
        library_dirs=lib_dirs,
        language="c++",
        extra_compile_args=["-g", "-fPIC", "-std=c++17", "--shared"]
        ),

    Extension("Joint_Writer", ["Cython_ext/Joint_Writer.pyx", "src/Joint_Writer.cpp"] + sources,
        include_dirs=include_dir,
        libraries=libs,
        library_dirs=lib_dirs,
        language="c++",
        extra_compile_args=["-g", "-fPIC", "-std=c++17", "--shared"]
        ),

    Extension("Skin_Reader", ["Cython_ext/Skin_Reader.pyx", "src/Skin_Reader.cpp"] + sources,
        include_dirs=include_dir,
        libraries=libs,
        library_dirs=lib_dirs,
        language="c++",
        extra_compile_args=["-g", "-fPIC", "-std=c++17", "--shared"]
        ),

    Extension("Visual_Reader", ["Cython_ext/Visual_Reader.pyx", "src/Visual_Reader.cpp"] + sources,
        include_dirs=include_dir,
        libraries=libs,
        library_dirs=lib_dirs,
        language="c++",
        extra_compile_args=["-g", "-fPIC", "-std=c++17", "--shared"]
        ),

    Extension("iCub_Interface", ["Cython_ext/iCub_Interface.pyx","./src/Interface_iCub.cpp"] + sources + sources1,
        include_dirs=include_dir,
        libraries=libs,
        library_dirs=lib_dirs,
        language="c++",
        extra_compile_args=["-g", "-fPIC", "-std=c++17", "--shared"]
        ),
    Extension("MasterClock", ["Cython_ext/Master_Clock.pyx"],
        include_dirs=include_dir,
        libraries=libs,
        library_dirs=lib_dirs,
        language="c++",
        extra_compile_args=["-g", "-fPIC", "-std=c++17", "--shared"]
        )
]

setup(
    name="iCub_Interface",
    ext_modules=cythonize(extensions, show_all_warnings=True),
    description="This program is an interface between the Neurosimulator ANNarchy and the iCub robot (tested with the iCub simulator and partly with gazebo). It is written in C++ with a Cython wrapping to Python.",
    version="0.3",
    author="Torsten Fietzek",
    keywords=["version", "0.2"],
    author_email="torsten.fietzek@informatik.tu-chemnitz.de",
    license="GNU General Public License V3",
    zip_safe=False
)

