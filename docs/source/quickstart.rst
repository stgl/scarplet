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
template and define a scale and the orientation parameters. In this case, +/- 90
degrees from vertical (*y* direction) captures all scarp orientations.

.. code-block:: python

   import numpy as np
   from scarplet.WindowedTemplate import Scarp
   params = {'scale': 100, 'ang_min': -np.pi / 2, 'ang_max': np.pi / 2}


Then, ``scarplet``'s ``match`` function will search over all parameters and return
the best-fitting height, relative age, and orientation at each DEM pixel.

.. code-block:: python

   res = sl.match(data, Scarp, **params)
   sl.plot_results(data, res)

All results are returned as *4* x *n* x *m* arrays of height/amplitude, relative age,
orientation, and signal-to-noise-ratio. The easiest way to work with these is 
to unpack the results and manipulate them as NumPy arrays

.. code-block:: python

   import matplotlib.pyplot as plt
   amp, age, angle, snr = res

   fig, ax = plt.subplots(2, 1)
   ax[0].hist(np.log10(age), bins=10)
   ax[0].set_xlabel('Morphologic age [m$^2$]')
   
   ax[1].hist(angle * 180 / np.pi, nbins=19)
   ax[1].set_xlabel('Orientation [deg.]')
