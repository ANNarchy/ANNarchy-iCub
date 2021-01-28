"""
Created on Thu Jul 9 20:26:04 CEST 2020

@author: Torsten Fietzek

produces Makefile from Makefile.template
"""
import os
import sys

from make_config import *

def set_yarp_prefix():
    # Yarp install direction
    yarp_prefix = None

    if "ROBOTOLOGY_SUPERBUILD_INSTALL_PREFIX" in os.environ:
        yarp_prefix = os.environ["ROBOTOLOGY_SUPERBUILD_INSTALL_PREFIX"]
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
                sys.exit("Did not find YARP in given path! Please set yarp_prefix manually in make_config.py or retry!")
    return yarp_prefix

def set_opencv_prefix():
    # OpenCV direction
    cv_include = None

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


if __name__ == "__main__":
    print("Start generating Makefile ...")
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


    with open("Makefile.template", "r") as makefile:
        if makefile.mode == 'r':
            contents =makefile.read()

    new_content = contents.replace("PYTHON_INCLUDE", "`/usr/bin/python" + py_version + "-config --includes`") #
    new_content = new_content.replace("OPENCV_INCLUDE", "-I" + cv_include)
    new_content = new_content.replace("YARP_LIB", "-L" + yarp_prefix + "/lib")
    if verbose:
        new_content = new_content.replace("VERBOSE", "--verbose")
    else:
        new_content = new_content.replace("VERBOSE ", "")

    f=open("Makefile", "w")
    if f.mode == 'w':
        f.write(new_content)
    f.close()
    print("Generated Makefile")

    print("Start Compiling ...")
    if not os.path.isdir("./build"):
        os.mkdir("./build")
    j_arg = ""
    if len(sys.argv) > 1:
        if type(sys.argv[1] == int):
            j_arg = " -j" + sys.argv[1]
    return_val = os.system("make" + j_arg)
    if return_val == 0:
        print("Finished Compiling")
    elif return_val == 2:
        print("Compilation interrupted!")
    elif return_val == 512:
        print("Compilation failed!")
        print("Please check include directories for YARP, OpenCV and Python!")
    else:
        print("Compilation failed!")
