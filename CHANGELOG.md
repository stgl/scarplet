### Log for `scarplet-python` and `scarp-reduce` project

Date            | Description
--------------- | -----------
October 2018    | Packaging for alpha realease via PyPI
6 October 2017  | EarthScope NorCal dataset processed and available on S3 
22 September 2017 | Tests with EarthScope data complete
12 September 2017 | Synthetic testing, Carrizo testing, benchmarking complete
July 2017    | Abandoned Celery for dedicated Match/Reduce instances using shared filesystem
30 June 2017 | Testing Celery framework
29 June 2017 | Update AMI with optimized linear algebra libs (tried ATLAS and OpenBLAS)
25-29 June 2017 | Benchmarking and develop worker classes for autoscaling
23-24 June 2017 | Started framework for worker management
22 June 2017    | Finished implementing basic parallel grid search functionality 
15 May 2017     | Added download utility for OpenTopography data
12 May 2017     | Template and parameter search pass synthetic tests

A slippy map for browsing tiles will be up soon!

To download tiles of results as 4 band rasters (1 = amplitude, 2 = relative age, 3 = orientation, 4 = SNR), get the files from an S3 bucket:

[https://s3-us-west-2.amazonaws.com/scarp-ot-ncal-scale/fgxxx_yyyy_results.tif](https://s3-us-west-2.amazonaws.com/scarp-ot-ncal-\<scale\>/fg<xxx>_<yyyy>_results.tif)

where "scale" is 100, 500, or 1000 (meters), and "xxx", "yyyy" refer to the most significant digits of the UTM coordinates of the tile lower left corner.

### TODO
(See issue tracker for all tasks related to scarplet project)

#### Core functionality
- [x] Clean up utilities and remove unused functions
- [ ] Port old GDAL code to `rasterio` in `dem.py` classes
- [ ] Improve nodata interpolation to reduce artifacts in x, y directions (i.e. write taperied interpolation method rather than using `rasterio.fill`)

#### Extra
- [ ] Add cleaned-up script for post-processing to remove artifacts
- [ ] Non-maximum supression
- [x] More templates!

#### Tests
- [ ] Increase test coverage for WindowedTemplate
- [x] Stop skipping tests, add small testing data to repo
