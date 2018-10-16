# scarplet


[![Build Status](https://travis-ci.com/rmsare/scarplet.svg?branch=master)](https://travis-ci.com/rmsare/scarplet)

A Python package for applying template matching techniques to digital elevation data, in
particular for detecting and measuring the maturity of fault scarps and other
landforms [[0, 1]](#references)

It was designed with two main goals:

* Allow contributors to define template functions for their problem area of interest
* Make it straightforward to apply these methods to large datasets by parallelizing/distrbuting computation using multiprocessing, [dask](https://dask.readthedocs.io), or other tools [[2]](#references)

## Getting started

### Installation

`scarplet` can be installed from PyPI.

```bash
pip install scarplet
```

or

```bash
$ virtualenv myenv
$ source myenv/bin/activate
(myenv) $ pip install scarplet
```

On some systems, GDAL will fail to install because headers are not found within
the virtual environment. In this case, install GDAL first, then other packages.

```bash
$ virtualenv myenv
$ source myenv/bin/activate
(myenv) $ pip install gdal==<VERSION> --global-option=build_ext --global-option='-I/usr/include/gdal/'
(myenv) $ pip install scarplet
```

where `<VERSION>` is your GDAL version (e.g., `1.11.2`, see `gdal-config --version`).

## Examples

### Detecting fault scarps

```python
import numpy as np
import scarplet as sl
from scarplet.WindowedTemplate import Scarp

params = {'scale': 100,
          'age': 10,
          'ang_min': -10 * np.pi / 2,
          'ang_max': 10 * np.pi / 2
         }

data = sl.load('data/faultzone.tif')
res = sl.match(data, Scarp, **params)

sl.plot_results(data, res)
```

<img src="docs/img/carrizo_example.png" alt="Fault scarp results" height="320">

### Extracting confined river channels

```python
import numpy as np
import scarplet as sl
from scarplet.WindowedTemplate import Channel 

params = {'scale': 10,
          'age': 10,
          'ang_min': -np.pi / 2,
          'ang_max': np.pi / 2
         }

data = sl.load('data/channelnetwork.tif')
res = sl.match(data, Channel, **params)

sl.plot_results(data, res)
```

<img src="docs/img/rivers_example.png" alt="Channel results" height="320">

There are also [example notebooks](https://scarplet.readthedocs.io/en/latest/index.html) in the documentation.

## Documentation

Read the documentation for example use cases, an API reference, and more. They
are hosted at [scarplet.readthedocs.io](https://scarplet.readthedocs.io).

## Contributing

### Bug reports

Bug reports are much appreciated. Please [open an issue](https://github.com/rmsare/scarplet/issues/new) with the `bug` label,
and provide a minimal example illustrating the problem.

### Suggestions

Feel free to [suggest new features](https://github.com/rmsare/scarplet/issues/new) in an issue with the `new-feature` label.

### Pull requests

Don't hestiate to file an issue; I would be happy to discuss extensions or help to build a new feature. 

If you would like to add a feature or fix a bug, please fork the repository, create a feature branch, and [submit a PR](https://github.com/rmsare/scarplet/compare) and reference any relevant issues. There are nice guides to contributing with GitHub [here](https://akrabat.com/the-beginners-guide-to-contributing-to-a-github-project/) and [here](https://yourfirstpr.github.io/). Please include tests where appropriate and check that the test suite passes (a Travis build or `pytest scarplet/tests`) before submitting.


### Support and questions

Please [open an issue](https://github.com/rmsare/scarplet/issues/new) with your question.

## References
[0] Hanks, T.C., 2000. The age of scarplike landforms from diffusion‐equation analysis. Quaternary Geochronology, 4, pp. 313-338. [doi](https://doi.org/10.1029/RF004p0313)

[1] Hilley, G.E., DeLong, S., Prentice, C., Blisniuk, K. and Arrowsmith, J.R., 2010. Morphologic dating of fault scarps using airborne laser swath mapping (ALSM) data. Geophysical Research Letters, 37(4). [doi](https://doi.org/10.1029/2009GL042044)

[2] Sare, R, Hilley, G. E., and DeLong, S. B., 2018, Regional scale detection of fault scarps and other tectonic landforms: Examples from Northern California, submitted to Journal of Geophysical Research: Solid Earth.

## License
This work is licensed under the MIT License (see [LICENSE](LICENSE)).
