import os
import sys
import filecmp
import numpy as np
import unittest

import matplotlib
import matplotlib.pyplot as plt

from context import scarplet
from scarplet import dem


TESTDATA_FILENAME = os.path.join(os.path.dirname(__file__), 'data/big_basin.tif')

CONTIGUOUS_FILENAMES = [os.path.join(os.path.dirname(__file__), 'data/contig/' + f) for f in os.listdir('tests/data/contig')] 
NONCONTIGUOUS_FILENAMES = [os.path.join(os.path.dirname(__file__), 'data/noncontig/' + f) for f in os.listdir('tests/data/noncontig')] 
MERGE_FILENAME = os.path.join(os.path.dirname(__file__), 'data/contig/mindego_hill.tif')


class CalculationMethodsTestCase(unittest.TestCase):
    
    
    def setUp(self):
        
        self.dem = dem.DEMGrid(TESTDATA_FILENAME)

    @unittest.skip("")
    def test_calculate_slope(self):

        sx, sy = self.dem._calculate_slope()
        true_sx, true_sy = np.load('data/big_basin_sxsy.npy')

    @unittest.skip("")
    def test_calculate_laplacian(self):

        del2z = self.dem._calculate_laplacian()
        true_del2z = np.load('data/big_basin_del2z.npy')
    
    @unittest.skip("")
    def test_calculate_directional_laplacian(self):
        
        alpha = np.pi/4
        del2z = self.dem._calculate_directional_laplacian(alpha)
        true_del2z_45 = np.load('data/big_basin_del2z_45.npy')

    @unittest.skip("")
    def test_pad_boundary(self):
        
        dx = 5
        dy = 5
        grid = self.dem._griddata

        pad_x = np.zeros((self.dem._georef_info.ny, np.round(dx/2)))
        pad_y = np.zeros((np.round(dy/2), self.dem._georef_info.nx + 2*np.round(dx/2)))
        padded_grid = np.vstack([pad_y, np.hstack([pad_x, self.dem._griddata, pad_x]), pad_y])
        
        self.dem._pad_boundary(dx, dy)
        
        self.assertEqual(self.dem._griddata.all(), padded_grid.all(), "Grid padded incorrectly")



class BaseSpatialGridTestCase(unittest.TestCase):


    def setUp(self):

        self.dem = dem.BaseSpatialGrid(TESTDATA_FILENAME)

    def test_is_contiguous(self):

        with self.subTest():
            self.assertTrue(self.dem.is_contiguous(self.dem), "Grid incorrectly flagged as not contiguous with itself")
        
        for f in CONTIGUOUS_FILENAMES:
            with self.subTest(f=f):
                adjacent_grid = dem.BaseSpatialGrid(f)
                self.assertTrue(self.dem.is_contiguous(adjacent_grid), "Adjacent grids incorrectly flagged as not contiguous")
        
        for f in NONCONTIGUOUS_FILENAMES:
            with self.subTest(f=f):
                nonadjacent_grid = dem.BaseSpatialGrid(f)
                self.assertFalse(self.dem.is_contiguous(nonadjacent_grid), "Non-adjacent grids incorrectly flagged as contiguous")

    def test_merge(self):

        adjacent_grid = dem.BaseSpatialGrid(MERGE_FILENAME)
        test_grid = self.dem.merge(adjacent_grid)
        true_grid = dem.BaseSpatialGrid('tests/data/merged.tif')
        
        self.assertEqual(test_grid._griddata.all(), true_grid._griddata.all(), "Grids merged incorrectly")

    @unittest.skip("Skipping plot test until master image generated")
    #@image_comparison(baseline_images=['plot_gist_earth'], extensions=['png'])
    def test_plot(self):

        self.dem.plot(cmap='gist_earth')

    @unittest.skip("Skipping save test until dtype detect is implemented")
    def test_save(self): # known failure: datatype different in saved test file
        
        this_file = os.path.join(os.path.dirname(__file__), 'data/big_basin_test.tif')
        test_file = TESTDATA_FILENAME
        
        self.dem.save(this_file)

        self.assertTrue(filecmp.cmp(this_file, test_file, shallow=False), "GeoTIFF saved incorrectly")

if __name__ == "__main__":
    unittest.main()
