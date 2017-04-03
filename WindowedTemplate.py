""" Class for windowed template matching over a spatial grid """

import numpy as np
from scipy.signal import convolve2d


class WindowedTemplate(object):
    
    
    def __init__(self):
        pass

    def template(self):
        pass


class Scarp(WindowedTemplate):

    
    name = "Vertical Scarp"

    def __init__(d, kt, alpha):
        self.d = d
        self.kt = kt
        self.alpha = alpha

    def template(self):
        pass

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
