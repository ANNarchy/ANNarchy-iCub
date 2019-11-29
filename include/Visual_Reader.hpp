/*
 *  Copyright (C) 2019 Torsten Follak
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
#include <string>
#include <vector>

#include <opencv2/opencv.hpp>

class VisualReader : private yarp::os::RFModule {
    typedef double precision;

 public:
    VisualReader() = default;
    ~VisualReader();

    /*** public methods for the user ***/
    // init Visual reader with given parameters for image resolution, field of view and eye selection
    bool Init(char eye, double fov_width, double fov_height, int img_width, int img_height, bool fast_filter);
    // start reading images from the iCub with YARP-RFModule
    bool Start(int argc, char *argv[]);
    // stop reading images from the iCub, by terminating the RFModule
    void Stop();
    // read image vector from the image buffer and remove it from the buffer
    std::vector<precision> ReadFromBuf();

 private:
    /** configuration variables **/
    bool dev_init = false;               // variable for initialization check
    static const int buffer_len = 30;    // length of the image buffer

    char act_eye;           // selected iCub eye to read images from
    int filter_ds;          // filter for the upscaling of the image
    bool cut_img;           // flag, being true if a part of the field of view is cutted of the image
    precision norm_fact;    // norming factor for the normalization of the image

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
    std::deque<std::vector<precision>> img_buffer[buffer_len];    // buffer to store the preprocessed iCub images

    yarp::os::BufferedPort<yarp::sig::ImageOf<yarp::sig::PixelRgb>> port_right;    // port for the iCub right eye image
    yarp::os::BufferedPort<yarp::sig::ImageOf<yarp::sig::PixelRgb>> port_left;     // port for the iCub left eye image

    yarp::sig::ImageOf<yarp::sig::PixelRgb> *iEyeRgb;
    cv::Mat tmpMat, monoMat, ROV;
    cv::Mat tmpMat1;
    int new_type;

    /*** methods for the YARP-RFModule ***/
    // configure RFModule
    bool configure(yarp::os::ResourceFinder &rf) override;
    // RFModule update function, is called when the module is running, load images from the iCub
    bool updateModule() override;
    // called when the RFModule ist interrupted
    bool interruptModule() override;
    // get calling period of updateModule
    double getPeriod() override;
    // called when the module ist terminated
    bool close() override;

    /*** auxilary methods ***/
    // check if init function was called
    bool CheckInit();
    // convert field of view horizontal degree position to horizontal pixel position
    double FovX2PixelX(double fx);
    // convert field of view vertical degree position to vertical pixel position
    double FovY2PixelY(double fy);
    // convert a 2D-matrix to 1D-vector
    std::vector<precision> Mat2Vec(cv::Mat matrix);
};
