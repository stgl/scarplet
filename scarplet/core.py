# -*- coding: utf-8
""" Functions for determining best-fit template parameters by convolution with
a grid """

import numexpr
import numpy as np
import multiprocessing as mp

import matplotlib
import matplotlib.pyplot as plt

import pyfftw
from pyfftw.interfaces.numpy_fft import fft2, ifft2, fftshift

from functools import partial

from scarplet.dem import DEMGrid


np.seterr(divide='ignore', invalid='ignore')

pyfftw.interfaces.cache.enable()


def calculate_amplitude(dem, Template, scale, age, angle):
    """Calculate amplitude and SNR of features using a template

    Parameters
    ----------
    dem : DEMGrid
        Grid object of elevation data
    Template : WindowedTemplate
        Class representing template function
    scale : float
        Scale of template function in DEM cell units
    age : float
        Age parameter for template function
    angle : float
        Orientation of template in radians

    Returns
    -------
    amp : np.array
        2-D array of amplitudes for each DEM pixel
    snr : np.array
        2-D array of signal-to-noise ratios for each DEM pixel
    """

    ny, nx = dem._griddata.shape
    de = dem._georef_info.dx
    t = Template(scale, age, angle, nx, ny, de)
    template = t.template()

    curv = dem._calculate_directional_laplacian(angle)

    amp, age, angle, snr = match_template(curv, template)
    mask = t.get_window_limits()
    amp[mask] = 0
    snr[mask] = 0

    return amp, snr


def calculate_best_fit_parameters_serial(dem,
                                         Template,
                                         scale,
                                         ang_max=np.pi / 2,
                                         ang_min=-np.pi / 2,
                                         **kwargs):
    """Calculate best-fitting parameters using a template

    Parameters
    ----------
    dem : DEMGrid
        Grid object of elevation data
    Template : WindowedTemplate
        Class representing template function
    scale : float
        Scale of template function in DEM cell units

    Other Parameters
    ----------------
    ang_max : float, optional
        Maximum orietnation of template, default pi / 2
    ang_min : float, optional
        Minimum orietnation of template, default -pi / 2
    kwargs : optional
        Any additional keyword arguments that may be passed to the template()
        method of the Template class

    Returns
    -------
    best_amp : np.array
        2-D array of best-fitting amplitudes for each DEM pixel
    best_age : np.array
        2-D array of best-fitting agees for each DEM pixel
    best_angle : np.array
        2-D array of best-fitting orientations for each DEM pixel
    best_snr : np.array
        2-D array of maximum signal-to-noise ratios for each DEM pixel
    """

    ang_stepsize = 1
    num_angles = int((180 / np.pi) * (ang_max - ang_min) / ang_stepsize + 1)
    orientations = np.linspace(ang_min, ang_max, num_angles)
    ages = 10 ** np.arange(0, 3.5, 0.1)

    ny, nx = dem._griddata.shape
    best_amp = np.zeros((ny, nx))
    best_angle = np.zeros((ny, nx))
    best_age = np.zeros((ny, nx))
    best_snr = np.zeros((ny, nx))

    for this_angle in orientations:
        for this_age in ages:
            this_amp, this_age, this_angle, this_snr = match_template(dem,
                                                                      Template,
                                                                      scale,
                                                                      this_age,
                                                                      this_angle,
                                                                      **kwargs)

            best_amp = numexpr.evaluate("(best_snr > this_snr)*best_amp + \
                                        (best_snr < this_snr)*this_amp")

            best_angle = numexpr.evaluate("(best_snr > this_snr)*best_angle + \
                                          (best_snr < this_snr)*this_angle")

            best_age = numexpr.evaluate("(best_snr > this_snr)*best_age + \
                                        (best_snr < this_snr)*this_age")

            best_snr = numexpr.evaluate("(best_snr > this_snr)*best_snr + \
                                        (best_snr < this_snr)*this_snr")

    return best_amp, best_age, best_angle, best_snr


def calculate_best_fit_parameters(dem,
                                  Template,
                                  scale,
                                  age,
                                  ang_max=np.pi / 2,
                                  ang_min=-np.pi / 2,
                                  **kwargs):
    """Calculate best-fitting parameters using a template with parallel search

    Parameters
    ----------
    dem : DEMGrid
        Grid object of elevation data
    Template : WindowedTemplate
        Class representing template function
    scale : float
        Scale of template function in DEM cell units
    age : float
        Age parameter for template function

    Other Parameters
    ----------------
    ang_max : float, optional
        Maximum orietnation of template, default pi / 2
    ang_min : float, optional
        Minimum orietnation of template, default -pi / 2

    Returns
    -------
    results : np.array
        Array of best amplitudes, ages, orientations, and  signal-to-noise
        ratios for each DEM pixel. Dimensions of (4, height, width).
    """

    ang_stepsize = 1
    num_angles = int((180 / np.pi) * (ang_max - ang_min) / ang_stepsize + 1)
    orientations = np.linspace(ang_min, ang_max, num_angles)
    orientations = (angle for angle in orientations)

    ny, nx = dem._griddata.shape

    nprocs = mp.cpu_count()
    pool = mp.Pool(processes=nprocs)
    wrapper = partial(match_template, dem, Template, scale, age)
    results = pool.imap(wrapper, orientations, chunksize=1)

    best_amp, best_age, best_angle, best_snr = compare(results, ny, nx)

    pool.close()
    pool.join()

    results = np.stack([best_amp,
                        best_age,
                        best_angle,
                        best_snr])

    return results


def compare(results, ny, nx):
    """Compare template matching results from asynchronous tasks

    Parameters
    ----------
    results : iterable
        Iterable containing outputs of a template matching method
    ny : int
        Number of rows in output
    nx : int
        Number of columns in output

    Returns
    -------
    best_amp : np.array
        2-D array of best-fitting amplitudes
    best_angle : np.array
        2-D array of best-fitting orientations
    best_snr : np.array
        2-D array of maximum signal-to-noise ratios
    """

    best_amp = np.zeros((ny, nx))
    best_age = np.zeros((ny, nx))
    best_angle = np.zeros((ny, nx))
    best_snr = np.zeros((ny, nx))

    for r in results:
        this_amp, this_age, this_angle, this_snr = r

        best_amp = numexpr.evaluate("(best_snr > this_snr)*best_amp + \
                                    (best_snr < this_snr)*this_amp")

        best_age = numexpr.evaluate("(best_snr > this_snr)*best_age + \
                                    (best_snr < this_snr)*this_age")

        best_angle = numexpr.evaluate("(best_snr > this_snr)*best_angle + \
                                      (best_snr < this_snr)*this_angle")

        best_snr = numexpr.evaluate("(best_snr > this_snr)*best_snr + \
                                    (best_snr < this_snr)*this_snr")
        del this_amp, this_snr, r

    return best_amp, best_age, best_angle, best_snr


def load(filename):
    """Load DEM from file

    Parameters
    ----------
    filename : string
        Filename of DEM

    Returns
    -------
    data_obj : DEMGrid
        DEMGrid object with DEM data
    """

    data_obj = DEMGrid(filename)
    data_obj._fill_nodata()

    return data_obj


def match(data, Template, **kwargs):
    """Match template to input data from DEM

    Parameters
    ----------
    data : DEMGrid
        DEMGrid object containing input data
    Template : WindowedTemplate
        Class of template function to use

    Returns
    -------
    results : np.array
        Array of best amplitudes, ages, orientations, and  signal-to-noise
        ratios for each DEM pixel. Dimensions of (4, height, width).
    """
    
    if 'age' in kwargs:
        results = calculate_best_fit_parameters(data, Template, **kwargs)
    else:
        results = calculate_best_fit_parameters_serial(data, Template, **kwargs)

    return results


def match_template(data, Template, scale, age, angle, **kwargs):
    """Match template function to curvature using convolution

    Parameters
    ----------
    data : DEMGrid
        Grid object of elevation data
    Template : WindowedTemplate
        Class representing template function
    scale : float
        Scale of template function in DEM cell units
    age : float
        Age parameter for template function
    angle : float
        Orientation of template in radians

    Other Parameters
    ----------------
    kwargs : optional
        Any additional keyword arguments that may be passed to the template()
        method of the Template class

    Returns
    -------
    amp : np.array
        2-D array of amplitudes for each DEM pixel
    age : np.array
        template age in m2
    angle : np.array 
        template orientation in radians 
    snr : np.array
        2-D array of signal-to-noise ratios for each DEM pixel

    References
    ----------
    Modifies method described in 

    _[0] Hilley, G.E., DeLong, S., Prentice, C., Blisniuk, K. and Arrowsmith, 
         J.R., 2010. Morphologic dating of fault scarps using airborne 
         laser swath mapping (ALSM) data. Geophysical Research Letters, 37(4).
         https://dx.doi.org/10.1029/2009GL042044
    """

    eps = np.spacing(1)
    curv = data._calculate_directional_laplacian(angle)
    ny, nx = curv.shape
    de = data._georef_info.dx

    template_obj = Template(scale, age, angle, nx, ny, de, **kwargs)
    template = template_obj.template()

    M = numexpr.evaluate("template != 0")
    fm2 = fft2(M)
    n = np.sum(M) + eps
    del M

    fc = fft2(curv)
    ft = fft2(template)
    fc2 = fft2(numexpr.evaluate("curv**2"))
    template_sum = np.sum(numexpr.evaluate("template**2"))
    del curv, template

    xcorr = np.real(fftshift(ifft2(numexpr.evaluate("ft*fc"))))
    amp = numexpr.evaluate("xcorr/template_sum")

    T1 = numexpr.evaluate("template_sum*(amp**2)")
    T3 = fftshift(ifft2(numexpr.evaluate("fc2*fm2")))

    # XXX: Epsilon factor is added to avoid small-magnitude dvision
    error = (1/n)*numexpr.evaluate("real(T1 - 2*amp*xcorr + T3)") + eps
    snr = numexpr.evaluate("abs(T1/error)")

    if hasattr(template_obj, 'get_err_mask'):
        mask = template_obj.get_err_mask()
        snr[mask] = 0

    mask = template_obj.get_window_limits()
    amp[mask] = 0
    snr[mask] = 0

    return amp, age, angle, snr


def plot_results(data, results, az=315, elev=45, figsize=(4, 16)):
    """Plots maps of results from template matching

    Parameters
    ----------
    data : DEMGrid
        DEMGrid object containing input data
    results : np.array
        Array of best-fitting results from compare() or similar function

    Optional Parameters
    -------------------
    az : float
        Azimuth of light source for hillshade
    elev : float
        Elevation angle of light source for hillshade
    figsize : tuple
        Figure size
    """

    fig, ax = plt.subplots(2, 2, figsize=figsize)
    ax = ax.ravel()

    ls = matplotlib.colors.LightSource(azdeg=az, altdeg=elev)
    hillshade = ls.hillshade(data._griddata,
                             vert_exag=1,
                             dx=data._georef_info.dx,
                             dy=data._georef_info.dy)

    labels = ['Amplitude [m]', 'Relative age [m$^2$]',
              'Orientation [deg.]', 'Signal-to-noise ratio']
    cmaps = ['Reds', 'viridis', 'RdBu_r', 'Reds']
    for i, val in enumerate(zip(ax, labels, cmaps)):
        axis, label, cmap = val
        axis.imshow(hillshade, alpha=1, cmap='gray')
        im = axis.imshow(results[i], alpha=0.5, cmap=cmap)
        cb = plt.colorbar(im, ax=axis, shrink=0.5,
                          orientation='horizontal', label=label)
        ticks = matplotlib.ticker.MaxNLocator(nbins=3)
        cb.locater = ticks
        cb.update_ticks()
