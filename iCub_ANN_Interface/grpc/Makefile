EXTFLAGS = ""
all:
	g++ -shared -g -fPIC -std=c++14 -O2 -Wall -march=native ./*.cc -o libiCub_ANN_grpc.so \
	$(EXTFLAGS) \
    -L/usr/lib -lprotobuf -lgrpc++ -lgrpc++_reflection
