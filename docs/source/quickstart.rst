Getting started with scarplet
=============================

Currently ``scarplet`` handles input data in GeoTiff format. Get a copy of your
elevation data as a GeoTiff, and you can load it as

.. code-block:: python

   import scarplet as sl
   data = sl.load('mydem.tif')


If you have gaps in your DEM, no data values will automatically be filled. Then
you are ready to choose a template and fit it to your data. These are defined
as classes in the WindowedTemplate submodule.

For example, to use a vertical scarp template, you would import the appropiate 
template and define a scale and orientation parameters. In this case, +/- 90
degrees from vertical (*x* direction) caputres all scarp orientations.

.. code-block:: python

   import numpy as np
   from scarplet.WindowedTemplate import Scarp
   params = {'scale': 100, 'ang_min': -np.pi / 2, 'ang_max': np.pi / 2}


Then, ``scarplet``'s ``match`` function will search over all parameters and return
the best-fitting height, relative age, and orientation at each DEM pixel.

.. code-block:: python

   res = sl.match(data, Scarp, **params)
   sl.plot_results(data, res)

