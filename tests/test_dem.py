import unittest
import numpy as np

class CalculationMethodsTestCase(unittest.TestCase):
    def setUp(self):
        self.dem = DEMGrid()

    def test_calculate_slope(self):
        sx, sy = self.dem._calculate_slope()

    def test_calculate_laplacian(self):
        del2z = self.dem._calculate_lapalacian()
    
    def test_calculate_directional_laplacian(self):
        alpha = np.pi/4
        del2z = self.dem._calculate_lapalacian(alpha)

    def test_pad_boundary(self):
        dx = 4
        dy = 4
        grid = self.dem._griddata

        pad_x = np.zeros((self.ny, dx/2))
        pad_y = np.zeros((self.nx + dx, dy/2))
        padgrid = np.vstack([pad_y, np.hstack([pad_x, self.dem._griddata, pad_x]), pad_y]])
        self.dem._pad_boundary(dx, dy)
        
        assertEqual(self.dem.grid, padgrid, 'Grid padded incorrectly (dx = 2, dy = 2)')
        
        dx = 5
        dy = 5
        grid = self.dem._griddata

        pad_x = np.zeros((self.ny, np.round(dx/2))
        pad_y = np.zeros((self.nx + 2*np.round(dx/2), np.round(dy/2)))
        padgrid = np.vstack([pad_y, np.hstack([pad_x, self.dem._griddata, pad_x]), pad_y]])
        self.dem._pad_boundary(dx, dy)
        
        assertEqual(self.dem.grid, padgrid, 'Grid padded incorrectly (dx = 5, dy = 5)')
