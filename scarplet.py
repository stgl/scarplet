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
            best_alpha = (best_snr > snr)*best_alpha + (best_snr < snr)*this_alpha
            best_age = (best_snr > snr)*best_age + (best_snr < snr)*this_age

