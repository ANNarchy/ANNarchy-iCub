#pragma once

#include <grpcpp/grpcpp.h>

#include "iCub_ANN_Interface/grpc/icub.grpc.pb.h"


class ClientInstance
{
  std::unique_ptr<iCubInterfaceMessages::ProvideInput::Stub> stub_;

public:
    ClientInstance(std::string ip_address, unsigned int port) {
        auto server_str = ip_address + ":" + std::to_string(static_cast<long>(port));
        auto channel = grpc::CreateChannel(server_str, grpc::InsecureChannelCredentials());

        stub_ = iCubInterfaceMessages::ProvideInput::NewStub(channel);

        std::cout << "Client connects to " << server_str << std::endl;
    }


    std::vector<double> retrieve_image() {
        iCubInterfaceMessages::ImageRequest request;
        iCubInterfaceMessages::ImageResponse response;

        grpc::ClientContext context;

        // auto state = stub_->ReadTest(&context, request, &response);
        auto state = stub_->ReadImage(&context, request, &response);

        if (state.ok()) {
          return std::vector<double>(response.imagel().begin(),
                                     response.imagel().end());
        } else {
            std::cerr << "ClientInstance::retrieve_image() failed: " << state.error_message() << std::endl;
            return std::vector<double>(320 * 240, 0.0); // TODO: make dependent from Population geometry
        }
    }

    double retrieve_singlejoint(int joint) {
        iCubInterfaceMessages::SingleJointRequest request;
        iCubInterfaceMessages::SingleJointResponse response;

        grpc::ClientContext context;

        auto state = stub_->ReadSingleJoint(&context, request, &response);

        if (state.ok()) {
            return response.angle();
        } else {
            std::cerr << "ClientInstance::retrieve_singlejoint() failed: " << state.error_message() << std::endl;
            return 0;
        }
    }
};
