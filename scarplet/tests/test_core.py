import filecmp
import numpy as np
import os
import sys
import pytest
import unittest

from osgeo import gdal, osr
from scipy.special import erf

from context import scarplet
import scarplet as sl
from scarplet import dem
from scarplet.WindowedTemplate import Scarp


DEFAULT_EPSG = 32610
TEST_DIR = os.path.dirname(__file__)


class TemplateMatchingTestCase(unittest.TestCase):
    
    
    def setUp(self):
        
        self.data = sl.load(os.path.join(TEST_DIR, 'data/synthetic.tif'))

    @pytest.mark.slow
    def test_match(self):
        
        template_args = {'scale': 100,
                        'ang_max': np.pi / 2,
                        'ang_min': -np.pi / 2
                        }

        res = sl.match(self.data, Scarp, **template_args)
        amp, age, alpha, snr = res

        true = np.load(os.path.join(TEST_DIR, 'results/synthetic_match1.npy'))
        true_amp, true_age, true_alpha, true_snr = true
        
        self.assertTrue(np.allclose(amp, true_amp), "Amplitudes incorrect")
        self.assertTrue(np.allclose(age, true_age), "Ages incorrect")
        self.assertTrue(np.allclose(alpha, true_alpha), "Orientations incorrect")
        self.assertTrue(np.allclose(snr, true_snr), "SNRs incorrect")

    def test_match_single_age(self):
        
        template_args = {'scale': 100,
                         'age': 10,
                        'ang_max': np.pi / 2,
                        'ang_min': -np.pi / 2
                        }

        res = sl.match(self.data, Scarp, **template_args)
        amp, age, alpha, snr = res
        
        true = np.load(os.path.join(TEST_DIR, 'results/synthetic_match2.npy'))
        true_amp, true_age, true_alpha, true_snr = true
        
        self.assertTrue(np.allclose(amp, true_amp), "Amplitudes incorrect")
        self.assertTrue(np.allclose(age, true_age), "Ages incorrect")
        self.assertTrue(np.allclose(alpha, true_alpha), "Orientations incorrect")
        self.assertTrue(np.allclose(snr, true_snr), "SNRs incorrect")

    def test_match_template(self):
        
        template_args = {'scale': 100,
                         'age': 10,
                         'angle': 0
                        }

        res = sl.match_template(self.data, Scarp, **template_args)
        amp, age, alpha, snr = res

        true = np.load(os.path.join(TEST_DIR, 'results/synthetic_match3.npy'))
        true_amp, true_age, true_alpha, true_snr = true
        
        self.assertTrue(np.allclose(amp, true_amp), "Amplitudes incorrect")
        self.assertTrue(np.allclose(age, true_age), "Ages incorrect")
        self.assertTrue(np.allclose(alpha, true_alpha), "Orientations incorrect")
        self.assertTrue(np.allclose(snr, true_snr), "SNRs incorrect")


def generate_synthetic_scarp(a, b, kt, x_max, y_max, de=1, sig2=0, theta=0):
    """ Generate DEM of synthetic scarp for testing """
    
    nx = int(2 * x_max / de)
    ny = int(2 * y_max / de)
    x = np.linspace(-x_max, x_max, num=nx)
    y = np.linspace(-y_max, y_max, num=ny)
    x, y = np.meshgrid(x, y)
    
    theta = np.pi/2 - theta
    xrot = x*np.cos(theta) + y*np.sin(theta)
    yrot = -x*np.sin(theta) + y*np.cos(theta)

    z = -erf(yrot/(2*np.sqrt(kt))) + b*yrot
    z = z + sig2*np.random.randn(ny, nx)

    return set_up_grid(z, nx, ny, de) 


def set_up_grid(data, nx, ny, de):

    synthetic = dem.DEMGrid()
    geo_transform = (0, de, 0, 0, 0, -de) 
    projection = osr.SpatialReference()
    projection.ImportFromEPSG(DEFAULT_EPSG)

    synthetic._griddata = data 
    synthetic._georef_info.geo_transform = geo_transform
    synthetic._georef_info.projection = projection
    synthetic._georef_info.dx = de 
    synthetic._georef_info.dy = de 
    synthetic._georef_info.nx = nx 
    synthetic._georef_info.ny = ny
    synthetic._georef_info.xllcenter = 0 
    synthetic._georef_info.yllcenter = 0 

    return synthetic
