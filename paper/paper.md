---
title: 'Scarplet: A Python package for topographic template matching and diffusion dating'
tags:
  - Python
  - geomorphology
  - topographic analysis
  - image processing
  - diffusion dating
authors:
  - name: Robert Sare
    orcid: 0000-0003-3711-6771
    affiliation: 1
  - name: George Hilley
    orcid: 0000-0002-1761-7547
    affiliation: 1
affiliations:
  - name: Department of Geological Sciences, Stanford University
    index: 1          
date: 11 October 2018
bibliography: paper.bib
---

# Summary

Detection and analysis of landforms is a major problem in geoscience, including
identifying and measuring the relative ages of earthquake fault scarps. Inverse 
methods using the diffusion equation have been applied to relatively date a wide range of landforms, 
including scarps (@hanks2000, @hilley2010), terraces (@avouac1993), 
and impact craters (@fassett2014). Size (height) and relative age estimates from
these techniques provide important contraints where instrumental or historic data
may be sparse: for example, in a fault zone with a limited record of historic 
seismicity. Similar wavelet-based methods are widely used in geophysics and 
channel network analysis as feature extraction techniques (@lashermes2007; @passalacqua2010).

The ``scarplet`` package provides a set of tools for performing feature
detection and diffusion dating using user-defined landform templates.
The package contains several template functions implemented for vertical scarp
dating as well as a crater template and common functions such as the Ricker 
wavelet. As the template matching approach can exploit simple map-reduce 
parallelism, it can be efficiently applied to large datasets in a distributed 
manner.

The core algorithms of ``scarplet`` use standard signal processing 
tools in the scientific Python ecosystem, and the basic ``WindowedTemplate`` 
classes used by these methods are easy to extend. The intent is to provide a 
quick, scalable option for topographic data analysis and template function 
prototyping which can be adapted by users familiar with NumPy and SciPy. As availability of
digital topographic data from airborne and satellite sources grows, tools like this
will help to enable quantitiative geomorphology on regional and global scales and
complement Python-based modelling packages such as LandLab (@hobley2017).

# References

