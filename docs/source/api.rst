API Reference
=============

This package is structured so that most functions are implemented in a ``core``
submodule and templates are defined as subclasses of ``WindowedTemplate`` in the
``WindowedTemplate`` submodule. Spatial data and I/O is handled by classes 
defined in ``dem``.

Core functionality
------------------

.. toctree::
   :maxdepth: 2

   scarplet.core

Templates
---------

.. toctree::
   :maxdepth: 2

   scarplet.WindowedTemplate

Data and IO
-----------

.. toctree::
   :maxdepth: 2

   scarplet.dem
   scarplet.datasets
