import unittest

import numpy as np
from osgeo import gdal, osr, ogr

from scipy.special import erf

import scarplet as sl

from scarplet.WindowedTemplate import Scarp, Channel

DEFAULT_EPSG = 32610 # UTM 10N



class ScarpTestCase(unittest.TestCase):


    def setUp(self):
    
        self.obj = Scarp(100, 10, 0, 100, 100, 1)

    def test_template(self):

        true = np.load('results/scarp_template.npy')
        test = self.obj.template()

        self.assertTrue(np.allclose(test, true), "Scarp template function is \
                        incorrect")

    def test_template_numexpr(self):

        true = np.load('results/scarp_template_numexpr.npy')
        test = self.obj.template_numexpr()

        self.assertTrue(np.allclose(test, true), "Scarp template function is \
                        incorrect")


class ChannelTestCase(unittest.TestCase):


    def setUp(self):
    
        self.obj = Channel(100, 0.1, 0, 100, 100, 1)

    def test_template(self):

        true = np.load('results/channel_template.npy')
        test = self.obj.template()

        self.assertTrue(np.allclose(test, true), "Channel template function is \
                        incorrect")
