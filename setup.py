

import os
import sys

from Cython.Build import cythonize
from setuptools import Extension, setup

# Python Version info
py_major = sys.version_info[0]
py_minor = sys.version_info[1]
py_version = str(py_major) + "." + str(py_minor)


# Yarp install direction
if "ROBOTOLOGY_SUPERBUILD_INSTALL_PREFIX" in os.environ:
    yarp_prefix = os.environ["ROBOTOLOGY_SUPERBUILD_INSTALL_PREFIX"]
elif "YARP_DATA_DIRS" in os.environ:
    yarp_data = os.environ['YARP_DATA_DIRS'].split(':')[0].split('/')
    if yarp_data[-1] == "iCub" or yarp_data[-1] == "yarp":
        yarp_prefix = "/".join(yarp_data[:-3])
    else:
        yarp_prefix = "/".join(yarp_data[:-2])
else:
    yarp_prefix = "/usr/local"


# OpenCV direction
cv_include = None

if os.path.isdir("/usr/include/opencv2"):
    cv_include = "/usr/include/"
elif os.path.isdir("/usr/include/opencv4"):
    cv_include = "/usr/include/opencv4"
elif os.path.isdir("/usr/local/include/opencv2"):
    cv_include = "/usr/local/include"
elif os.path.isdir("/usr/local/include/opencv4"):
    cv_include = "/usr/local/include/opencv4"
else:
    if cv_include == None:
        sys.exit("Did not find OpenCV include path! Please set cv_include manually!")

libs = ["opencv_core", "opencv_imgproc",
        "YARP_dev", "YARP_init", "YARP_math", "YARP_name", "YARP_os", "YARP_run", "YARP_sig"]

lib_dirs=["/usr/lib", "/usr/local/lib", yarp_prefix + "/lib"]

include_dir = ["./include", yarp_prefix + "/include", cv_include]

sources = ["include/INI_Reader/INIReader.cpp", "include/INI_Reader/ini.cpp"]
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
    ext_modules=cythonize(extensions),
    description="This program is an interface between the Neurosimulator ANNarchy and the iCub robot (tested with the iCub simulator and partly with gazebo). It is written in C++ with a Cython wrapping to Python.",
    version="0.2",
    author="Torsten Follak",
    keywords=["version", "0.2"],
    author_email="torsten.follak@informatik.tu-chemnitz.de",
    license="GNU General Public License V3",
    zip_safe=False
)

