import os
import sys
import filecmp
import numpy as np
import unittest

import matplotlib
import matplotlib.pyplot as plt

from context import scarplet
from scarplet import dem


TESTDATA_FILENAME = os.path.join(os.path.dirname(__file__), 'data/faultzone.tif')


class CalculationMethodsTestCase(unittest.TestCase):
    
    
    def setUp(self):
        
        self.dem = dem.DEMGrid(TESTDATA_FILENAME)

    def test_calculate_slope(self):

        sx, sy = self.dem._calculate_slope()
        true_sx, true_sy = np.load('results/faultzone_sxsy.npy')

        self.assertEqual(sx.all(), true_sx.all(), "Slope (x direction) incorrect")
        self.assertEqual(sy.all(), true_sy.all(), "Slope (y direction) incorrect")

    def test_calculate_laplacian(self):

        del2z = self.dem._calculate_laplacian()
        true_del2z = np.load('results/faultzone_del2z.npy')
        self.assertEqual(del2z.all(), true_del2z.all(), "Laplacian incorrect (y axis direction)")
    
    def test_calculate_directional_laplacian(self):
        
        alphas = [-np.pi / 2, -np.pi / 4, np.pi / 4, np.pi / 2]
        for alpha in alphas:
            del2z = self.dem._calculate_directional_laplacian(alpha)
            alpha *= 180 / np.pi
            true_del2z = np.load('results/faultzone_del2z_{:.0f}.npy'.format(alpha))
            self.assertEqual(del2z.all(), true_del2z.all(), "Laplacian incorrect (+{:.0f} deg)".format(alpha))

    def test_pad_boundary(self):
        
        dx = 5
        dy = 5
        grid = self.dem._griddata

        padded_grid = np.pad(grid, pad_width=(dy, dx), mode='reflect')
        
        self.dem._pad_boundary(dx, dy)
        
        self.assertEqual(self.dem._griddata.all(), padded_grid.all(), "Grid padded incorrectly")


if __name__ == "__main__":
    unittest.main()
