"""
Benchmarks for basic operations in scarplet code
"""
import dem
import scarplet
from WindowedTemplate import Scarp

import numpy as np
import numexpr

from scipy.special import erf, erfinv

import pyfftw
from pyfftw.interfaces.numpy_fft import fft2, ifft2, fftshift

from timeit import default_timer as timer
from progressbar import ProgressBar, Bar, Percentage, ETA

import matplotlib.pyplot as plt

def calculate_directional_laplacian_numexpr(data, alpha):

    dx = data._georef_info.dx
    dy = data._georef_info.dy       
    z = data._griddata
    nan_idx = np.isnan(z)
    z[nan_idx] = 0
    
    dz_dx = np.diff(z, 1, 1)/dx
    d2z_dxdy = np.diff(dz_dx, 1, 0)/dx
    pad_x = np.zeros((d2z_dxdy.shape[0], 1))
    d2z_dxdy = np.hstack([pad_x, d2z_dxdy])
    pad_y = np.zeros((1, d2z_dxdy.shape[1]))
    d2z_dxdy = np.vstack([pad_y, d2z_dxdy])
    
    d2z_dx2 = np.diff(z, 2, 1)/dx**2
    pad_x = np.zeros((d2z_dx2.shape[0], 1))
    d2z_dx2 = np.hstack([pad_x, d2z_dx2, pad_x])

    d2z_dy2 = np.diff(z, 2, 0)/dy**2
    pad_y = np.zeros((1, d2z_dy2.shape[1]))
    d2z_dy2 = np.vstack([pad_y, d2z_dy2, pad_y])

    del2z = numexpr.evaluate("d2z_dx2*cos(alpha)**2 - 2*d2z_dxdy*sin(alpha)*cos(alpha) + d2z_dy2*sin(alpha)**2")
    del2z[nan_idx] = np.nan 

    return del2z

def match_template_numexpr(data, template):
    
    eps = np.spacing(1)
    #template = template_function(template_args)

    if data.ndim < template.ndim:
        raise ValueError("Dimensions of template must be less than or equal to dimensions of data matrix")
    if np.any(np.less(data.shape, template.shape)):
        raise ValueError("Size of template must be less than or equal to size of data matrix")

    #pad_width = tuple((wid, wid) for wid in template.shape)

    #data = np.pad(data, pad_width=pad_width, mode='symmetric')

    M = numexpr.evaluate("template != 0")
    fc = fft2(data)
    ft = fft2(template)
    fc2 = fft2(numexpr.evaluate("data**2"))
    fm2 = fft2(M)

    #xcorr = signal.fftconvolve(data, template, mode='same')
    xcorr = np.real(fftshift(ifft2(numexpr.evaluate("ft*fc"))))
    template_sum = np.sum(template**2)
    
    amp = numexpr.evaluate("xcorr/template_sum")
   
    # TODO  remove intermediate terms to make more memory efficent
    n = np.sum(M) + eps
    T1 = numexpr.evaluate("template_sum*(amp**2)")
    T3 = fftshift(ifft2(numexpr.evaluate("fc2*fm2")))
    error = (1/n)*numexpr.evaluate("real(T1 - 2*amp*xcorr + T3)") + eps # avoid small-magnitude dvision
    #error = (1/n)*(amp**2*template_sum - 2*amp*fftshift(ifft2(fc*ft)) + fftshift(ifft2(fc2*fm2))) + eps
    snr = numexpr.evaluate("real(T1/error)")

    return amp, snr

def template_numexpr(nx, ny, de, kt, alpha):
    frac = 0.9
    c = abs(2*np.sqrt(kt)*erfinv(frac))

    x = de*np.linspace(1, nx, num=nx)
    y = de*np.linspace(1, ny, num=ny)
    x = x - np.mean(x)
    y = y - np.mean(y)

    x, y = np.meshgrid(x, y)
    xr = numexpr.evaluate("x*cos(alpha) + y*sin(alpha)")
    yr = numexpr.evaluate("-x*sin(alpha) + y*cos(alpha)")

    pi = np.pi
    W = numexpr.evaluate("(-xr/(2*kt**(3/2)*sqrt(pi)))*exp(-xr**2/(4*kt))")

    mask = numexpr.evaluate("(abs(xr) < c) & (abs(yr) < d)")
    W = numexpr.evaluate("W*mask")
    #W = W.T

    return W

if __name__ == "__main__":

    data = dem.DEMGrid("tests/data/carrizo.tif")
    
    orientations = np.linspace(-np.pi/2, np.pi/2, 91) 
    ages = [0, 1, 2, 3]

    d = 100
    ny, nx = data._griddata.shape
    de = data._georef_info.dx
   
    # Normal test
    #print("Testing naive implementation")

    #best_amp = np.zeros((ny, nx))
    #best_age = np.zeros((ny, nx))
    #best_alpha = np.zeros((ny, nx))
    #best_snr = np.zeros((ny, nx))

    #pbar = ProgressBar(widgets=[Percentage(), Bar(left='[', right=']'), ' ', ETA()], maxval=len(ages)*len(orientations)).start()

    #start = timer()
    #for i, this_alpha in enumerate(orientations):
    #    for j, this_age in enumerate(ages):
    #        
    #        this_age = 10**this_age

    #        t0 = timer()
    #        t = Scarp(d, this_age, this_alpha, nx, ny, de)
    #        template = t.template()
    #        t1 = timer()
    #        #print("Generate template:\t\t\t{:.2f} s".format(t1-t0))

    #        t0 = timer()
    #        curv = data._calculate_directional_laplacian(this_alpha)
    #        t1 = timer()
    #        #print("Calculate Laplacian:\t\t\t{:.2f} s".format(t1-t0))
    #        
    #        t0 = timer()
    #        this_amp, this_snr = scarplet.match_template(curv, template)
    #        t1 = timer()
    #        #print("Match template:\t\t\t\t{:.2f} s".format(t1-t0))
    #        mask = t.get_window_limits()
    #        this_amp[mask] = 0 
    #        this_snr[mask] = 0

    #        t0 = timer()
    #        best_amp = (best_snr > this_snr)*best_amp + (best_snr < this_snr)*this_amp
    #        best_age = (best_snr > this_snr)*best_age + (best_snr < this_snr)*this_age
    #        best_alpha = (best_snr > this_snr)*best_alpha + (best_snr < this_snr)*this_alpha
    #        best_snr = (best_snr > this_snr)*best_snr + (best_snr < this_snr)*this_snr
    #        t1 = timer()
    #        #print("Find best SNR:\t\t\t\t{:.2f} s".format(t1-t0))

    #        pbar.update((i+1)*len(ages))
    #stop = timer()
    #print("\nTime elapsed:\t\t\t\t{:.2f} s".format(stop-start))

    #fig = plt.figure()
    #fig.add_subplot(121)
    #plt.imshow(best_snr)

    #true_age = best_age.copy()
    #true_snr = best_snr.copy()

    # Numexpr test
    print("-"*80)
    print("Testing numexpr implementation")

    best_amp = np.zeros((ny, nx))
    best_age = np.zeros((ny, nx))
    best_alpha = np.zeros((ny, nx))
    best_snr = np.zeros((ny, nx))

    pbar = ProgressBar(widgets=[Percentage(), Bar(left='[', right=']'), ' ', ETA()], maxval=len(ages)*len(orientations)).start()

    start = timer()
    for i, this_alpha in enumerate(orientations):
        for j, this_age in enumerate(ages):
            
            this_age = 10**this_age

            t0 = timer()
            t = Scarp(d, this_age, this_alpha, nx, ny, de)
            template = t.template_numexpr()
            t1 = timer()
            #print("Generate template:\t\t\t{:.2f} s".format(t1-t0))

            t0 = timer()
            curv = data._calculate_directional_laplacian_numexpr(this_alpha)
            t1 = timer()
            #print("Calculate Laplacian:\t\t\t{:.2f} s".format(t1-t0))
            
            t0 = timer()
            this_amp, this_snr = scarplet.match_template_numexpr(curv, template)
            t1 = timer()
            #print("Match template:\t\t\t\t{:.2f} s".format(t1-t0))
            mask = t.get_window_limits()
            this_amp[mask] = 0 
            this_snr[mask] = 0

            t0 = timer()
            best_amp = numexpr.evaluate("(best_snr > this_snr)*best_amp + (best_snr < this_snr)*this_amp")
            best_age = numexpr.evaluate("(best_snr > this_snr)*best_age + (best_snr < this_snr)*this_age")
            best_alpha = numexpr.evaluate("(best_snr > this_snr)*best_alpha + (best_snr < this_snr)*this_alpha")
            best_snr = numexpr.evaluate("(best_snr > this_snr)*best_snr + (best_snr < this_snr)*this_snr")
            t1 = timer()
            #print("Find best SNR:\t\t\t\t{:.2f} s".format(t1-t0))

            pbar.update((i+1)*len(ages))
    stop = timer()
    print("\nTime elapsed:\t\t\t\t{:.2f} s".format(stop-start))

    fig.add_subplot(122)
    plt.imshow(best_snr)

    fig = plt.figure()
    fig.add_subplot(121)
    plt.imshow(true_age - best_age)
    fig.add_subplot(122)
    plt.imshow(true_snr - best_snr)

    plt.show()

