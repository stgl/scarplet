""" Class for windowed template matching over a spatial grid """

import dem
from osgeo import osr, ogr, gdal

import math
import numpy as np
import numexpr

from scipy.signal import convolve2d
from scipy.special import erf, erfinv
import matplotlib.pyplot as plt

np.seterr(divide='ignore', invalid='ignore')

DEFAULT_EPSG = 32610 # UTM 10N

class WindowedTemplate(object):
    
    
    def __init__(self):
        
        self.d = None
        self.alpha = None
        self.nx = None
        self.ny = None
        self.de = None

    def parse_args(self, **kwargs):
        
        keys = tuple(kwargs.keys())
        values = tuple(kwargs.values())

        args = dict(zip(keys, values))

        return args

    def template(self):
        pass

    def get_window_limits(self):

        x4 = self.d*np.cos(self.alpha - np.pi/2)
        y4 = self.d*np.sin(self.alpha - np.pi/2)
        x1 = self.d*np.cos(self.alpha)
        y1 = self.d*np.sin(self.alpha)
        an_y = abs((x4 - x1) + 2 * self.c * np.cos(self.alpha - np.pi/2))
        an_x = abs((y1 - y4) + 2 * self.c * np.sin(self.alpha - np.pi/2))

        x = self.de*np.linspace(1, self.nx, num=self.nx)
        y = self.de*np.linspace(1, self.ny, num=self.ny)
        x = x - np.mean(x)
        y = y - np.mean(y)

        X, Y = np.meshgrid(x, y)
        mask = ((X < (min(x) + an_x)) | (X > (max(x) - an_x)) | (Y < (min(y) + an_y)) | (Y > (max(y) - an_y)))

        return mask
    

class Scarp(WindowedTemplate):

    
    def __init__(self, d, kt, alpha, nx, ny, de):

        self.d = d
        self.kt = kt
        self.alpha = -alpha
        self.nx = nx
        self.ny = ny
        self.de = de
        
        frac = 0.9
        self.c = abs(2 * np.sqrt(self.kt) * erfinv(frac))

    def template(self):

        x = self.de * np.linspace(1, self.nx, num=self.nx)
        y = self.de * np.linspace(1, self.ny, num=self.ny)
        x = x - np.mean(x)
        y = y - np.mean(y)

        x, y = np.meshgrid(x, y)
        xr = x * np.cos(self.alpha) + y * np.sin(self.alpha)
        yr = -x * np.sin(self.alpha) + y * np.cos(self.alpha)

        W = (-xr / (2. * self.kt ** (3 / 2.) * np.sqrt(np.pi))) \
            * np.exp(-xr ** 2. / (4. * self.kt))

        mask = (abs(xr) < self.c) & (abs(yr) < self.d)
        W = W * mask
        #W = W.T
        W = np.flipud(np.fliplr(W))

        return W

    def template_numexpr(self):
        
        alpha = self.alpha
        kt = self.kt
        c = self.c
        d = self.d

        x = self.de * np.linspace(1, self.nx, num=self.nx)
        y = self.de * np.linspace(1, self.ny, num=self.ny)
        x = x - np.mean(x)
        y = y - np.mean(y)

        x, y = np.meshgrid(x, y)
        xr = numexpr.evaluate("x * cos(alpha) + y * sin(alpha)")
        yr = numexpr.evaluate("-x * sin(alpha) + y * cos(alpha)")

        pi = np.pi
        W = numexpr.evaluate("(-xr / (2 * kt ** (3/2) * sqrt(pi))) * exp(-xr ** 2 / (4 * kt))")

        mask = numexpr.evaluate("(abs(xr) < c) & (abs(yr) < d)")
        W = numexpr.evaluate("W * mask")
        #W = W.T
        W = np.flipud(np.fliplr(W))

        return W
    

class Morlet(WindowedTemplate):
    
    
    def __init__(self, d, kt, alpha):

        self.d = d
        self.kt = kt
        self.alpha = alpha

    def template(self):
        pass


class Ricker(WindowedTemplate):


    def __init__(self, d, f, alpha, nx, ny, de):

        self.d = d
        self.f = f
        self.alpha = -alpha
        self.nx = nx
        self.ny = ny
        self.de = de

    def template(self):
        
        alpha = self.alpha
        #c = self.c
        d = self.d
        f = self.f

        x = self.de * np.linspace(1, self.nx, num=self.nx)
        y = self.de * np.linspace(1, self.ny, num=self.ny)
        x = x - np.mean(x)
        y = y - np.mean(y)

        x, y = np.meshgrid(x, y)
        xr = numexpr.evaluate("x * cos(alpha) + y * sin(alpha)")
        yr = numexpr.evaluate("-x * sin(alpha) + y * cos(alpha)")

        pi = np.pi
        W = numexpr.evaluate("(1. - 2. * (pi * f * xr) ** 2.) * exp(-(pi * f * xr) ** 2.)")

        #mask = numexpr.evaluate("(abs(xr) < c) & (abs(yr) < d)")
        #W = numexpr.evaluate("W*mask")
        #W = W.T
        #W = np.flipud(np.fliplr(W))

        return W


class Channel(Ricker):
    pass 

