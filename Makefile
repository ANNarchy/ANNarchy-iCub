# TODO: maybe a better name ;-)
all:
	cython ./Cython_ext/iCub_Interface.pyx ./Cython_ext/Joint_Reader.pyx ./Cython_ext/Joint_Writer.pyx ./Cython_ext/Skin_Reader.pyx ./Cython_ext/Visual_Reader.pyx --cplus

    # Build JointReader
	g++ -g -fPIC --shared -std=c++17 include/INI_Reader/*.cpp src/* ./Cython_ext/Joint_Reader.cpp -o \
	./build/Joint_Reader.so -Iinclude -L/usr/local/lib `/usr/bin/python3.6m-config --includes` -lopencv_core -lopencv_imgproc -lYARP_dev -lYARP_init -lYARP_math -lYARP_name -lYARP_os -lYARP_run -lYARP_sig -L/usr/lib -lpython3.6m

    # Build JointWriter
	g++ -g -fPIC --shared -std=c++17 include/INI_Reader/*.cpp src/* ./Cython_ext/Joint_Writer.cpp -o \
	./build/Joint_Writer.so -Iinclude -L/usr/local/lib `/usr/bin/python3.6m-config --includes` -lopencv_core -lopencv_imgproc -lYARP_dev -lYARP_init -lYARP_math -lYARP_name -lYARP_os -lYARP_run -lYARP_sig -L/usr/lib -lpython3.6m

    # Build SkinReader
	g++ -g -fPIC --shared -std=c++17 include/INI_Reader/*.cpp src/* ./Cython_ext/Skin_Reader.cpp -o \
	./build/Skin_Reader.so -Iinclude -L/usr/local/lib `/usr/bin/python3.6m-config --includes` -lopencv_core -lopencv_imgproc -lYARP_dev -lYARP_init -lYARP_math -lYARP_name -lYARP_os -lYARP_run -lYARP_sig -L/usr/lib -lpython3.6m

    # Build VisualReader
	g++ -g -fPIC --shared -std=c++17 include/INI_Reader/*.cpp src/* ./Cython_ext/Visual_Reader.cpp -o \
	./build/Visual_Reader.so -Iinclude -L/usr/local/lib `/usr/bin/python3.6m-config --includes` -lopencv_core -lopencv_imgproc -lYARP_dev -lYARP_init -lYARP_math -lYARP_name -lYARP_os -lYARP_run -lYARP_sig -L/usr/lib -lpython3.6m

    # Build Interface
	g++ -g -fPIC --shared -std=c++17 include/INI_Reader/*.cpp src/* ./Cython_ext/*.cpp -o \
	./build/iCub_Interface.so -Iinclude -L/usr/local/lib `/usr/bin/python3.6m-config --includes` -lopencv_core -lopencv_imgproc -lYARP_dev -lYARP_init -lYARP_math -lYARP_name -lYARP_os -lYARP_run -lYARP_sig -L/usr/lib -lpython3.6m

