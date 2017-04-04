""" Functions for determinig best-fit template parameters by convolution with a
grid """

import dem
import WindowedTemplate as wt
import numpy as np
from numpy.fft import fft2, ifft2, fftshift
from scipy import signal

eps = np.spacing(1)

@profile
def calculate_best_fit_parameters(dem, Template, **kwargs):
    
    template_args = parse_args(**kwargs)
    template_args['nx'] = dem._georef_info.nx
    template_args['ny'] = dem._georef_info.ny


    age_max = 1 
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
            template = Template(template_args).template()

            curv = dem._calculate_directional_laplacian(this_alpha)
            
            amp, snr = match_template(curv, template)

            best_snr = (best_snr > snr)*best_snr + (best_snr < snr)*snr
            best_amp = (best_snr > snr)*best_amp + (best_snr < snr)*amp
            best_alpha = (best_snr > snr)*best_alpha + (best_snr < snr)*this_alpha
            best_age = (best_snr > snr)*best_age + (best_snr < snr)*this_age
            
    return best_amp, best_age, best_alpha, best_snr 

@profile
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
    error = (1/n)*(amp**2*template_sum - 2*amp*fftshift(ifft2(fc*ft)) + fftshift(ifft2(fc2*fm2))) + eps
    snr = (amp**2)*template_sum/error
    error = np.real(error)
    snr = np.real(snr)

    #return amp
    return amp, snr

def parse_args(**kwargs):
    pass
