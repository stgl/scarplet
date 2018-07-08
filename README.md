# scarplet
Python framework for template matching to detect fault scarps and other landforms in digital elevation data.

### Features
This repository implements a windowed template matching algorithm in Python. Two-dimensional windowed template functions with a range of plan-view orientations are convolved with input data, and the best-fitting (highest signal-to-noise ratio) template parameters are retained at each pixel. 

The algorithm works on georeferenced digital elevation models using curvature-based template functions. A template for fault scarps is provided, based on work by Hilley, *et al.*, 2010, Hanks, 2000, and many others. This returns best-fitting scarp height, relative age, orientation, and SNR at each DEM pixel. It detects scarp-like features as areas of high SNR and gives estimates of their relative age and height.

For the scarp template, this approach is similar to the Canny edge detector or derivative of Gaussians method. In 1D, the template is the derivative of a Gaussian function (the slope profile of the model scarp). The parameter search is over 2D template orientation and template function variance. These correspond to the plan-view orientation of a linear scarp, and the "smoothness"/maturity of the scarp in profile. 

The classes provided can handle other template functions as well (to be implemented).
