#pragma once

#include <grpc++/ext/proto_server_reflection_plugin.h>
#include <grpc++/grpc++.h>
#include <grpc++/health_check_service_interface.h>

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

    grpc::Status WriteSingleTargetEncoded(grpc::ServerContext *context, const iCubInterfaceMessages::SingleTargetEncodedRequest *request,
                                          iCubInterfaceMessages::SingleTargetEncodedResponse *response) override {

        response->mutable_angle()->Swap(&google::protobuf::RepeatedField<double> (pop->r.begin(), pop->r.end()));
        response->set_status(iCubInterfaceMessages::Status::SUCCESS);

        return grpc::Status::OK;
    }

    grpc::Status WriteMultiTargets(grpc::ServerContext *context, const iCubInterfaceMessages::MultiTargetRequest *request,
                                   iCubInterfaceMessages::MultiTargetResponse *response) override {

        response->mutable_angle()->Swap(&google::protobuf::RepeatedField<double> (pop->r.begin(), pop->r.end()));
        response->set_status(iCubInterfaceMessages::Status::SUCCESS);

        return grpc::Status::OK;
    }

    grpc::Status WriteMultiTargetsEncoded(grpc::ServerContext *context, const iCubInterfaceMessages::MultiTargetEncodedRequest *request,
                                          iCubInterfaceMessages::MultiTargetEncodedResponse *response) override {

        response->mutable_angle()->Swap(&google::protobuf::RepeatedField<double> (pop->r.begin(), pop->r.end()));
        response->set_status(iCubInterfaceMessages::Status::SUCCESS);

        return grpc::Status::OK;
    }

    grpc::Status WriteAllTargets(grpc::ServerContext *context, const iCubInterfaceMessages::AllTargetRequest *request,
                                   iCubInterfaceMessages::AllTargetResponse *response) override {

        response->mutable_angle()->Swap(&google::protobuf::RepeatedField<double> (pop->r.begin(), pop->r.end()));
        response->set_status(iCubInterfaceMessages::Status::SUCCESS);

        return grpc::Status::OK;
    }

    grpc::Status WriteAllTargetsEncoded(grpc::ServerContext *context, const iCubInterfaceMessages::AllTargetEncodedRequest *request,
                                        iCubInterfaceMessages::AllTargetEncodedResponse *response) override {

        response->mutable_angle()->Swap(&google::protobuf::RepeatedField<double> (pop->r.begin(), pop->r.end()));
        response->set_status(iCubInterfaceMessages::Status::SUCCESS);

        return grpc::Status::OK;
    }

public:
    WriteOutputServiceImpl(ANNarchyPopulation* pop) {
        this->pop = pop;
    }

    ANNarchyPopulation* pop; // never delete
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
        std::cout << "Write output server: shutdown gRPC Server." << std::endl;
        delete _implementation;
        this->server->Shutdown();
    }
};
