""" Functions for determinig best-fit template parameters by convolution with a
grid """

import dem
import WindowedTemplate as wt
import numpy as np
from scipy import signal

def calculate_best_fit_parameters(dem, template_function, **kwargs):
    
    template_args = parse_args(**kwargs)

    num_angles = 180/ang_stepsize
    num_ages = (age_max - age_min)/age_stepsize
    orientations = np.linspace(-np.pi/2, np.pi/2, num_angles)
    ages = np.linspace(age_min, age_max, num_ages)

    for this_alpha in orientations:
        for this_age in ages:

            template_args['alpha'] = this_alpha
            template_args['age'] = this_age

            curv = dem._calculate_directional_laplacian(this_alpha)

            amplitude, snr = match_template(curv, template_function, template_args)

            if 'noiselevel' in kwargs:
                snr = snr/noiselevel

            best_snr = (best_snr > snr)*best_snr + (best_snr < snr)*snr
            best_amplitude = (best_snr > snr)*best_amplitude + (best_snr < snr)*this_amplitude
            best_alpha = (best_snr > snr)*best_alpha + (best_snr < snr)*this_alpha
            best_age = (best_snr > snr)*best_age + (best_snr < snr)*this_age

    return best_amplitude, best_age, best_alpha, best_snr 

def match_template(data, template_function, template_args):
    
    template = template_function(template_args)

    if data.ndim < template.ndim:
        raise ValueError("Dimensions of template must be less than or equal to dimensions of data matrix")
    if np.any(np.less(data.shape, template.shape)):
        raise ValueError("Size of template must be less than or equal to size of data matrix")

    pad_width = tuple((wid, wid) for wid in template.shape)

    data = np.pad(data, pad_width=pad_width, mode='symmetric')

    xcorr = signal.fftconvolve(data, template)
    template_power = sum(np.ravel(template)**2)
    
    amplitude = xcorr/template_power
    #error =
    #snr = (amplitude**2)*template_power/error

    return amplitude
    #return amplitude, snr
