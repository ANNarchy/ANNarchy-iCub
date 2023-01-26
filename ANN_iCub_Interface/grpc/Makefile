EXTFLAGS = ""
all:
	g++ -shared -g -fPIC -std=c++17 -O2 -Wall -march=native -pthread ./*.cc -o libiCub_ANN_grpc.so -L/usr/lib -lprotobuf -lgrpc++ -lgrpc++_reflection $(EXTFLAGS) 
