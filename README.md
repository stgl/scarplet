# scarplet

A Python package for template matching to detect fault scarps and other
landforms in digital elevation data.

It was designed with two main goals:
    - Allow contributors to easily extend the method to other landforms by defining their own template functions
    - Make it straightforward to deploy matching tasks in parallel using [dask]() or other tools

<p align='center'><img src=https://github.com/rmsare/scarplet/raw/master/data/northcoast.png width="640px"></p>

**Signal-to-noise ratio of scarp-like landforms.** a) Swath of elevation data along the northern San Andreas Fault, CA, USA, b) Mapping from the USGS Quaternary faults and folds database, c) Successful and unsuccessful detections by the scarplet methodology.

## Features

## Getting started

### Installation

`scarplet` can be installed with PyPI.

```
pip install scarplet
```

### Examples

#### Detecting fault scarps

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

<img src="docs/img/carrizo_example.png" alt="Fault scarp results" height="600">

#### Extracting confined river channels

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

<img src="docs/img/rivers_example.png" alt="Channel results" height="600">

There are also [example notebooks]() in the documentation.

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

If you would like to add a feature or fix a bug, please [submit a PR](https://github.com/rmsare/scarplet/compare)
and reference any relevant issues.

### Support and questions

Please [open an issue](https://github.com/rmsare/scarplet/issues/new) with your question.

## References
- Hanks, T.C., 2000. The age of scarplike landforms from diffusion‐equation analysis. Quaternary Geochronology, 4, pp.313-338. [doi](https://doi.org/10.1029/RF004p0313)
- Hilley, G.E., DeLong, S., Prentice, C., Blisniuk, K. and Arrowsmith, J.R., 2010. Morphologic dating of fault scarps using airborne laser swath mapping (ALSM) data. Geophysical Research Letters, 37(4). [doi](https://doi.org/10.1029/2009GL042044)

## License
This work is licensed under the MIT License (see [LICENSE](LICENSE)).
