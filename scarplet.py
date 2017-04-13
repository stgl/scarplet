""" Functions for determinig best-fit template parameters by convolution with a
grid """

import dem
import WindowedTemplate as wt
import numpy as np
import pyfftw
from pyfftw.interfaces.numpy_fft import fft2, ifft2, fftshift

eps = np.spacing(1)
pyfftw.interfaces.cache.enable()

def calculate_amplitude(dem, Template, d, age, alpha):
    ny, nx = dem._griddata.shape
    de = dem._georef_info.dx
    t = Template(d, age, alpha, nx, ny, de)
    template = t.template()

    curv = dem._calculate_directional_laplacian(alpha)
    
    amp, snr = match_template(curv, template)
    mask = t.window_limits()
    amp[mask] = 0 
    snr[mask] = 0 

    return amp, snr

#@profile
def calculate_best_fit_parameters(dem, Template, **kwargs):
    
    template_args = parse_args(**kwargs)
    template_args['nx'] = dem._georef_info.nx
    template_args['ny'] = dem._georef_info.ny

    age_max = 3.5 
    age_min = 0
    age_stepsize = 0.1
    ang_stepsize = 1

    num_angles = 180/ang_stepsize + 1
    num_ages = (age_max - age_min)/age_stepsize
    orientations = np.linspace(-np.pi/2, np.pi/2, num_angles)
    ages = np.linspace(age_min, age_max, num_ages)

    best_amp = np.zeros((ny, nx))
    best_age = np.zeros((ny, nx))
    best_alpha = np.zeros((ny, nx))
    best_snr = np.zeros((ny, nx))

    for this_alpha in orientations:
        for this_age in ages:
            
            this_age = 10**this_age

            template_args['alpha'] = this_alpha
            template_args['age'] = this_age
            t = Template(template_args)
            template = t.template()

            curv = dem._calculate_directional_laplacian(this_alpha)
            
            amp, snr = match_template(curv, template)
            mask = t.window_limits()
            amp[mask] = 0 
            snr[mask] = 0

            best_snr = (best_snr > snr)*best_snr + (best_snr < snr)*snr
            best_amp = (best_snr > snr)*best_amp + (best_snr < snr)*amp
            best_alpha = (best_snr > snr)*best_alpha + (best_snr < snr)*this_alpha
            best_age = (best_snr > snr)*best_age + (best_snr < snr)*this_age
            
    return best_amp, best_age, best_alpha, best_snr 

def compare_fits(grids):
    s = grids[0].amplitude.shape
    best_snr = np.zeros(s)
    best_amp = np.zeros(s)
    best_age = np.zeros(s)
    best_alpha = np.zeros(s)

    for fit in grids:
        best_snr = (best_snr > fit.snr)*best_snr + (best_snr < fit.snr)*fit.snr
        best_amp = (best_snr > fit.snr)*best_amp + (best_snr < fit.snr)*fit.amplitude
        best_alpha = (best_snr > fit.snr)*best_alpha + (best_snr < fit.snr)*fit.alpha
        best_age = (best_snr > fit.snr)*best_age + (best_snr < fit.snr)*fit.age

    return best_amp, best_age, best_alpha, best_snr

#@profile
def match_template(data, template):
    
    #template = template_function(template_args)

    if data.ndim < template.ndim:
        raise ValueError("Dimensions of template must be less than or equal to dimensions of data matrix")
    if np.any(np.less(data.shape, template.shape)):
        raise ValueError("Size of template must be less than or equal to size of data matrix")

    pad_width = tuple((wid, wid) for wid in template.shape)

    #data = np.pad(data, pad_width=pad_width, mode='symmetric')

    M = template != 0
    fc = fft2(data)
    ft = fft2(template)
    fc2 = fft2(data**2)
    fm2 = fft2(M)

    #xcorr = signal.fftconvolve(data, template, mode='same')
    xcorr = np.real(fftshift(ifft2(ft*fc)))
    template_sum = np.sum(template**2)
    
    amp = xcorr/template_sum
    
    n = np.sum(M) + eps
    T1 = template_sum*amp**2
    T2 = -2*xcorr
    T3 = fftshift(ifft2(fc2*fm2))
    error = (1/n)*(T1 + T2 + T3) + eps
    #error = (1/n)*(amp**2*template_sum - 2*amp*fftshift(ifft2(fc*ft)) + fftshift(ifft2(fc2*fm2))) + eps
    error = np.real(error)
    snr = T1/error
    snr = np.real(snr)

    return amp, snr

def parse_args(**kwargs):
    pass


class TemplateFit(object):
    def __init__(d, age, alpha, amplitude, snr):
        self.d = d
        self.age = age
        self.alpha = alpha
        self.amplitude = amplitude
        self.snr = snr

