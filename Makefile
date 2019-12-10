# TODO: maybe a better name ;-)
all:
	cython iCubCPP.pyx --cplus

	g++ -g -fPIC --shared -std=c++11 include/INI_Reader/*.cpp src/* *.cpp -o \
	iCubCPP.so -Iinclude -L/usr/local/lib `/scratch/tofo/anaconda/bin/python3.7m-config --includes` -lopencv_core -lopencv_imgproc -lYARP_dev -lYARP_init -lYARP_math -lYARP_name -lYARP_OS -lYARP_run -lYARP_sig -L/scratch/tofo/anaconda/lib -lpython3.7m

