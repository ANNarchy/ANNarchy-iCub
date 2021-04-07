#pragma once

#include <grpcpp/ext/proto_server_reflection_plugin.h>
#include <grpcpp/grpcpp.h>
#include <grpcpp/health_check_service_interface.h>

#include <thread>

#include "iCub_ANN_Interface/grpc/icub.grpc.pb.h"
#include "iCub_ANN_Interface/grpc/icub.pb.h"

template<typename ANNarchyPopulation>
class WriteOutputServiceImpl final : public iCubInterfaceMessages::WriteOutput::Service {

    grpc::Status WriteSingleTarget(grpc::ServerContext *context, const iCubInterfaceMessages::SingleTargetRequest *request,
                          iCubInterfaceMessages::SingleTargetResponse *response) override {

        response->set_angle(pop->r[0]);
        response->set_status(iCubInterfaceMessages::Status::SUCCESS);

        return grpc::Status::OK;
    }

public:
    WriteOutputServiceImpl(ANNarchyPopulation* pop) {
        this->pop = pop;
    }

    ANNarchyPopulation* pop;
};

template<typename ANNarchyPopulation>
class WriteOutputServerInstance {
    std::unique_ptr<grpc::Server> server;
    WriteOutputServiceImpl<ANNarchyPopulation>* _implementation;

public:
    WriteOutputServerInstance(std::string ip_address, unsigned int port, WriteOutputServiceImpl<ANNarchyPopulation>* implementation) {
        grpc::ServerBuilder builder;
        _implementation = implementation;

        grpc::EnableDefaultHealthCheckService(true);
        grpc::reflection::InitProtoReflectionServerBuilderPlugin();
        // Listen on the given address without any authentication mechanism.
        builder.AddListeningPort(ip_address + ":" + std::to_string(port), grpc::InsecureServerCredentials());
        // Register "service" as the instance through which we'll communicate with
        // clients. In this case it corresponds to an *synchronous* service.
        builder.RegisterService(implementation);
        // Increase the maximum message size (default 4 MB)
        // builder.SetMaxMessageSize(4*1024*1024);

        server = std::unique_ptr<grpc::Server>(builder.BuildAndStart());
        std::cout << "Write output server listening on " << ip_address << ":" << port << std::endl;
    }

    void wait() {
        // std::cout << "Server is in wait mode!" << std::endl;
        this->server->Wait();
    }

    void shutdown() {
        delete _implementation;
        std::cout << "Write output server: shutdown gRPC Server." << std::endl;
        this->server->Shutdown();
    }
};
