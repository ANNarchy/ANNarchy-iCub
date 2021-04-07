#pragma once

#include <grpcpp/ext/proto_server_reflection_plugin.h>
#include <grpcpp/grpcpp.h>
#include <grpcpp/health_check_service_interface.h>

#include <thread>

#include "iCub_ANN_Interface/grpc/icub.grpc.pb.h"
#include "iCub_ANN_Interface/grpc/icub.pb.h"
#include "iCub_ANN_Interface/include/Module_Base_Class.hpp"

class ProvideInputServiceImpl final : public iCubInterfaceMessages::ProvideInput::Service {

    grpc::Status ReadTest(grpc::ServerContext *context, const iCubInterfaceMessages::TestRequest *request,
                          iCubInterfaceMessages::TestResponse *response) override {
        std::cout << "Read Test Request" << std::endl;
        response->set_status(iCubInterfaceMessages::Status::SUCCESS);
        return grpc::Status::OK;
    }

    grpc::Status ReadImage(grpc::ServerContext *context, const iCubInterfaceMessages::ImageRequest *request,
                           iCubInterfaceMessages::ImageResponse *response) override {
        auto image = interface_instance->provideData();
        google::protobuf::RepeatedField<double> data(image.begin(), image.end());
        response->mutable_imagel()->Swap(&data);
        return grpc::Status::OK;
    }

    grpc::Status ReadSingleJoint(grpc::ServerContext *context, const iCubInterfaceMessages::SingleJointRequest *request,
                                 iCubInterfaceMessages::SingleJointResponse *response) override {
        auto angle = interface_instance->provideData(request->joint(), request->encode());
        google::protobuf::RepeatedField<double> data(angle.begin(), angle.end());
        response->mutable_angle()->Swap(&data);
        return grpc::Status::OK;
    }

    grpc::Status ReadMultiJoints(grpc::ServerContext *context, const iCubInterfaceMessages::MultiJointRequest *request,
                               iCubInterfaceMessages::MultiJointResponse *response) override {
        auto angles =
            interface_instance->provideData(std::vector<int32_t>(request->joint().begin(), request->joint().end()), request->encode());
        google::protobuf::RepeatedField<double> data(angles.begin(), angles.end());
        response->mutable_angle()->Swap(&data);
        return grpc::Status::OK;
    }

    grpc::Status ReadAllJoints(grpc::ServerContext *context, const iCubInterfaceMessages::AllJointsRequest *request,
                                 iCubInterfaceMessages::AllJointsResponse *response) override {
        auto angles = interface_instance->provideData(request->encode());
        google::protobuf::RepeatedField<double> data(angles.begin(), angles.end());
        response->mutable_angle()->Swap(&data);
        return grpc::Status::OK;
    }

 public:
    Mod_BaseClass *interface_instance;
};

class ServerInstance {
    std::unique_ptr<grpc::Server> server;
    // ProvideInputServiceImpl implementation;
    ProvideInputServiceImpl implementation;

 public:
    ServerInstance(std::string ip_address, unsigned int port, Mod_BaseClass *interface_instance) {
        implementation.interface_instance = interface_instance;
        grpc::ServerBuilder builder;

        grpc::EnableDefaultHealthCheckService(true);
        grpc::reflection::InitProtoReflectionServerBuilderPlugin();
        // Listen on the given address without any authentication mechanism.
        builder.AddListeningPort(ip_address + ":" + std::to_string(port), grpc::InsecureServerCredentials());
        // Register "service" as the instance through which we'll communicate with
        // clients. In this case it corresponds to an *synchronous* service.
        builder.RegisterService(&implementation);
        // Increase the maximum message size (default 4 MB)
        // builder.SetMaxMessageSize(4*1024*1024);

        server = std::unique_ptr<grpc::Server>(builder.BuildAndStart());
        std::cout << "[" << implementation.interface_instance->get_identifier() << "] Server listening on " << ip_address << ":" << port
                  << std::endl;
    }

    void wait() {
        // std::cout << "Server is in wait mode!" << std::endl;
        this->server->Wait();
    }

    void shutdown() {
        std::cout << "[" << implementation.interface_instance->get_identifier() << "] Shutdown gRPC Server." << std::endl;
        this->server->Shutdown();
    }
};