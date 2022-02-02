/*
 *  Copyright (C) 2019-2021 Torsten Fietzek
 *
 *  Visual_Reader.hpp is part of the iCub ANNarchy interface
 *
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  The iCub ANNarchy interface is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this headers. If not, see <http://www.gnu.org/licenses/>.
 */

#pragma once

#include <yarp/os/all.h>
#include <yarp/sig/all.h>

#include <deque>
#include <map>
#include <opencv2/opencv.hpp>
#include <string>
#include <thread>
#include <vector>

#include "Module_Base_Class.hpp"
#ifdef _USE_GRPC
#include "ProvideInputServer.h"
#endif

/**
 * \brief  Read-out of the camera images from the iCub robot
 */
// class VisualReader : private yarp::os::RFModule, public Mod_BaseClass {
class VisualReader : public Mod_BaseClass {

 public:
#ifndef _DOUBLE_PRECISION
    typedef float precision;
#endif
#ifdef _DOUBLE_PRECISION
    typedef double precision;
#endif

    VisualReader() = default;
    ~VisualReader();

    /*** public methods for the user ***/

    /**
     * \brief Init Visual reader with given parameters for image resolution, field of view and eye selection.
     * \param[in] eye character representing the selected eye (l/L; r/R) or b/B for binocular mode (right and left eye image are stored in the same buffer)
     * \param[in] fov_width output field of view width in degree [0, 60] (input fov width: 60°)
     * \param[in] fov_height output field of view height in degree [0, 48] (input fov height: 48°)
     * \param[in] img_width output image width in pixel (input width: 320px)
     * \param[in] img_height output image height in pixel (input height: 240px)
     * \param[in] max_buffer_size maximum buffer length
     * \param[in] fast_filter flag to select the filter for image upscaling; True for a faster filter
     * \return True, if the initializatiion was successful. False if an error occured. Additionally, an error message is written to the error stream (cerr).\n
     *          Typical errors:
     *              - arguments not valid: e.g. eye character not valid
     *              - YARP-Server not running
     */
    bool Init(char eye, double fov_width, double fov_height, int img_width, int img_height, unsigned int max_buffer_size, bool fast_filter,
              std::string ini_path);

    /**
     * \brief Init Visual reader with given parameters for image resolution, field of view and eye selection. 
     * \param[in] eye character representing the selected eye (l/L; r/R) or b/B for binocular mode (right and left eye image are stored in the same buffer) 
     * \param[in] fov_width output field of view width in degree [0, 60] (input fov width: 60°) 
     * \param[in] fov_height * output field of view height in degree [0, 48] (input fov height: 48°)
     * \param[in] img_width output image width in pixel (input width: 320px)
     * \param[in] img_height output image height in pixel (input height: 240px)
     * \param[in] max_buffer_size maximum buffer length
     * \param[in] fast_filter flag to select the filter for image upscaling; True for a faster filter 
     * \param[in] ip_address gRPC server ip address -> has to match ip address of the Vision-Population
     * \param[in] port gRPC server port -> has to match port of the Vision-Population
     * \return True, if the initializatiion was successful. False if an error occured. Additionally, an error message is written to the error stream (cerr).\n 
     *          Typical errors:
     *              - arguments not valid: e.g. eye character not valid
     *              - YARP-Server not running
     */
    bool InitGRPC(char eye, double fov_width, double fov_height, int img_width, int img_height, unsigned int max_buffer_size,
                  bool fast_filter, std::string ini_path, std::string ip_address, unsigned int port);

    /**
     * \brief Read a set of images from the robot cameras.
     * \return camera images.
     */
    std::vector<std::vector<precision>> ReadRobotEyes();

    /**
     * \brief Close Visual Reader module.
     */
    void Close() override;

#ifdef _USE_GRPC
    std::vector<double> provideData();
#endif

 private:
    /** configuration variables **/
    unsigned int buffer_len = 30;    // length of the image buffer
    bool rf_running = false;

    char act_eye;           // selected iCub eye to read images from
    int filter_ds;          // filter for the upscaling of the image
    bool cut_img;           // flag, being true if a part of the field of view is cutted of the image
    precision norm_fact;    // normalization factor for the normalization of the image

    /** fix iCub-visual data **/
    const int icub_width = 320;      // iCub image width in pixel
    const int icub_height = 240;     // iCub image height in pixel
    const double icub_fov_x = 60;    // iCub field of view horizontal in degree
    const double icub_fov_y = 48;    // iCub field of view vertical in degree

    /** image parameter **/
    int out_fov_x_up, out_fov_x_low;    // pixel borders for horizontal field of view in the iCub image
    int out_fov_y_up, out_fov_y_low;    // pixel borders for vertical field of view in the iCub image
    int rov_width;                      // image width for given horizontal field of view (ROV, region of view)
    int rov_height;                     // image height for given vertical field of view (ROV, region of view)

    int out_width;     // output image width in pixel
    int out_height;    // output image height in pixel

    double res_scale_x;    // scaling factor in x direction to scale ROV to ouput image width
    double res_scale_y;    // scaling factor in y direction to scale ROV to ouput image height

    /** image data structures **/
    std::deque<std::vector<precision>> img_buffer;    // buffer to store the preprocessed iCub images

    yarp::sig::ImageOf<yarp::sig::PixelRgb> *iEyeRgb;                  // YARP-image structure for image handling -> single eye
    yarp::sig::ImageOf<yarp::sig::PixelRgb> *iEyeRgb_r, *iEyeRgb_l;    // YARP-image structure for image handling -> both eyes

    cv::Mat tmpMat, monoMat, ROV, tmpMat1;    // matrices for image computations -> single eye
    cv::Mat tmpMat_r, tmpMat_l, monoMat_r, monoMat_l, ROV_r, ROV_l, tmpMat1_r, tmpMat1_l;    // matrices for image computations -> both eye
    int new_type;    // store CV data type for images -> single/double precision

    /** yarp ports **/
    std::string client_port_prefix;                                                // client portame prefix
    std::string robot_port_prefix;                                                 // robot portname prefix
    yarp::os::BufferedPort<yarp::sig::ImageOf<yarp::sig::PixelRgb>> port_right;    // port for the iCub right eye image
    yarp::os::BufferedPort<yarp::sig::ImageOf<yarp::sig::PixelRgb>> port_left;     // port for the iCub left eye image

    /** grpc communication **/
#ifdef _USE_GRPC
    std::string _ip_address = "";    // gRPC server ip address
    unsigned int _port = -1;         // gRPC server port
    ServerInstance *image_source;    // gRPC server instance
    std::thread server_thread;       // thread for running the gRPC server in parallel
#endif

    /*** auxilary methods ***/
    //
    std::vector<precision> ProcessRead();
    // convert field of view horizontal degree position to horizontal pixel position
    double FovX2PixelX(double fx);
    // convert field of view vertical degree position to vertical pixel position
    double FovY2PixelY(double fy);
    // convert a 2D-matrix to 1D-vector
    std::vector<precision> Mat2Vec(cv::Mat matrix);
};
