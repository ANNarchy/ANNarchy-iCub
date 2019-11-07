#pragma once

#include <queue>
#include <string>

#include <opencv2/opencv.hpp>

#include <yarp/os/all.h>
#include <yarp/sig/all.h>


class Visual_Reader : private yarp::os::RFModule
{
  public:
    Visual_Reader();
    ~Visual_Reader();

    // init Visual reader with given parameters for image resolution, field of view and eye selection
    bool init(char eye, double fov_width, double fov_height, int img_width, int img_height);
    // start reading images from the iCub with YARP-RFModule
    void start(int argc, char *argv[]);
    // stop reading images from the iCub, by terminating the RFModule
    void stop();
    // read image vector from the image buffer and remove it from the buffer
    std::vector<double> read_fromBuf();

  private:
    bool dev_init = false; // variable for initialization check
    char act_eye;          // selected iCub eye to read images from

    // fix iCub-visual data //
    const int icub_width = 320;   // iCub image width in pixel
    const int icub_height = 240;  // iCub image height in pixel
    const double icub_fov_x = 60; // iCub field of view horizontal in degree
    const double icub_fov_y = 48; // iCub field of view vertical in degree

    int out_fov_x_up, out_fov_x_low; // pixel borders for horizontal field of view in the iCub image
    int out_fov_y_up, out_fov_y_low; // pixel borders for vertical field of view in the iCub image
    int ROV_width;                   // image width for given horizontal field of view (ROV, region of view)
    int ROV_height;                  // image height for given vertical field of view (ROV, region of view)

    int out_width;  // output image width in pixel
    int out_height; // output image height in pixel

    double res_scale_x; // scaling factor in x direction to scale ROV to ouput image width
    double res_scale_y; // scaling factor in y direction to scale ROV to ouput image height

    std::queue<std::vector<double>> img_buffer[30]; // buffer to store the preprocessed iCub images

    yarp::os::BufferedPort<yarp::sig::ImageOf<yarp::sig::PixelRgb>> PortRight; // port for the iCub right eye image
    yarp::os::BufferedPort<yarp::sig::ImageOf<yarp::sig::PixelRgb>> PortLeft;  // port for the iCub left eye image

    // functions for the YARP-RFModule //
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

    // auxilary functions //
    // check if init function was called
    bool check_init();
    // convert field of view horizontal degree position to horizontal pixel position
    double fov_x2pixel_x(double fx);
    // convert field of view vertical degree position to vertical pixel position
    double fov_y2pixel_y(double fy);
    // convert a 2D-matrix to 1D-vector
    std::vector<int> mat2vec(cv::Mat matrix);
};
