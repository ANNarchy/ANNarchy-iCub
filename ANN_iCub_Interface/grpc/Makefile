EXTFLAGS = ""
all:
	g++ -shared -g -fPIC -std=c++17 -O3 -Wall -march=native -pthread ./*.cc -o libiCub_ANN_grpc.so -lprotobuf -lgrpc++ -lgrpc++_reflection $(EXTFLAGS) 
