"""
Benchmarks for basic operations in scarplet code
"""
import dem
import scarplet
from WindowedTemplate import Scarp

import numpy as np
import numexpr

#import pyfftw
#from pyfftw.interfaces.numpy_fft import fft2, ifft2, fftshift

from timeit import default_timer as timer

if __name__ == "__main__":
    data = dem.DEMGrid("tests/data/carrizo.tif")
    
    orientations = [0, np.pi/4]
    ages = [0, 10]

    d = 100
    ny, nx = data._griddata.shape
    de = data._georef_info.dx
   
    # Normal test
    print("Testing naive implementation")

    best_amp = np.zeros((ny, nx))
    best_age = np.zeros((ny, nx))
    best_alpha = np.zeros((ny, nx))
    best_snr = np.zeros((ny, nx))

    start = timer()
    for i, this_alpha in enumerate(orientations):
        for j, this_age in enumerate(ages):
            
            this_age = 10**this_age

            t0 = timer()
            t = Scarp(d, this_age, this_alpha, nx, ny, de)
            template = t.template()
            t1 = timer()
            print("Generate template:\t\t\t{:.2f} s".format(t1-t0))

            t0 = timer()
            curv = data._calculate_directional_laplacian(this_alpha)
            t1 = timer()
            print("Calculate Laplacian:\t\t\t{:.2f} s".format(t1-t0))
            
            t0 = timer()
            this_amp, this_snr = scarplet.match_template(curv, template)
            t1 = timer()
            print("Match template:\t\t\t\t{:.2f} s".format(t1-t0))
            mask = t.get_window_limits()
            this_amp[mask] = 0 
            this_snr[mask] = 0

            t0 = timer()
            best_amp = (best_snr > this_snr)*best_amp + (best_snr < this_snr)*this_amp
            best_age = (best_snr > this_snr)*best_age + (best_snr < this_snr)*this_age
            best_alpha = (best_snr > this_snr)*best_alpha + (best_snr < this_snr)*this_alpha
            best_snr = (best_snr > this_snr)*best_snr + (best_snr < this_snr)*this_snr
            t1 = timer()
            print("Find best SNR:\t\t\t\t{:.2f} s".format(t1-t0))
    stop = timer()
    print("Time elapsed:\t\t\t\t{:.2f} s\".format(stop-start))

    # Numexpr test
    print("-"*80)
    print("Testing numexpr implementation")

    best_amp = np.zeros((ny, nx))
    best_age = np.zeros((ny, nx))
    best_alpha = np.zeros((ny, nx))
    best_snr = np.zeros((ny, nx))

    start = timer()
    for i, this_alpha in enumerate(orientations):
        for j, this_age in enumerate(ages):
            
            this_age = 10**this_age

            t0 = timer()
            t = Scarp(d, this_age, this_alpha, nx, ny, de)
            template = t.template()
            t1 = timer()
            print("Generate template:\t\t\t{:.2f} s".format(t1-t0))

            t0 = timer()
            curv = data._calculate_directional_laplacian(this_alpha)
            t1 = timer()
            print("Calculate Laplacian:\t\t\t{:.2f} s".format(t1-t0))
            
            t0 = timer()
            this_amp, this_snr = scarplet.match_template(curv, template)
            t1 = timer()
            print("Match template:\t\t\t\t{:.2f} s".format(t1-t0))
            mask = t.get_window_limits()
            this_amp[mask] = 0 
            this_snr[mask] = 0

            t0 = timer()
            best_amp = numexpr.evaluate("(best_snr > this_snr)*best_amp + (best_snr < this_snr)*this_amp")
            best_age = numexpr.evaluate("(best_snr > this_snr)*best_age + (best_snr < this_snr)*this_age")
            best_alpha = numexpr.evaluate("(best_snr > this_snr)*best_alpha + (best_snr < this_snr)*this_alpha")
            best_snr = numexpr.evaluate("(best_snr > this_snr)*best_snr + (best_snr < this_snr)*this_snr")
            t1 = timer()
            print("Find best SNR:\t\t\t\t{:.2f} s".format(t1-t0))
    stop = timer()
    print("Time elapsed:\t\t\t\t{:.2f} s".format(stop-start))
