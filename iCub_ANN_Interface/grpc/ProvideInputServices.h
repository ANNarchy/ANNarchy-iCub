#pragma once

#include <grpc++/grpc++.h>
#include <grpc++/health_check_service_interface.h>
#include <grpc++/ext/proto_server_reflection_plugin.h>

#include "iCub_ANN_Interface/grpc/icub.grpc.pb.h"
#include "iCub_ANN_Interface/grpc/icub.pb.h"

class ProvideInputServiceImpl final: public iCubInterfaceMessages::ProvideInput::Service {
    grpc::Status ReadImage(grpc::ServerContext* context, const iCubInterfaceMessages::ImageRequest *request, iCubInterfaceMessages::ImageResponse *response) {
        
    }
};

class ANNarchyServiceInstance
{
    ProvideInputServiceImpl implementation_;
    grpc::ServerBuilder builder;
    std::unique_ptr<grpc::Server> server;

public:

    ANNarchyServiceInstance(std::string ip_address, unsigned int port) {
        grpc::EnableDefaultHealthCheckService(true);
        grpc::reflection::InitProtoReflectionServerBuilderPlugin();
        // Listen on the given address without any authentication mechanism.
        builder.AddListeningPort(ip_address + ":" + std::to_string(port), grpc::InsecureServerCredentials());
        // Register "service" as the instance through which we'll communicate with
        // clients. In this case it corresponds to an *synchronous* service.
        builder.RegisterService(&implementation_);
        // Increase the maximum message size (default 4 MB)
        builder.SetMaxMessageSize(4*1024*1024);
    }

};