.. Scarplet documentation master file, created by
   sphinx-quickstart on Thu Oct 11 17:00:08 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

scarplet: A Python package for topographic template matching
============================================================

``scarplet`` is a tool for topographic feature detection and diffusion or
degradation dating. It allows users to define template functions based on the
curvature of a landform, and fit them to digital elevation data. As a package,
it provides

* A scalable template matching algorithm with ``match`` and ``compare`` operations
* A ``Scarp`` template for fault scarp diffusion dating, and templates for
  detecting river channels or impact craters
* Flexible template classes 

Contents
========

.. toctree::
   :maxdepth: 1
   :caption: Getting Started 
    
   installation
   quickstart

.. toctree::
   :maxdepth: 1
   :caption: Examples
    
   examples/scarps.ipynb
   examples/channels.ipynb
   examples/multiprocessing_example.ipynb

.. toctree::
   :maxdepth: 1
   :caption: How to

   new_template

.. toctree::
   :maxdepth: 1
   :caption: API documentation

   api 

