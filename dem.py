""" Classes for loading digital elevation models as numeric grids """

import os, sys
import numpy as np
from osgeo import gdal, gdal_const

class CalculationMixin(object):
    def _caclulate_slope(self, dx):
        PAD_DX = 2
        PAD_DY = 2

        grid = self._pad_boundary(PAD_DX, PAD_DY)
        slope_x = (grid[1:-1, 2:] - grid[1:-1, :-2])/(2*dx)
        slope_y = (grid[2, 1:-1] - grid[:-2, 1:-1])/(2*dx)

        return slope_x, slope_y
    
    def _calculate_laplacian(self, dx):
    
    def _calculate_directional_laplacian(self, dx, alpha):

    def _detrend_grid(self, dx):
        

    def _pad_boundary(self, dx, dy):

        return padded_grid

class GDALMixin(object):
    pass

class GeorefInfo(object):
    pass

#class GeographicMixin(object):
#    pass

class BaseSpatialGrid(GDALMixin):
    pass

class DEMGrid(BaseSpatialGrid, CalculationMixin):
    pass
