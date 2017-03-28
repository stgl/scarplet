import unittest
import matplotlib
import matplotplib.pyplot as plt
from matplotlib.testing.decorators import image_comparison
import numpy as np
import filecmp

TESTDATA_FILENAME = os.path.join(os.path.dirname(__file__), 'data/big_basin.tif')


class CalculationMethodsTestCase(unittest.TestCase):
    
    
    def setUp(self):
        
        self.dem = DEMGrid(TESTDATA_FILENAME)

    def test_calculate_slope(self):

        sx, sy = self.dem._calculate_slope()

    def test_calculate_laplacian(self):

        del2z = self.dem._calculate_lapalacian()
    
    def test_calculate_directional_laplacian(self):
        
        alpha = np.pi/4
        del2z = self.dem._calculate_lapalacian(alpha)

    def test_pad_boundary(self):
        
        dx = 5
        dy = 5
        grid = self.dem._griddata

        pad_x = np.zeros((self.ny, np.round(dx/2))
        pad_y = np.zeros((self.nx + 2*np.round(dx/2), np.round(dy/2)))
        padgrid = np.vstack([pad_y, np.hstack([pad_x, self.dem._griddata, pad_x]), pad_y]])
        self.dem._pad_boundary(dx, dy)
        
        assertEqual(self.dem.grid, padgrid, 'Grid padded incorrectly')


class BaseSpatialGridTestCase(unittest.TestCase):


    def setUp(self):

        self.dem = BaseSpatialGrid(TESTDATA_FILENAME)

    @image_comparison(baseline_images=['plot_gist_earth'], extensions=['png'])
    def test_plot(self):

        self.plot(cmap='gist_earth')

    def test_save(self):
        
        os.remove('test.tif')
        self.save('test.tif')
        
        this_file = os.path.join(os.path.dirname(__file__), 'test.tif')
        test_file = TESTDATA_FILENAME

        self.assertTrue(filecmp.cmp(this_file, test_file, shallow=False), 'GeoTIFF saved incorrectly')

