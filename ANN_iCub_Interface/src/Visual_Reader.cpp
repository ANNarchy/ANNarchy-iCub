/*
 *  Copyright (C) 2019-2022 Torsten Fietzek
 *
 *  VisualReader.cpp is part of the ANNarchy iCub interface
 *
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  The ANNarchy iCub interface is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this headers. If not, see <http://www.gnu.org/licenses/>.
 */

#include "Visual_Reader.hpp"

#include <yarp/cv/Cv.h>
#include <yarp/dev/all.h>
#include <yarp/os/all.h>
#include <yarp/sig/all.h>

#include <chrono>
#include <iostream>
#include <opencv2/opencv.hpp>
#include <queue>
#include <string>
#include <thread>
#include <vector>

#include "INI_Reader/INIReader.h"
#include "Module_Base_Class.hpp"
#ifdef _USE_GRPC
#include "ProvideInputServer.h"
#endif

typedef std::chrono::high_resolution_clock Clock;

// Destructor
VisualReader::~VisualReader() { Close(); }

// TODO(tofie): typing -> replace int with unsigned int, where it is useful
// integer bilder übertragen?
/*** public methods for the user ***/
bool VisualReader::Init(char eye, double fov_width, double fov_height, int img_width, int img_height, bool fast_filter, std::string ini_path) {
    /*
        Initialize Visual reader with given parameters for image resolution, field of view and eye selection

        params: char eye                        -- character representing the selected eye (l/L; r/R) or b/B for binocular mode
                                                   (right and left eye image are stored in the same buffer)
                double fov_width                -- output field of view width in degree [0, 60] (input fov width: 60°)
                double fov_height               -- output field of view height in degree [0, 48] (input fov height: 48°)
                int img_width                   -- output image width in pixel (input width: 320px)
                int img_height                  -- output image height in pixel (input height: 240px)
                bool fast_filter                -- flag to select the filter for image upscaling; True for a faster filter

        return: bool                -- return True, if successful
    */

    if (!this->dev_init) {
        // set ouput image size
        out_width = img_width;
        out_height = img_height;

        // check YARP-Network
        if (!yarp::os::Network::checkNetwork()) {
            std::cerr << "[Visual Reader] YARP Network is not online. Check nameserver is running!" << std::endl;
            return false;
        }

#ifdef _USE_LOG_QUIET
        // set YARP loging level to warnings, if the respective environment variable is set
        auto yarp_quiet = GetEnvVar("YARP_QUIET");
        if (yarp_quiet == "on" || yarp_quiet == "1") {
            yarp::os::Log::setMinimumPrintLevel(yarp::os::Log::WarningType);
        }
#endif

        // compute output field of view borders in input image
        if (fov_width <= icub_fov_x) {
            out_fov_x_low = static_cast<int>(ceil(FovX2PixelX(-fov_width / 2.0)));
            out_fov_x_up = static_cast<int>(floor(FovX2PixelX(fov_width / 2.0)));
        } else {
            std::cerr << "[Visual Reader] Selected field of view width is out of range" << std::endl;
            return false;
        }

        if (fov_height <= icub_fov_y) {
            out_fov_y_low = static_cast<int>(ceil(FovY2PixelY(fov_height / 2.0)));
            out_fov_y_up = static_cast<int>(floor(FovY2PixelY(-fov_height / 2.0)));
        } else {
            std::cerr << "[Visual Reader] Selected field of view height is out of range" << std::endl;
            return false;
        }

        // calculate output region of view (ROV) (image part equivalent to output field of view)
        rov_width = out_fov_x_up - out_fov_x_low;
        rov_height = out_fov_y_up - out_fov_y_low;
        if (rov_width != fov_width || rov_height != fov_height) {
            cut_img = true;
        } else {
            cut_img = false;
        }

        // set OpenCV type for use in method calls
        if (typeid(precision) == typeid(double)) {
            new_type = CV_64FC1;
            std::cout << "[Visual Reader] Double precision is selected." << std::endl;
        } else if (typeid(precision) == typeid(float)) {
            new_type = CV_32FC1;
            std::cout << "[Visual Reader] Single precision is selected." << std::endl;
        } else {
            std::cerr << "[Visual Reader] Precision type is not valid!" << std::endl;
            return false;
        }

        // calculate scaling factors to scale ROV to output image size
        res_scale_x = static_cast<double>(out_width) / (rov_width);
        res_scale_y = static_cast<double>(out_height) / (rov_height);

        // select filter for upscaling
        if (res_scale_y > 1 || res_scale_x > 1) {
            if (fast_filter) {
                filter_ds = cv::INTER_LINEAR;
            } else {
                filter_ds = cv::INTER_CUBIC;
            }
        }

        norm_fact = 1 / 255.0;

        // read configuration data from ini file
        INIReader reader_gen(ini_path + "/interface_param.ini");
        if (reader_gen.ParseError() != 0) {
            std::cerr << "[Visual Reader] Error in parsing the ini-file! Please check the ini-path \"" << ini_path << "\" and the ini file content!" << std::endl;
            return false;
        }
        bool on_Simulator = reader_gen.GetBoolean("general", "simulator", true);
        robot_port_prefix = reader_gen.Get("general", "robot_port_prefix", "/icubSim");
        if (on_Simulator && (robot_port_prefix != "/icubSim")) {
            std::cerr << "[Visual Reader] The port prefix does not match the default simulator prefix!" << std::endl;
        }
        client_port_prefix = reader_gen.Get("general", "client_port_prefix", "/client");

        bool gray = reader_gen.GetBoolean("vision", "gray", true);
        if (gray) {
            colorcode = cv::COLOR_RGB2GRAY;
        } else {
            colorcode = cv::COLOR_RGB2BGR;
        }

        // open and connect YARP port for the chosen eye
        if (eye == 'r' || eye == 'R') {    // right eye chosen
            act_eye = 'R';
            std::string port_name = client_port_prefix + "/V_Reader/image_" + eye + "/right:i";
            std::string robot_port_name = robot_port_prefix + "/cam/right";
            std::string robot_port_postfix = "/rgbImage:o";

            if (yarp::os::Network::exists(robot_port_name)) {
            } else if (yarp::os::Network::exists(robot_port_name + robot_port_postfix)) {
                robot_port_name = robot_port_name + robot_port_postfix;
            }

            port_right.open(port_name);
            if (!yarp::os::Network::connect(robot_port_name.c_str(), port_name.c_str())) {
                std::cerr << "[Visual Reader] Could not connect to right eye camera port!" << std::endl;
                return false;
            }
        } else if (eye == 'l' || eye == 'L') {    // left eye chosen
            act_eye = 'L';
            std::string robot_port_name = robot_port_prefix + "/cam/left";
            std::string robot_port_postfix = "/rgbImage:o";

            if (yarp::os::Network::exists(robot_port_name)) {
            } else if (yarp::os::Network::exists(robot_port_name + robot_port_postfix)) {
                robot_port_name = robot_port_name + robot_port_postfix;
            }

            std::string port_name = client_port_prefix + "/V_Reader/image_" + eye + "/left:i";
            port_left.open(port_name);
            if (!yarp::os::Network::connect(robot_port_name.c_str(), port_name.c_str())) {
                std::cerr << "[Visual Reader] Could not connect to left eye camera port!" << std::endl;
                return false;
            }
        } else if (eye == 'b' || eye == 'B') {    // both eyes chosen
            act_eye = 'B';

            std::string robot_port_name_l = robot_port_prefix + "/cam/left";
            std::string robot_port_postfix_l = "/rgbImage:o";

            if (yarp::os::Network::exists(robot_port_name_l)) {
            } else if (yarp::os::Network::exists(robot_port_name_l + robot_port_postfix_l)) {
                robot_port_name_l = robot_port_name_l + robot_port_postfix_l;
            }

            std::string port_name_l = client_port_prefix + "/V_Reader/image_" + eye + "/left:i";
            port_left.open(port_name_l);
            if (!yarp::os::Network::connect(robot_port_name_l.c_str(), port_name_l.c_str())) {
                std::cerr << "[Visual Reader] Could not connect to left eye camera port!" << std::endl;
                return false;
            }

            std::string robot_port_name_r = robot_port_prefix + "/cam/right";
            std::string robot_port_postfix_r = "/rgbImage:o";

            if (yarp::os::Network::exists(robot_port_name_r)) {
            } else if (yarp::os::Network::exists(robot_port_name_r + robot_port_postfix_r)) {
                robot_port_name_r = robot_port_name_r + robot_port_postfix_r;
            }

            std::string port_name_r = client_port_prefix + "/V_Reader/image_" + eye + "/right:i";
            port_right.open(port_name_r);
            if (!yarp::os::Network::connect(robot_port_name_r.c_str(), port_name_r.c_str())) {
                std::cerr << "[Visual Reader] Could not connect to right eye camera port!" << std::endl;
                return false;
            }
        } else {
            std::cerr << "[Visual Reader] Invalid character for eye selection!" << std::endl;
            return false;
        }

        this->type = "VisualReader";
        this->icub_part = std::string(1, eye);
        init_param["eye"] = std::to_string(act_eye);
        init_param["fov_width"] = std::to_string(fov_width);
        init_param["fov_height"] = std::to_string(fov_height);
        init_param["img_width"] = std::to_string(img_width);
        init_param["img_height"] = std::to_string(img_height);
        init_param["fast_filter"] = std::to_string(fast_filter);
        init_param["ini_path"] = ini_path;
        this->dev_init = true;
        return true;
    } else {
        std::cerr << "[Visual Reader] Initialization already done!" << std::endl;
        return false;
    }
}

#ifdef _USE_GRPC
bool VisualReader::InitGRPC(char eye, double fov_width, double fov_height, int img_width, int img_height, bool fast_filter, std::string ini_path, std::string ip_address,
                            unsigned int port) {
    /*
        Initialize Visual reader with given parameters for image resolution, field of view, eye selection and grpc parameter

        params: char eye                        -- character representing the selected eye (l/L; r/R) or b/B for binocular mode 
                                                   (right and left eye image are stored in the same buffer)
                double fov_width                -- output field of view width in degree [0, 60] (input fov width: 60°)
                double fov_height               -- output field of view height in degree [0, 48] (input fov height: 48°)
                int img_width                   -- output image width in pixel (input width: 320px)
                int img_height                  -- output image height in pixel (input height: 240px)
                bool fast_filter                -- flag to select the filter for image upscaling; True for a faster filter
                string ip_address               -- gRPC server ip address
                unsigned int port               -- gRPC server port

        return: bool                -- return True, if successful
    */

    if (!this->dev_init) {
        if (this->Init(eye, fov_width, fov_height, img_width, img_height, fast_filter, ini_path)) {
            this->_ip_address = ip_address;
            this->_port = port;
            this->image_source = new ServerInstance(ip_address, port, this);
            this->server_thread = std::thread(&ServerInstance::wait, this->image_source);
            init_param["ip_address"] = ip_address;
            init_param["port"] = std::to_string(port);
            dev_init_grpc = true;
            return true;
        } else {
            std::cerr << "[Visual Reader] Initialization failed!" << std::endl;
            return false;
        }
    } else {
        std::cerr << "[Visual Reader] Initialization already done!" << std::endl;
        return false;
    }
}
#else
bool VisualReader::InitGRPC(char eye, double fov_width, double fov_height, int img_width, int img_height, bool fast_filter, std::string ini_path, std::string ip_address,
                            unsigned int port) {
    /*
        Initialize Visual reader with given parameters for image resolution, field of view, eye selection and grpc parameter

        params: char eye                        -- character representing the selected eye (l/L; r/R) or b/B for binocular mode
                                                   (right and left eye image are stored in the same buffer)
                double fov_width                -- output field of view width in degree [0, 60] (input fov width: 60°)
                double fov_height               -- output field of view height in degree [0, 48] (input fov height: 48°)
                int img_width                   -- output image width in pixel (input width: 320px)
                int img_height                  -- output image height in pixel (input height: 240px)
                bool fast_filter                -- flag to select the filter for image upscaling; True for a faster filter
                string ip_address               -- gRPC server ip address
                unsigned int port               -- gRPC server port

        return: bool                -- return True, if successful
    */
    std::cerr << "[Visual Reader] gRPC is not included in the setup process!" << std::endl;
    return false;
}
#endif

std::vector<std::vector<VisualReader::precision>> VisualReader::ReadRobotEyes() {
    std::vector<std::vector<VisualReader::precision>> imgs;
    if (CheckInit()) {
        if (act_eye == 'B') {
            // read image from the iCub and get CV-Matrix
            iEyeRgb_r = port_left.read();
            iEyeRgb_l = port_right.read();

            if (iEyeRgb_r == nullptr || iEyeRgb_l == nullptr) {
                return imgs;
            }
            cv::Mat RgbMat_r = yarp::cv::toCvMat(*iEyeRgb_r);
            cv::Mat RgbMat_l = yarp::cv::toCvMat(*iEyeRgb_l);

            cv::cvtColor(RgbMat_r, tmpMat_r, colorcode);
            cv::cvtColor(RgbMat_l, tmpMat_l, colorcode);

            // extracting the output part of the field of view
            if (!cut_img) {
                ROV_r = tmpMat_r;
                ROV_l = tmpMat_l;
            } else {
                ROV_r = tmpMat_r(cv::Rect(out_fov_x_low, out_fov_y_low, rov_width, rov_height)).clone();
                ROV_l = tmpMat_l(cv::Rect(out_fov_x_low, out_fov_y_low, rov_width, rov_height)).clone();
            }

            // resize ROV to given output resolution
            if (res_scale_x == 1 && res_scale_x == 1) {
                monoMat_r = ROV_r;
                monoMat_l = ROV_l;

            } else if (res_scale_x < 1 || res_scale_x < 1) {
                cv::resize(ROV_r, monoMat_r, cv::Size(), res_scale_x, res_scale_y, cv::INTER_AREA);
                cv::resize(ROV_l, monoMat_l, cv::Size(), res_scale_x, res_scale_y, cv::INTER_AREA);

            } else {
                cv::resize(ROV_r, monoMat_r, cv::Size(), res_scale_x, res_scale_y, filter_ds);
                cv::resize(ROV_l, monoMat_l, cv::Size(), res_scale_x, res_scale_y, filter_ds);
            }

            // normalize the image from 0..255 to 0..1.0
            monoMat_r.convertTo(tmpMat1_r, new_type, norm_fact);
            monoMat_l.convertTo(tmpMat1_l, new_type, norm_fact);

            // flat the image matrix to 1D-vector
            std::vector<precision> img_vec_norm_r = MatC2Vec(tmpMat1_r);
            std::vector<precision> img_vec_norm_l = MatC2Vec(tmpMat1_l);

            // store image in the buffer
            imgs.push_back(img_vec_norm_r);
            imgs.push_back(img_vec_norm_l);
        } else {
            // read image from the iCub and get CV-Matrix
            if (act_eye == 'L') {
                iEyeRgb = port_left.read();
            }
            if (act_eye == 'R') {
                iEyeRgb = port_right.read();
            }

            if (iEyeRgb == nullptr) {
                return imgs;
            }
            imgs.push_back(ProcessRead());
        }
    }
    return imgs;
}

std::vector<uint8_t> VisualReader::RetrieveRobotEye() {
    std::vector<uint8_t> img;
    if (CheckInit()) {
        // read image from the iCub and get CV-Matrix
        if (act_eye == 'L') {
            iEyeRgb = port_left.read();
        }
        if (act_eye == 'R') {
            iEyeRgb = port_right.read();
        }

        if (iEyeRgb == nullptr) {
            return std::vector<uint8_t>();
        }
        // convert yarp image to vector
        std::vector<uint8_t> vec(iEyeRgb->getRawImage(), iEyeRgb->getRawImage() + iEyeRgb->getRawImageSize());
        return vec;
    }
    return std::vector<uint8_t>();
}

void VisualReader::Close() {
    /*
        Close module by closing the ports and shutdown gRPC connection
    */

#ifdef _USE_GRPC
    if (dev_init_grpc) {
        image_source->shutdown();
        server_thread.join();
        delete image_source;
        dev_init_grpc = false;
    }
#endif

    // close Ports
    // disconnect and close left eye port
    if (!port_left.isClosed()) {
        yarp::os::Network::disconnect(robot_port_prefix + "/cam/left", client_port_prefix + "/V_Reader/image/left:i");
        port_left.close();
    }

    // disconnect and close right eye port
    if (!port_right.isClosed()) {
        yarp::os::Network::disconnect(robot_port_prefix + "/cam/right", client_port_prefix + "/V_Reader/image/right:i");
        port_right.close();
    }

    this->dev_init = false;
}

/*** gRPC related functions ***/
#ifdef _USE_GRPC
std::vector<double> VisualReader::provideData() {
    std::vector<double> img;
    if (act_eye == 'L') {
        iEyeRgb = port_left.read();
    }
    if (act_eye == 'R') {
        iEyeRgb = port_right.read();
    }

    if (iEyeRgb == nullptr) {
        return img;
    }
    return ProcessRead();
}
#endif

/*** auxilary methods ***/
std::vector<VisualReader::precision> VisualReader::ProcessRead() {
    cv::Mat RgbMat = yarp::cv::toCvMat(*iEyeRgb);

    cv::cvtColor(RgbMat, tmpMat, colorcode);

    // extracting the output part of the field of view
    if (!cut_img) {
        ROV = tmpMat;
    } else {
        ROV = tmpMat(cv::Rect(out_fov_x_low, out_fov_y_low, rov_width, rov_height)).clone();
    }

    // resize ROV to given output resolution
    if (res_scale_x == 1 && res_scale_x == 1) {
        monoMat = ROV;
    } else if (res_scale_x < 1 || res_scale_x < 1) {
        cv::resize(ROV, monoMat, cv::Size(), res_scale_x, res_scale_y, cv::INTER_AREA);
    } else {
        cv::resize(ROV, monoMat, cv::Size(), res_scale_x, res_scale_y, filter_ds);
    }

    // normalize the image from 0..255 to 0..1.0
    monoMat.convertTo(tmpMat1, new_type, norm_fact);

    // flat the image matrix to 1D-vector
    return MatC2Vec(tmpMat1);
}

double VisualReader::FovX2PixelX(double fx) {
    /*
        Convert field of view horizontal degree position to horizontal pixel position

        params: double fx   -- horizontal field of view position in degree

        return: double      -- horizontal field of view position in pixel
    */
    double pixel;
    // conversion function retrieved from measured data
    pixel = 0.0006 * pow(fx, 3) + 4.8056 * fx + 160;
    return pixel;
}

double VisualReader::FovY2PixelY(double fy) {
    /*
        Convert field of view vertical degree position to vertical pixel position

        params: double fy   -- vertical field of view position in degree

        return: double      -- vertical field of view position in pixel
    */

    double pixel;
    // conversion function retrieved from measured data
    pixel = -0.0005 * pow(fy, 3) + 0.0005 * pow(fy, 2) - 4.7269 * fy + 120.0;
    return pixel;
}

std::vector<VisualReader::precision> VisualReader::Mat2Vec(cv::Mat matrix) {
    /*
        Convert a 2D-matrix to 1D-vector

        params: cv::Mat matrix                          -- image as 2D-matrix

        return: std::vector<VisualReader::precision>    -- image as 1D-vector
    */

    // convert a 2D-matrix to 1D-vector, distinguish two cases with different methods
    std::vector<precision> vec;

    if (matrix.isContinuous()) {    // faster, only possible when data is continous in memory
        vec.assign(reinterpret_cast<precision *>(matrix.data), reinterpret_cast<precision *>(matrix.data) + matrix.total());
    } else {    // slower, but is always possible
        for (int i = 0; i < matrix.rows; ++i) {
            vec.insert(vec.begin(), matrix.ptr<precision>(i), matrix.ptr<precision>(i) + matrix.cols);
        }
    }
    return vec;
}

std::vector<VisualReader::precision> VisualReader::MatC2Vec(cv::Mat matrix) {
    /*
        Convert a multi dimensional matrix to 1D-vector

        params: cv::Mat matrix        -- image as matrix

        return: std::vector<VisualReader::precision>    -- image as 1D-vector
    */

    // convert a multi dimensional matrix to 1D-vector, distinguish two cases with different methods
    std::vector<precision> vec;

    if (matrix.isContinuous()) {    // faster, only possible when data is continous in memory
        vec.assign(reinterpret_cast<precision *>(matrix.data), reinterpret_cast<precision *>(matrix.data) + matrix.total() * matrix.channels());
    } else {    // slower, but is always possible
        for (int i = 0; i < matrix.rows; ++i) {
            vec.insert(vec.begin(), matrix.ptr<precision>(i), matrix.ptr<precision>(i) + matrix.cols * matrix.channels());
        }
    }
    return vec;
}

std::vector<uint8_t> VisualReader::Mat3D2Vec(cv::Mat matrix) {
    /*
        Convert a 3D-matrix to 1D-vector

        params: cv::Mat matrix        -- image as 3D-matrix

        return: std::vector<uint8_t>    -- image as 1D-vector
    */

    // convert a 3D-matrix to 1D-vector, distinguish two cases with different methods
    std::vector<uint8_t> vec;

    if (matrix.isContinuous()) {    // faster, only possible when data is continous in memory
        vec.assign(matrix.data, matrix.data + matrix.total() * matrix.channels());
    } else {    // slower, but is always possible
        for (int i = 0; i < matrix.rows; ++i) {
            vec.insert(vec.begin(), matrix.ptr<uint8_t>(i), matrix.ptr<uint8_t>(i) + matrix.cols * matrix.channels());
        }
    }
    return vec;
}
