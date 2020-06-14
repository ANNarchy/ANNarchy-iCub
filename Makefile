# TODO: maybe a better name ;-)
all:
	cython iCub_Interface.pyx Joint_Reader.pyx Joint_Writer.pyx Skin_Reader.pyx Visual_Reader.pyx --cplus

    # Build JointReader
	g++ -g -fPIC --shared -std=c++17 include/INI_Reader/*.cpp src/* Joint_Reader.cpp -o \
	Joint_Reader.so -Iinclude -L/usr/local/lib `/usr/bin/python3.6m-config --includes` -lopencv_core -lopencv_imgproc -lYARP_dev -lYARP_init -lYARP_math -lYARP_name -lYARP_os -lYARP_run -lYARP_sig -L/usr/lib -lpython3.6m

    # Build JointWriter
	g++ -g -fPIC --shared -std=c++17 include/INI_Reader/*.cpp src/* Joint_Writer.cpp -o \
	Joint_Writer.so -Iinclude -L/usr/local/lib `/usr/bin/python3.6m-config --includes` -lopencv_core -lopencv_imgproc -lYARP_dev -lYARP_init -lYARP_math -lYARP_name -lYARP_os -lYARP_run -lYARP_sig -L/usr/lib -lpython3.6m

    # Build SkinReader
	g++ -g -fPIC --shared -std=c++17 include/INI_Reader/*.cpp src/* Skin_Reader.cpp -o \
	Skin_Reader.so -Iinclude -L/usr/local/lib `/usr/bin/python3.6m-config --includes` -lopencv_core -lopencv_imgproc -lYARP_dev -lYARP_init -lYARP_math -lYARP_name -lYARP_os -lYARP_run -lYARP_sig -L/usr/lib -lpython3.6m

    # Build VisualReader
	g++ -g -fPIC --shared -std=c++17 include/INI_Reader/*.cpp src/* Visual_Reader.cpp -o \
	Visual_Reader.so -Iinclude -L/usr/local/lib `/usr/bin/python3.6m-config --includes` -lopencv_core -lopencv_imgproc -lYARP_dev -lYARP_init -lYARP_math -lYARP_name -lYARP_os -lYARP_run -lYARP_sig -L/usr/lib -lpython3.6m

    # Build Interface
	g++ -g -fPIC --shared -std=c++17 include/INI_Reader/*.cpp src/* *.cpp -o \
	iCub_Interface.so -Iinclude -L/usr/local/lib `/usr/bin/python3.6m-config --includes` -lopencv_core -lopencv_imgproc -lYARP_dev -lYARP_init -lYARP_math -lYARP_name -lYARP_os -lYARP_run -lYARP_sig -L/usr/lib -lpython3.6m

