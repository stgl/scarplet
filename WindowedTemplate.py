""" Class for windowed template matching over a spatial grid """

import math
import numpy as np
from scipy.signal import convolve2d
from scipy.special import erfinv

import matplotlib.pyplot as plt

class WindowedTemplate(object):
    
    
    def __init__(self):
        pass

    def parse_args(self, **kwargs):
        
        keys = tuple(kwargs.keys())
        values = tuple(kwargs.values())

        args = dict(zip(keys, values))

        return args


    def template(self):
        pass

    

class Scarp(WindowedTemplate):

    
    name = "Vertical Scarp"

    def __init__(self, d, kt, alpha, nx, ny, de):
        self.d = d
        self.kt = kt
        self.alpha = alpha
        self.nx = nx
        self.ny = ny
        self.de = de

    def template(self):

        frac = 0.9
        c = abs(2*np.sqrt(self.kt)*erfinv(frac))
        
        x = self.de*np.linspace(1, self.nx, num=self.nx)
        y = self.de*np.linspace(1, self.ny, num=self.ny)
        x = x - np.mean(x)
        y = y - np.mean(y)

        x, y = np.meshgrid(x, y)
        xr = x*np.cos(self.alpha) + y*np.sin(self.alpha)
        yr = -x*np.sin(self.alpha) + y*np.cos(self.alpha)

        W = (-xr/(2*self.kt**(3/2)*np.sqrt(np.pi)))*np.exp(-xr**2/(4*self.kt))

        mask = (abs(xr) < c) & (abs(yr) < self.d)
        W = W*mask

        fig = plt.figure()
        plt.subplot(2,1,1)
        plt.imshow(W, cmap='bwr')
        plt.subplot(2,1,2)
        plt.plot(W[self.nx/2, ::])

        return W, mask

class Channel(WindowedTemplate):
    
    
    name = "Channel"

    def __init__(d, kt, alpha):
        self.d = d
        self.kt = kt
        self.alpha = alpha

    def template(self):
        pass


class Morlet(WindowedTemplate):


    name = "Morlet"

    def __init__(d, kt, alpha):
        self.d = d
        self.kt = kt
        self.alpha = alpha

    def template(self):
        pass



