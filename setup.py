from setuptools import Extension, setup
from Cython.Build import cythonize
import sys



libs = ["opencv_core", "opencv_imgproc", "python3.6m",
        "YARP_dev", "YARP_init", "YARP_math", "YARP_name",
        "YARP_os", "YARP_run", "YARP_sig"]

lib_dirs=['/usr/lib', '/usr/local/lib', '`/usr/bin/python3.6m-config --includes`']

include_dir = ["./include"]

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
        )
]

setup(
    name="iCub_Interface",
    ext_modules=cythonize(extensions),
    zip_safe=False
)

