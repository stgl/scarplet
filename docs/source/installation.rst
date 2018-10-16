Installation
============

``scarplet`` is on PyPI. You can install it with

.. code-block:: bash

   pip install scarplet 

The main dependencies are:

* NumPy
* Numexpr
* GDAL and Rasterio
* PyFFTW
* SciPy

Installing GDAL
===============

GDAL and ``python-gdal`` are notoriously tricky to install. Hopefully your system
has GDAL installed already; if not, you can install using your OS' package
manager.

For example, on Ubuntu or Debian,

.. code-block:: bash
   
   sudo apt-get install gdal libgdal1h gdal-bin

Or, on OS X,

.. code-block:: bash

   brew install gdal

Then, the Python bindings to GDAL can be installed. Typically this is as 
simple as

.. code-block:: bash

   pip install gdal

but you may find that the compiler can't find the GDAL header files. Usually
this will give a an error like ``fatal error: cpl_vsi_error.h: No such file or
directory``. To get around this, we need to pass the include path to ``pip``:

.. code-block:: bash

   pip install gdal --global-option=build_ext --global-option="-I/usr/include/gdal/"

or

.. code-block:: bash

   pip install gdal==$(gdal-config --version) --global-option=build_ext --global-option="-I/usr/include/gdal/"

In my case, with GDAL 1.11.2, this is

.. code-block:: bash

   pip install gdal==1.11.2 --global-option=build_ext --global-option="-I/usr/include/gdal/"

Once GDAL is installed, you can go ahead and install the package as usual

.. code-block:: bash

   pip install scarplet 
