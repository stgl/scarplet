import os
import sys
import filecmp
import numpy as np
import unittest

import matplotlib
import matplotlib.pyplot as plt

from context import scarplet
from scarplet import dem


TEST_DIR = os.path.dirname(__file__)


class CalculationMethodsTestCase(unittest.TestCase):
    
    
    def setUp(self):
        
        self.dem = dem.DEMGrid(os.path.join(TEST_DIR, 'data/faultzone.tif'))

    def test_calculate_slope(self):

        sx, sy = self.dem._calculate_slope()
        true_sx, true_sy = np.load(os.path.join(TEST_DIR, 'results/faultzone_sxsy.npy'))

        self.assertTrue(np.allclose(sx, true_sx), "Slope (x direction) incorrect")
        self.assertTrue(np.allclose(sy, true_sy), "Slope (y direction) incorrect")

    def test_calculate_laplacian(self):

        del2z = self.dem._calculate_laplacian()
        true_del2z = np.load(os.path.join(TEST_DIR, 'results/faultzone_del2z.npy'))
        self.assertTrue(np.allclose(del2z, true_del2z), "Laplacian incorrect (y axis direction)")
    
    def test_calculate_directional_laplacian(self):
        
        alphas = [-np.pi / 2, -np.pi / 4, np.pi / 4, np.pi / 2]
        for alpha in alphas:
            del2z = self.dem._calculate_directional_laplacian(alpha)
            alpha *= 180 / np.pi
            true_del2z = np.load(os.path.join(TEST_DIR, 'results/faultzone_del2z_{:.0f}.npy'.format(alpha)))
            self.assertTrue(np.allclose(del2z, true_del2z), "Laplacian incorrect (+{:.0f} deg)".format(alpha))

    def test_pad_boundary(self):
        
        dx = 5
        dy = 5
        grid = self.dem._griddata

        padded_grid = np.pad(grid, pad_width=(dy, dx), mode='reflect')
        
        self.dem._pad_boundary(dx, dy)
        
        self.assertEqual(self.dem._griddata.all(), padded_grid.all(), "Grid padded incorrectly")
