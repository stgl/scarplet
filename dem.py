""" Classes for loading digital elevation models as numeric grids """

import os, sys
import numpy as np
from osgeo import gdal, gdal_const

class CalculationMixin(object):

    def _caclulate_slope(self):
        PAD_DX = 2
        PAD_DY = 2

        z_pad = self._pad_boundary(PAD_DX, PAD_DY)
        slope_x = (z_pad[1:-1, 2:] - z_pad[1:-1, :-2])/(2*self.dx)
        slope_y = (z_pad[2, 1:-1] - z_pad[:-2, 1:-1])/(2*self.dx)

        return slope_x, slope_y
    
    def _calculate_laplacian(self):
        return self._calculate_directional_laplacian(0)

    def _calculate_directional_laplacian(self, alpha):
        dz_dx = np.diff(self._griddata, 1, 2)/self.dx
        d2z_dxdy = np.diff(dz_dx, 1, 1)/self.dx
        
        d2z_dx2 = np.diff(self._griddata, 1, 1)/self.dx**2
        d2z_dy2 = np.diff(self._griddata, 2, 1)/self.dy**2

        del2z = d2z_dx2*np.cos(alpha)**2 - 2*d2z_dxdy*np.sin(alpha)*np.cos(alpha) + d2z_dy2*np.sin(alpha)**2
        
        return del2z

    def _pad_boundary(self, dx, dy):
        pad_x = np.zeros((self.ny, np.round(dx/2)))
        self._griddata = np.hstack([pad_x, self._griddata, pad_x]) 
        
        self.nx += 2*np.round(dx/2) 
        self.ny += 2*np.round(dy/2) 
        
        pad_y = np.zeros((np.round(dy/2), self.nx))
        self._griddata = np.vstack([pad_y, self._griddata, pad_y]) 

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
