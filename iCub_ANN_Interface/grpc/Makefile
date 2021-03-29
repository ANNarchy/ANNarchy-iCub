EXTFLAGS = ""
all:
	g++ -shared -fPIC -fpermissive -std=c++14 ./*.cc -o libiCub_ANN_grpc.so \
    -L/usr/lib -lprotobuf -lgrpc++ -lgrpc++_reflection \
	$(EXTFLAGS)
