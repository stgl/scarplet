""" Classes for loading digital elevation models as numeric grids """

import os, sys
import numpy as np
from osgeo import gdal, gdalconst
import osr

GDAL_DRIVER_NAME = 'GTiff'

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


class BaseSpatialGrid(GDALMixin):
    

    dtype = gdalconst.GDT_Float32
    
    _georef_info = GeorefInfo()

    def save(self, filename):

        ncols = self._georef_info.nx
        nrows = self._georef_info.ny
        dx = self._georef_info.dx
        if self._georef_info.dy is not None:
            dy = self._georef_info.dy
        else:
            dy = dx

        x_origin = self._georef_info.xllcenter
        y_origin = self._georef_info.yllcenter

        driver = gdal.GetDriverByName(GDAL_DRIVER_NAME)
        out_raster = driver.Create(filename, ncols, nrows, 1, dtype)
        out_raster.SetGeoTransform((x_origin, dx, 0, y_origin, dy))
        out_band = out_raster.GetRasterBand(1)
        out_band.WriteArray(self._griddata)

        srs = osr.SpatialReference()
        srs.ImportFromEPSG(EPSG_CODE)
        out_raster.SetProjection(srs.ExportToWkt())
        out_band.FlushCache()

    @classmethod
    def load(cls, filename):

        return_object = cls()

        gdal_dataset = gdal.Open(filename)
        band = gdal_dataset.GetRasterBand(1)
        nodata = band.GetNoDataValue()
        return_object._griddata = band.ReadAsArray() 

        if nodata is not None:
            nodata_index = np.where(return_object._griddata == nodata)
            if cls.dtype is not np.uint8:
                return_object._griddata[nodata_index] = np.NAN

        geo_transform = gdal_dataset.GetGeoTransform()
        nx = gdal_dataset.RasterXSize
        ny = gdal_dataset.RasterYSize

        return_object._georef_info.geo_transform = geo_transform
        return_object._georef_info.dx = return_object._georef_info.geo_transform[1]
        return_object._georef_info.xllcenter = return_object._georef_info.geo_transform[0] + return_object._georef_info.dx
        return_object._georef_info.yllcenter = return_object._georef_info.geo_transform[3] - return_object._georef_info.dy
        return_object._georef_info.nx = nx 
        return_object._georef_info.ny = ny

        return return_object


class DEMGrid(BaseSpatialGrid, CalculationMixin):
    pass


class GeorefInfo(object):


    def __init__(self):
        self.geo_transform = 0
        self.projection = 0
        self,xllcenter = 0
        self.yllcenter = 0
        self.dx = 0
        self.dy = 0
        self.nx = 0
        self.ny = 0

