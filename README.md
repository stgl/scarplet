# scarplet
A Python framework for template matching to detect fault scarps and other landforms in digital elevation data. Still a work in progress! 

The [scarp-reduce](https://github.com/rmsare/scarp-reduce) repo contains basic task management scripts to run this in distributed mode on AWS.

<p align='center'><img src=https://github.com/rmsare/scarplet/raw/master/data/northcoast.png width="640px"></p>

**Signal-to-noise ratio of scarp-like landforms.** a) Swath of elevation data along the northern San Andreas Fault, CA, USA, b) Mapping from the USGS Quaternary faults and folds database, c) Successful and unsuccessful detections by the scarplet methodology.

### Details
This repository implements a windowed template matching algorithm in Python. Two-dimensional windowed template functions with a range of plan-view orientations are convolved with input data, and the best-fitting (highest signal-to-noise ratio) template parameters are retained at each pixel. 

The algorithm works on georeferenced digital elevation models using curvature-based template functions. A template for fault scarps is provided, based on work by [Hilley, *et al.*, 2010](https://doi.org/10.1029/2009GL042044), [Hanks, 2000](https://doi.org/10.1029/RF004p0313), and many others. This returns best-fitting scarp height, relative age, orientation, and SNR at each DEM pixel. It detects scarp-like features as areas of high SNR and gives estimates of their relative age and height.

For the scarp template, this approach is similar to the Canny edge detector or derivative of Gaussians method. In 1D, the template is the derivative of a Gaussian function (the slope profile of the model scarp). The parameter search is over 2D template orientation and template function variance. These correspond to the plan-view orientation of a linear scarp, and the "smoothness"/maturity of the scarp in profile. 

The classes provided can handle other template functions as well (to be implemented).

### References
- Hanks, T.C., 2000. The age of scarplike landforms from diffusion‐equation analysis. Quaternary geochronology, 4, pp.313-338. [doi](https://doi.org/10.1029/RF004p0313)
- Hilley, G.E., DeLong, S., Prentice, C., Blisniuk, K. and Arrowsmith, J.R., 2010. Morphologic dating of fault scarps using airborne laser swath mapping (ALSM) data. Geophysical Research Letters, 37(4). [doi](https://doi.org/10.1029/2009GL042044)
