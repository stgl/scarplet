# scarplet-python
Python framework for template matching to detect fault scarps in ALSM data. Very much a work in progress, not for general consumption yet.

### Features
This repository implements a framework for windowed template matching in Python. Two-dimensional windowed template functions at a range of orientations are convolved with input data, and the best-fitting (highest signal-to-noise ratio) template parameters are retained at each pixel.

It works on georeferenced digital elevation models using a curvature-based template functions. A template for scarp-like features is provided, based on work by Hilley, *et al.*, 2010, Hanks, 2000, and many others. This returns best-fitting scarp height, relative age, orientation, and SNR at each DEM pixel.

For scarps, the approach is similar to the Canny edge detector or derivative of Gaussians method. The classes provided can handle other template functions as well (to be implemented).


### Changelog

Date            | Description
--------------- | -----------
6 October 2017  | EarthScope NorCal dataset processed and available on S3
22 September 2017 | Tests with EarthScope data complete
12 September 2017 | Synthetic testing, Carrizo testing, benchmarking complete
July 2017    | Abandoned Celery for dedicated Match/Reduce instances using shared filesystem
30 June 2017 | Testing Celery framework
29 June 2017 | Update AMI with optimized linear algebra libs
25-29 June 2017 | Benchmarking and develop worker classes for autoscaling
23-24 June 2017 | Started framework for worker management
22 June 2017    | Finished implementing basic parallel grid search functionality 
15 May 2017     | Added download utility for OpenTopography data
12 May 2017     | Template and parameter search pass synthetic tests

### TODO
(See issue tracker for all tasks related to scarplet project)

- Port GDAL code to `rasterio` in `dem.py` classes
- Improve nodata interpolation to reduce artifacts in x, y directions (i.e. write taperied interpolation method rather than using `rasterio.fill`)
- Add cleaned-up script for post-processing to remove artifacts
- Non-maximum supression
- Increase test coverage
