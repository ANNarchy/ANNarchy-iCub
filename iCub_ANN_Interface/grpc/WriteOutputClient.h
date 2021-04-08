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

    double retrieve_singletarget(){
        iCubInterfaceMessages::SingleTargetRequest request;
        iCubInterfaceMessages::SingleTargetResponse response;

        grpc::ClientContext context;

        auto state = stub_->WriteSingleTarget(&context, request, &response);

        if (state.ok()) {
            return response.angle();
        } else {
            std::cerr << "WriteClientInstance::retrieve_singletarget() failed: " << state.error_message() << std::endl;
            return 0.;
        }
    }

    std::vector<double> retrieve_singletarget_enc() {
        iCubInterfaceMessages::SingleTargetEncodedRequest request;
        iCubInterfaceMessages::SingleTargetEncodedResponse response;

        grpc::ClientContext context;

        auto state = stub_->WriteSingleTargetEncoded(&context, request, &response);

        if (state.ok()) {
            return std::vector<double>(response.angle().begin(), response.angle().end());
        } else {
            std::cerr << "WriteClientInstance::retrieve_singletarget_enc() failed: " << state.error_message() << std::endl;
            return std::vector<double>(1., 0.0);
        }
    }

    std::vector<double> retrieve_multitarget() {
        iCubInterfaceMessages::MultiTargetRequest request;
        iCubInterfaceMessages::MultiTargetResponse response;

        grpc::ClientContext context;

        auto state = stub_->WriteMultiTargets(&context, request, &response);

        if (state.ok()) {
            return std::vector<double>(response.angle().begin(), response.angle().end());
        } else {
            std::cerr << "WriteClientInstance::retrieve_multitarget() failed: " << state.error_message() << std::endl;
            return std::vector<double>(1., 0.0);
        }
    }

    std::vector<double> retrieve_multitarget_enc() {
        iCubInterfaceMessages::MultiTargetEncodedRequest request;
        iCubInterfaceMessages::MultiTargetEncodedResponse response;

        grpc::ClientContext context;

        auto state = stub_->WriteMultiTargetsEncoded(&context, request, &response);

        if (state.ok()) {
            return std::vector<double>(response.angle().begin(), response.angle().end());
        } else {
            std::cerr << "WriteClientInstance::retrieve_multitarget_enc() failed: " << state.error_message() << std::endl;
            return std::vector<double>();
        }
    }

    std::vector<double> retrieve_alltarget() {
        iCubInterfaceMessages::AllTargetRequest request;
        iCubInterfaceMessages::AllTargetResponse response;

        grpc::ClientContext context;

        auto state = stub_->WriteAllTargets(&context, request, &response);

        if (state.ok()) {
            return std::vector<double>(response.angle().begin(), response.angle().end());
        } else {
            std::cerr << "WriteClientInstance::retrieve_alltarget() failed: " << state.error_message() << std::endl;
            return std::vector<double>(1., 0.0);
        }
    }

    std::vector<double> retrieve_alltarget_enc() {
        iCubInterfaceMessages::AllTargetEncodedRequest request;
        iCubInterfaceMessages::AllTargetEncodedResponse response;

        grpc::ClientContext context;

        auto state = stub_->WriteAllTargetsEncoded(&context, request, &response);

        if (state.ok()) {
            return std::vector<double>(response.angle().begin(), response.angle().end());
        } else {
            std::cerr << "WriteClientInstance::retrieve_alltarget_enc() failed: " << state.error_message() << std::endl;
            return std::vector<double>();
        }
    }
};
