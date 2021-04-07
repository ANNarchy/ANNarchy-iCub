#pragma once

#include <grpcpp/grpcpp.h>

#include "iCub_ANN_Interface/grpc/icub.grpc.pb.h"

class WriteClientInstance
{
  std::unique_ptr<iCubInterfaceMessages::WriteOutput::Stub> stub_;

public:
    WriteClientInstance(std::string ip_address, unsigned int port) {
        auto server_str = ip_address + ":" + std::to_string(static_cast<long>(port));
        auto channel = grpc::CreateChannel(server_str, grpc::InsecureChannelCredentials());

        stub_ = iCubInterfaceMessages::WriteOutput::NewStub(channel);

        std::cout << "Client connects to " << server_str << std::endl;
    }

};
