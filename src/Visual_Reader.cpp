/*
 *  Copyright (C) 2019 Torsten Follak
 *
 *  Visual_Reader.cpp is part of the iCub ANNarchy interface
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

#include <iostream>
#include <queue>
#include <string>

#include <opencv2/opencv.hpp>

#include <yarp/cv/Cv.h>
#include <yarp/dev/all.h>
#include <yarp/os/all.h>
#include <yarp/sig/all.h>

#include "Visual_Reader.hpp"

#include <chrono>
typedef std::chrono::high_resolution_clock Clock;


// Constructor
Visual_Reader::Visual_Reader() {}

// Destructor
Visual_Reader::~Visual_Reader() {}

// init Visual reader with given parameters for image resolution, field of view and eye selection
bool Visual_Reader::Init(char eye, double fov_width, double fov_height, int img_width, int img_height)
/*
    params: char eye            -- characteer representing the selected eye (l/L; r/R)
            double fov_width    -- output field of view width in degree [0, 60] (input fov width: 60°)
            double fov_height   -- output field of view height in degree [0, 48] (input fov height: 48°)
            int img_width       -- output image width in pixel (input width: 320px)
            int img_height      -- output image height in pixel (input height: 240px)

    return: bool                -- return True, if successful
*/
{
    if (!dev_init)
        {
            // set ouput image size
            out_width = img_width;
            out_height = img_height;

            // compute output field of view borders in input image
            if (fov_width <= icub_fov_x)
                {
                    out_fov_x_low = static_cast<int>(ceil(FovX2PixelX(-fov_width / 2.0)));
                    out_fov_x_up = static_cast<int>(floor(FovX2PixelX(fov_width / 2.0)));
                }
            else
                {
                    std::cerr << "[Visual Reader] Selected field of view width is out of range" << std::endl;
                    return false;
                }

            if (fov_height <= icub_fov_y)
                {
                    out_fov_y_low = static_cast<int>(ceil(FovY2PixelY(fov_height / 2.0)));
                    out_fov_y_up = static_cast<int>(floor(FovY2PixelY(-fov_height / 2.0)));
                }
            else
                {
                    std::cerr << "[Visual Reader] Selected field of view height is out of range" << std::endl;
                    return false;
                }

            // calculate output region of view (ROV) (image part equivalent to output field of view)
            rov_width = out_fov_x_up - out_fov_x_low;
            rov_height = out_fov_y_up - out_fov_y_low;

            // calculate scaling factors to scale ROV to output image size
            res_scale_x = ((double)(out_width)) / (rov_width);
            res_scale_y = ((double)(out_height)) / (rov_height);

            // init YARP-Network
            yarp::os::Network::init();
            if (!yarp::os::Network::checkNetwork())
                {
                    std::cerr << "[Visual Reader] YARP Network is not online. Check nameserver is running" << std::endl;
                    return false;
                }

            // open and connect YARP port for the chosen eye
            // right eye chosen
            if (eye == 'r' || eye == 'R')
                {
                    act_eye = 'R';
                    std::string port_name = "/V_Reader/image/right:i";
                    port_right.open(port_name);
                    if (!yarp::os::Network::connect("/icubSim/cam/right", port_name.c_str()))
                        {
                            return false;
                        }
                }
            // left eye chosen
            if (eye == 'l' || eye == 'L')
                {
                    act_eye = 'L';
                    std::string port_name = "/V_Reader/image/left:i";
                    port_left.open(port_name);
                    if (!yarp::os::Network::connect("/icubSim/cam/left", port_name.c_str()))
                        {
                            return false;
                        }
                }
            dev_init = true;
            return true;
        }
    else
        {
            std::cerr << "[Visual Reader] Initialization aready done!" << std::endl;
            return false;
        }
}

// check if init function was called
bool Visual_Reader::CheckInit()
{
    if (!dev_init)
        {
            std::cerr << "[Visual Reader] Error: Device is not initialized" << std::endl;
            return false;
        }
    else
        {
            return true;
        }
}

// read image vector from the image buffer and remove from the buffer
std::vector<double> Visual_Reader::ReadFromBuf()
/*
    return: std::vector<double>     -- image (1D-vector) from the image buffer
*/
{
    if (CheckInit())
        {
            // if image buffer is not empty return the image and delete it from the buffer
            std::vector<double> img;
            if (img_buffer->empty())
                {
                    printf("[Visual Reader] The image buffer is empty \n");
                }
            else
                {
                    img = img_buffer->front();
                    img_buffer->pop();
                }
            return img;
        }
    else
        {
            std::vector<double> empty;
            return empty;
        }
}

// start reading images from the iCub with YARP-RFModule
void Visual_Reader::Start(int argc, char *argv[])
/*
    params: int argc, char *argv[]  -- main function inputs from program call; can be used to configure RFModule; not implemented yet
*/
{
    if (CheckInit())
        {
            // configure YARP-RessourceFinder and start RFModule as seperate Thread
            yarp::os::ResourceFinder rf;
            rf.configure(argc, argv);

            runModuleThreaded(rf);
        }
}

// stop reading images from the iCub, by terminating the RFModule
void Visual_Reader::Stop()
{
    if (CheckInit())
        {
            // stop and close RFModule
            stopModule(true);
            close();
        }
}

// configure YARP-RFModule
bool Visual_Reader::configure(yarp::os::ResourceFinder &rf)
/*
    params: yarp::os::ResourceFinder &rf  -- YARP ResourceFinder can be used to configure variables from e.g. ini-file

    return: bool                          -- return True, if successful
*/
{
    // empty, because anything is configured in init(); needed for RFMoule
    return true;
}

// get calling period of updateModule
double Visual_Reader::getPeriod()
/*
    return: double      -- period for calling updateModule
*/
{
    // 0.0 to synchronize with incoming images
    return 0.0;
}

// YARP-RFModule update function, is called when the module is running, load images from the iCub
bool Visual_Reader::updateModule()
/*
    return: bool      -- return True, if successful
*/
{
    auto t1 = Clock::now();

    // read image from the iCub and get CV-Matrix
    yarp::sig::ImageOf<yarp::sig::PixelRgb> *iEyeRgb;
    if (act_eye == 'L')
        {
            iEyeRgb = port_left.read();
        }
    if (act_eye == 'R')
        {
            iEyeRgb = port_right.read();
        }

    cv::Mat RgbMat = yarp::cv::toCvMat(*iEyeRgb);

    // convert rgb image to grayscale image
    cv::Mat tmpMat, monoMat;
    cv::cvtColor(RgbMat, tmpMat, cv::COLOR_RGB2GRAY);

    // extracting the output part of the field of view
    cv::Mat ROV = tmpMat(cv::Rect(out_fov_x_low, out_fov_y_low, rov_width, rov_height)).clone();

    // resize ROV to given output resolution
    if (res_scale_x == 1 && res_scale_x == 1)
        {
            monoMat = ROV;
        }
    else if (res_scale_x < 1 || res_scale_x < 1)
        {
            cv::resize(ROV, monoMat, cv::Size(), res_scale_x, res_scale_y, cv::INTER_AREA);
        }
    else
        {
            cv::resize(ROV, monoMat, cv::Size(), res_scale_x, res_scale_y, cv::INTER_LINEAR);
        }

    // flat the image matrix to 1D-vector
    std::vector<int> img_vector = Mat2Vec(monoMat);

    // normalize the image from 0..255 to 0..1
    std::vector<double> img_vec_norm(img_vector.size());
    for (int i = 0; i < img_vector.size(); i++)
        {
            img_vec_norm[i] = (static_cast<double>(img_vector[i]) / 255.0);
        }

    // store image in the buffer
    img_buffer->push(img_vec_norm);

    auto t2 = Clock::now();
    std::cout << "[Visual Reader] Load image in: " << std::chrono::duration_cast<std::chrono::milliseconds>(t2 - t1).count() << " ms"
              << std::endl;

    return true;
}

// called when interrupting/stopping the YARP-RFModule
bool Visual_Reader::interruptModule()
/*
    return: bool      -- return True, if successful
*/
{
    // interrupt port communication
    if (act_eye == 'L')
        {
            port_left.interrupt();
        }
    if (act_eye == 'R')
        {
            port_right.interrupt();
        }
    return true;
}

// closes used Network parts; called by the YARP-RFModule when it is terminating
bool Visual_Reader::close()
/*
    return: bool      -- return True, if successful
*/
{
    // disconnect and close left eye port
    if (!port_left.isClosed())
        {
            yarp::os::Network::disconnect("/icubSim/cam/left", "/V_Reader/image/left:i");
            port_left.close();
        }

    // disconnect and close right eye port
    if (!port_right.isClosed())
        {
            yarp::os::Network::disconnect("/icubSim/cam/right", "/V_Reader/image/right:i");
            port_right.close();
        }

    // close YARP Network
    yarp::os::Network::fini();
    return true;
}

// convert field of view horizontal degree position to horizontal pixel position
double Visual_Reader::FovX2PixelX(double fx)
/*
    params: double fx   -- horizontal field of view position in degree

    return: double      -- horizontal field of view position in pixel
*/
{
    double pixel;
    // conversion function retrieved from measured data
    pixel = 0.0006 * pow(fx, 3) + 4.8056 * fx + 160;
    return pixel;
}

// convert field of view vertical degree position to vertical pixel position
double Visual_Reader::FovY2PixelY(double fy)
/*
    params: double fy   -- vertical field of view position in degree

    return: double      -- vertical field of view position in pixel
*/
{
    double pixel;
    // conversion function retrieved from measured data
    pixel = -0.0005 * pow(fy, 3) + 0.0005 * pow(fy, 2) - 4.7269 * fy + 120.0;
    return pixel;
}

// convert a 2D-matrix to 1D-vector
std::vector<int> Visual_Reader::Mat2Vec(cv::Mat matrix)
/*
    params: cv::Mat matrix    -- image as 2D-matrix

    return: std::vector<int>  -- image as 1D-vector
*/
{
    std::vector<int> vec;
    // convert a 2D-matrix to 1D-vector, distinguish to cases with different methods
    if (matrix.isContinuous()) // faster, only possible when data continous in memory
        {
            vec.assign(matrix.data, matrix.data + matrix.total());
        }
    else // slower, always possible
        {
            for (int i = 0; i < matrix.rows; ++i)
                {
                    vec.insert(vec.end(), matrix.ptr<int>(i), matrix.ptr<int>(i) + matrix.cols);
                }
        }
    return vec;
}
