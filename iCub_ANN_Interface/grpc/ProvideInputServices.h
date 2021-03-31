#pragma once

#include <thread>

#include <grpc++/grpc++.h>
#include <grpc++/health_check_service_interface.h>
#include <grpc++/ext/proto_server_reflection_plugin.h>

#include "iCub_ANN_Interface/grpc/icub.grpc.pb.h"
#include "iCub_ANN_Interface/grpc/icub.pb.h"

class ProvideInputServiceImpl final: public iCubInterfaceMessages::ProvideInput::Service {
    grpc::Status ReadImage(grpc::ServerContext* context, const iCubInterfaceMessages::ImageRequest *request, iCubInterfaceMessages::ImageResponse *response) {
        

        return grpc::Status::OK;
    }
};

class ServerInstance
{
    std::unique_ptr<grpc::Server> server;

public:

    ServerInstance(std::string ip_address, unsigned int port) {
        grpc::ServerBuilder builder;
        ProvideInputServiceImpl implementation;

        grpc::EnableDefaultHealthCheckService(true);
        grpc::reflection::InitProtoReflectionServerBuilderPlugin();
        // Listen on the given address without any authentication mechanism.
        builder.AddListeningPort(ip_address + ":" + std::to_string(port), grpc::InsecureServerCredentials());
        // Register "service" as the instance through which we'll communicate with
        // clients. In this case it corresponds to an *synchronous* service.
        builder.RegisterService(&implementation);
        // Increase the maximum message size (default 4 MB)
        builder.SetMaxMessageSize(4*1024*1024);

        server = std::unique_ptr<grpc::Server>(builder.BuildAndStart());
        std::cout << "Server listening on " << ip_address << ":" << port << std::endl;
        server->Wait();
    }

    void wait() {
        this->server->Wait();
    }

};

class ClientInstance
{
    std::unique_ptr<iCubInterfaceMessages::ProvideInput::Stub> stub_;

public:
    ClientInstance(std::string ip_address, unsigned int port) {
        auto server_str = ip_address+":"+std::to_string(static_cast<long>(port));
        auto channel = grpc::CreateChannel(server_str, grpc::InsecureChannelCredentials());

        stub_ = iCubInterfaceMessages::ProvideInput::NewStub(channel);

        std::cout << "Client connects to " << server_str << std::endl;
    }

    std::vector<double> retrieve_image() {
        grpc::ClientContext context;
        iCubInterfaceMessages::ImageRequest request;
        iCubInterfaceMessages::ImageResponse response;

        auto state = stub_->ReadImage(&context, request, &response);

        if (state.ok()) {
            return std::vector<double>();
        } else {
            std::cerr << "ClientInstance::retrieve_image() failed: " << state.error_message() << std::endl;
            return std::vector<double>();
        }
    }
};
