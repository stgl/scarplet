""" Classes for loading digital elevation models as numeric grids """

import os, sys
import numpy as np
from osgeo import gdal, gdal_const

class CalculationMixin(object):
    def _caclulate_slope(self, dx):
        PAD_DX = 2
        PAD_DY = 2

        z = self._griddata
        z_pad = self._pad_boundary(PAD_DX, PAD_DY)
        slope_x = (z_pad[1:-1, 2:] - z_pad[1:-1, :-2])/(2*dx)
        slope_y = (z_pad[2, 1:-1] - z_pad[:-2, 1:-1])/(2*dx)

        return slope_x, slope_y
    
    def _calculate_laplacian(self, dx):
    
    def _calculate_directional_laplacian(self, dx, alpha):

    def _pad_boundary(self, dx, dy):

class GDALMixin(object):
    pass

class GeorefInfo(object):
    pass

#class GeographicMixin(object):
#    pass

class BaseGrid(GDALMixin):
    pass

class DEMGrid(BaseGrid, CalculationMixin):
    pass
