#pragma once

#include <grpcpp/grpcpp.h>

#include "iCub_ANN_Interface/grpc/icub.grpc.pb.h"

class ClientInstance {
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
            return std::vector<double>(response.imagel().begin(), response.imagel().end());
        } else {
            std::cerr << "ClientInstance::retrieve_image() failed: " << state.error_message() << std::endl;
            return std::vector<double>(320 * 240, 0.0);    // TODO: make dependent from Population geometry
        }
    }

    std::vector<double> retrieve_singlejoint(int joint, bool encode) {
        iCubInterfaceMessages::SingleJointRequest request;
        request.set_joint(joint);
        request.set_encode(encode);
        iCubInterfaceMessages::SingleJointResponse response;

        grpc::ClientContext context;

        auto state = stub_->ReadSingleJoint(&context, request, &response);

        if (state.ok()) {
            return std::vector<double>(response.angle().begin(), response.angle().end());
        } else {
            std::cerr << "ClientInstance::retrieve_singlejoint() failed: " << state.error_message() << std::endl;
            return std::vector<double>(1, 0.0);    // TODO: make dependent from Population geometry
        }
    }

    std::vector<double> retrieve_multijoints(std::vector<int> joints, bool encode) {
        iCubInterfaceMessages::MultiJointRequest request;
        request.set_encode(encode);
        request.mutable_joint()->Swap(&google::protobuf::RepeatedField<int>(joints.begin(), joints.end()));
        iCubInterfaceMessages::MultiJointResponse response;

        grpc::ClientContext context;

        auto state = stub_->ReadMultiJoints(&context, request, &response);

        if (state.ok()) {
            return std::vector<double>(response.angle().begin(), response.angle().end());
        } else {
            std::cerr << "ClientInstance::retrieve_multijoints() failed: " << state.error_message() << std::endl;
            return std::vector<double>(1, 0.0);    // TODO: make dependent from Population geometry
        }
    }

    std::vector<double> retrieve_alljoints(bool encode) {
        iCubInterfaceMessages::AllJointsRequest request;
        request.set_encode(encode);
        iCubInterfaceMessages::AllJointsResponse response;

        grpc::ClientContext context;

        auto state = stub_->ReadAllJoints(&context, request, &response);

        if (state.ok()) {
            return std::vector<double>(response.angle().begin(), response.angle().end());
        } else {
            std::cerr << "ClientInstance::retrieve_alljoints() failed: " << state.error_message() << std::endl;
            return std::vector<double>(1, 0.0);    // TODO: make dependent from Population geometry
        }
    }

    std::vector<double> retrieve_skin_arm() {
        iCubInterfaceMessages::SkinArmRequest request;
        iCubInterfaceMessages::SkinResponse response;

        grpc::ClientContext context;

        // auto state = stub_->ReadTest(&context, request, &response);
        auto state = stub_->ReadSkinArm(&context, request, &response);

        if (state.ok()) {
            return std::vector<double>(response.sensor_data().begin(), response.sensor_data().end());
        } else {
            std::cerr << "ClientInstance::retrieve_image() failed: " << state.error_message() << std::endl;
            return std::vector<double>(1, 0.0);    // TODO: make dependent from Population geometry
        }
    }

    std::vector<double> retrieve_skin_forearm() {
        iCubInterfaceMessages::SkinForearmRequest request;
        iCubInterfaceMessages::SkinResponse response;

        grpc::ClientContext context;

        // auto state = stub_->ReadTest(&context, request, &response);
        auto state = stub_->ReadSkinForearm(&context, request, &response);

        if (state.ok()) {
            return std::vector<double>(response.sensor_data().begin(), response.sensor_data().end());
        } else {
            std::cerr << "ClientInstance::retrieve_image() failed: " << state.error_message() << std::endl;
            return std::vector<double>(1, 0.0);    // TODO: make dependent from Population geometry
        }
    }

    std::vector<double> retrieve_skin_hand() {
        iCubInterfaceMessages::SkinHandRequest request;
        iCubInterfaceMessages::SkinResponse response;

        grpc::ClientContext context;

        // auto state = stub_->ReadTest(&context, request, &response);
        auto state = stub_->ReadSkinHand(&context, request, &response);

        if (state.ok()) {
            return std::vector<double>(response.sensor_data().begin(), response.sensor_data().end());
        } else {
            std::cerr << "ClientInstance::retrieve_image() failed: " << state.error_message() << std::endl;
            return std::vector<double>(1, 0.0);    // TODO: make dependent from Population geometry
        }
    }

    std::vector<double> retrieve_kinematic_hand() {
        iCubInterfaceMessages::KinematicRequest request;
        iCubInterfaceMessages::KinematicResponse response;

        grpc::ClientContext context;

        // auto state = stub_->ReadTest(&context, request, &response);
        auto state = stub_->ReadKinematicHand(&context, request, &response);

        if (state.ok()) {
            return std::vector<double>(response.position().begin(), response.position().end());
        } else {
            std::cerr << "ClientInstance::retrieve_kinematic_hand() failed: " << state.error_message() << std::endl;
            return std::vector<double>(3, 0.0);    // TODO: make dependent from Population geometry
        }
    }
};
