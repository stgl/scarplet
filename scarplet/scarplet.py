""" Functions for determinig best-fit template parameters by convolution with a
grid """


import numpy as np
import numexpr
import multiprocessing as mp
import matplotlib.pyplot as plt

import pyfftw
from pyfftw.interfaces.numpy_fft import fft2, ifft2, fftshift

from functools import partial

from scarplet.dem import BaseSpatialGrid, DEMGrid, Hillshade


np.seterr(divide='ignore', invalid='ignore')

pyfftw.interfaces.cache.enable()


def calculate_amplitude(dem, Template, d, age, alpha):

    ny, nx = dem._griddata.shape
    de = dem._georef_info.dx
    t = Template(d, age, alpha, nx, ny, de)
    template = t.template()

    curv = dem._calculate_directional_laplacian(alpha)
    
    amp, snr = match_template(curv, template)
    mask = t.get_window_limits()
    amp[mask] = 0 
    snr[mask] = 0 

    return amp, snr

#@profile
def calculate_best_fit_parameters_serial(dem, Template, d, this_age, **kwargs):
    
    this_age = 10**this_age
    #args = parse_args(**kwargs)
    de = dem._georef_info.dx 

    ang_stepsize = 1

    num_angles = 180/ang_stepsize + 1
    orientations = np.linspace(-np.pi/2, np.pi/2, num_angles)

    ny, nx = dem._griddata.shape
    best_amp = np.zeros((ny, nx))
    best_alpha = np.zeros((ny, nx))
    best_snr = np.zeros((ny, nx))

    for this_alpha in orientations:
        t = Template(d, this_age, this_alpha, nx, ny, de)
        template = t.template()

        curv = dem._calculate_directional_laplacian_numexpr(this_alpha)
        
        this_amp, this_snr = match_template_numexpr(curv, template)
        mask = t.get_window_limits()
        this_amp[mask] = np.nan 
        this_snr[mask] = np.nan

        best_amp = numexpr.evaluate("(best_snr > this_snr)*best_amp + (best_snr < this_snr)*this_amp")
        best_alpha = numexpr.evaluate("(best_snr > this_snr)*best_alpha + (best_snr < this_snr)*this_alpha")
        best_snr = numexpr.evaluate("(best_snr > this_snr)*best_snr + (best_snr < this_snr)*this_snr")         
    
    return best_amp, this_age*np.ones_like(best_amp), best_alpha, best_snr 

# XXX: This version uses multiple cores
def calculate_best_fit_parameters(dem, Template, d, this_age, ang_max, ang_min, **kwargs):
    
    this_age = 10**this_age # XXX: Assumes age parameter is given as logarithm
    #args = parse_args(**kwargs) 
    de = dem._georef_info.dx 

    ang_stepsize = 1

    num_angles = int((180 / np.pi) * (ang_max - ang_min) / ang_stepsize + 1)
    orientations = np.linspace(ang_min, ang_max, num_angles)

    ny, nx = dem._griddata.shape

    nprocs = mp.cpu_count()
    pool = mp.Pool(processes=nprocs)
    wrapper = partial(match_template, dem, Template, d, this_age)
    results = pool.imap(wrapper, (angle for angle in orientations), chunksize=1)
    
    best_amp, best_alpha, best_snr = compare_async_results(results, ny, nx)

    pool.close()
    pool.join()
    
    return np.stack([best_amp, this_age*np.ones_like(best_amp), best_alpha, best_snr])

def compare_async_results(results, ny, nx):

    best_amp = np.zeros((ny, nx))
    best_alpha = np.zeros((ny, nx))
    best_snr = np.zeros((ny, nx))

    for r in results:
        this_amp, this_alpha, this_snr = r

        best_amp = numexpr.evaluate("(best_snr > this_snr)*best_amp + (best_snr < this_snr)*this_amp")
        best_alpha = numexpr.evaluate("(best_snr > this_snr)*best_alpha + (best_snr < this_snr)*this_alpha")
        best_snr = numexpr.evaluate("(best_snr > this_snr)*best_snr + (best_snr < this_snr)*this_snr")         
        del this_amp, this_snr, r

    return best_amp, best_alpha, best_snr 

def load(filename):

    data_obj = DEMGrid(filename)
    data_obj._fill_nodata()

    return data_obj

def match(data, Template, **kwargs):

    results = calculate_best_fit_parameters_serial(data, Template, **kwargs)

    return results

#@profile
def match_template(data, Template, d, age, angle):

    eps = np.spacing(1)
    curv = data._calculate_directional_laplacian(angle) 
    ny, nx = curv.shape
    de = data._georef_info.dx 

    template_obj = Template(d, age, angle, nx, ny, de)
    template = template_obj.template()
    mask = template_obj.get_window_limits()

    if curv.ndim < template.ndim:
        raise ValueError("Dimensions of template must be less than or equal to dimensions of data matrix")
    if np.any(np.less(curv.shape, template.shape)):
        raise ValueError("Size of template must be less than or equal to size of data matrix")

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
   
    # TODO  remove intermediate terms to make more memory efficent
    T1 = numexpr.evaluate("template_sum*(amp**2)")
    T3 = fftshift(ifft2(numexpr.evaluate("fc2*fm2")))
    error = (1/n)*numexpr.evaluate("real(T1 - 2*amp*xcorr + T3)") + eps # avoid small-magnitude dvision
    #error = (1/n)*(amp**2*template_sum - 2*amp*fftshift(ifft2(fc*ft)) + fftshift(ifft2(fc2*fm2))) + eps
    snr = numexpr.evaluate("abs(T1/error)")

    # XXX: this is neccessary to avoid comparisons with NAN
    amp[mask] = 0
    snr[mask] = 0

    return amp, angle, snr

def plot_results(data, results, figsize=(9,3)):
    
    results[0] = np.abs(results[0])
    results[1] = np.log10(results[1])

    fig, ax = plt.subplots(1, 3, figsize=figsize)

    ls = matplotlib.colors.LightSource(azdeg=az, altdeg=elev)
    hillshade = ls.hillshade(data._griddata, vert_exag=1, dx=data._georef_info.dx, dy=data._georef_info.dy)
    
    labels = ['Amplitude [m]', 'Relative age [m$^2$]', 'Orientation [deg.]', 'Signal-to-noise ratio']
    cmaps = ['Reds', 'viridis', 'RdBu_r', 'Reds']
    for i, axis, label, cmap in enumerate(zip(ax, labels, cmaps)):
        axis.imshow(hillshade, alpha=1, cmap='gray')
        im = axis.imshow(results[i], alpha=0.5, cmap=cmaps)
        plt.colorbar(im, ax=ax, shrink=0.5, orientation='horizontal', label=label)
