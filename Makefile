# TODO: maybe a better name ;-)
all:
	cython iCub_Interface.pyx --cplus

	g++ -g -fPIC --shared -std=c++17 include/INI_Reader/*.cpp src/* *.cpp -o \
	iCub_Interface.so -Iinclude -L/usr/local/lib `/usr/bin/python3.6m-config --includes` -lopencv_core -lopencv_imgproc -lYARP_dev -lYARP_init -lYARP_math -lYARP_name -lYARP_os -lYARP_run -lYARP_sig -L/usr/lib -lpython3.6m

