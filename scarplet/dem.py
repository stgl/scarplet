""" Classes for loading digital elevation models as numeric grids """

import os, sys

import matplotlib
import matplotlib.pyplot as plt

import numpy as np
import numexpr

from osgeo import gdal, gdalconst
import osr

sys.path.append('/usr/bin')
import gdal_merge

from utils import BoundingBox

sys.setrecursionlimit(10000)

FLOAT32_MIN = np.finfo(np.float32).min

GDAL_DRIVER_NAME = 'GTiff'


class CalculationMixin(object):

    def __init__(self):
        
        pass

    def _calculate_slope(self):
        
        dx = self._georef_info.dx
        dy = self._georef_info.dy

        PAD_DX = 2
        PAD_DY = 2

        self._pad_boundary(PAD_DX, PAD_DY)
        z_pad = self._griddata
        
        slope_x = (z_pad[1:-1, 2:] - z_pad[1:-1, :-2])/(2*dx)
        slope_y = (z_pad[2, 1:-1] - z_pad[:-2, 1:-1])/(2*dx)
        
        return slope_x, slope_y
    
    def _calculate_laplacian(self):
        
        return self._calculate_directional_laplacian(0)

    def _calculate_directional_laplacian(self, alpha):
 
        dx = self._georef_info.dx
        dy = self._georef_info.dy       
        z = self._griddata
        nan_idx = np.isnan(z)
        z[nan_idx] = 0
        
        dz_dx = np.diff(z, 1, 1)/dx
        d2z_dxdy = np.diff(dz_dx, 1, 0)/dx
        pad_x = np.zeros((d2z_dxdy.shape[0], 1))
        d2z_dxdy = np.hstack([pad_x, d2z_dxdy])
        pad_y = np.zeros((1, d2z_dxdy.shape[1]))
        d2z_dxdy = np.vstack([pad_y, d2z_dxdy])
        
        d2z_dx2 = np.diff(z, 2, 1)/dx**2
        pad_x = np.zeros((d2z_dx2.shape[0], 1))
        d2z_dx2 = np.hstack([pad_x, d2z_dx2, pad_x])

        d2z_dy2 = np.diff(z, 2, 0)/dy**2
        pad_y = np.zeros((1, d2z_dy2.shape[1]))
        d2z_dy2 = np.vstack([pad_y, d2z_dy2, pad_y])

        del2z = d2z_dx2*np.cos(alpha)**2 - 2*d2z_dxdy*np.sin(alpha)*np.cos(alpha) + d2z_dy2*np.sin(alpha)**2
        del2z[nan_idx] = np.nan 

        return del2z

    def _calculate_directional_laplacian_numexpr(self, alpha):

        dx = self._georef_info.dx
        dy = self._georef_info.dy       
        z = self._griddata
        nan_idx = np.isnan(z)
        z[nan_idx] = 0
        
        dz_dx = np.diff(z, 1, 1)/dx
        d2z_dxdy = np.diff(dz_dx, 1, 0)/dx
        pad_x = np.zeros((d2z_dxdy.shape[0], 1))
        d2z_dxdy = np.hstack([pad_x, d2z_dxdy])
        pad_y = np.zeros((1, d2z_dxdy.shape[1]))
        d2z_dxdy = np.vstack([pad_y, d2z_dxdy])
        
        d2z_dx2 = np.diff(z, 2, 1)/dx**2
        pad_x = np.zeros((d2z_dx2.shape[0], 1))
        d2z_dx2 = np.hstack([pad_x, d2z_dx2, pad_x])

        d2z_dy2 = np.diff(z, 2, 0)/dy**2
        pad_y = np.zeros((1, d2z_dy2.shape[1]))
        d2z_dy2 = np.vstack([pad_y, d2z_dy2, pad_y])

        del2z = numexpr.evaluate("d2z_dx2*cos(alpha)**2 - 2*d2z_dxdy*sin(alpha)*cos(alpha) + d2z_dy2*sin(alpha)**2")
        del2z[nan_idx] = np.nan 

        return del2z

    def _estimate_curvature_noiselevel(self):
        
        from scipy import ndimage

        angles = np.linspace(0, np.pi, num=180)

        m = [] 
        sd = []

        for alpha in angles:
            del2z = self._calculate_directional_laplacian(alpha)
            # TODO: determine bandpass range from original spectrum
            lowpass = ndimage.gaussian_filter(del2z, 100) 
            highpass = del2z - lowpass
            m.append(np.nanmean(highpass))
            sd.append(np.nanstd(highpass))

        return m, sd

    def _pad_boundary(self, dx, dy):

        #dx = np.round(dx/2)
        #dy = np.round(dy/2)

        #nx = self._georef_info.nx
        #ny = self._georef_info.ny

        #pad_x = np.zeros((ny, dx))
        #z_pad = np.hstack([pad_x, self._griddata, pad_x]) 
        #
        #nx += 2*dx 
        #
        #pad_y = np.zeros((dy, nx))
        #z_pad = np.vstack([pad_y, z_pad, pad_y]) 

        self._griddata = np.pad(self._griddata, pad_width=(dy, dx), mode='constant')

        nx, ny = self._griddata.shape
        
        self._georef_info.nx = nx
        self._georef_info.ny = ny
        self._georef_info.xllcenter -= dx
        self._georef_info.yllcenter -= dy
        self._griddata = z_pad 

class GDALMixin(object):
    pass


class GeorefInfo(object):

    def __init__(self):

        self.geo_transform = None
        self.projection = None
        self.xllcenter = None
        self.yllcenter = None
        self.dx = None
        self.dy = None
        self.nx = None 
        self.ny = None
        self.ulx = None
        self.uly = None
        self.lrx = None
        self.lry = None

#class GeographicMixin(object):
#    pass


class BaseSpatialGrid(GDALMixin):
    

    dtype = gdalconst.GDT_Float32 # TODO: detect and set dtype

    def __init__(self, filename=None):
        
        _georef_info = GeorefInfo()

        if filename is not None:
            self._georef_info = _georef_info # TODO: fix reference...
            self.load(filename)
            self.filename = filename
        else:
            self.filename = None
            self._georef_info = _georef_info # TODO: fix reference...
            self._griddata = np.empty((0,0))

    def is_contiguous(self, grid):

        return self.bbox.intersects(grid.bbox) 

    def merge(self, grid):

        if not self.is_contiguous(grid):
            raise ValueError("Grids are not contiguous")

        sys.argv = ['', self.filename, grid.filename]
        gdal_merge.main()
        merged_grid = BaseSpatialGrid('out.tif') 
        merged_grid._griddata[merged_grid._griddata == FLOAT32_MIN] = np.nan
        os.remove('out.tif')

        return merged_grid

    def plot(self, **kwargs):
        
        fig = plt.figure()
        ax = fig.add_subplot(1,1,1)
        ax.imshow(self._griddata, **kwargs)

    def save(self, filename): 

        ncols = self._georef_info.nx
        nrows = self._georef_info.ny

        x_origin = self._georef_info.xllcenter
        y_origin = self._georef_info.yllcenter

        driver = gdal.GetDriverByName(GDAL_DRIVER_NAME)
        out_raster = driver.Create(filename, ncols, nrows, 1, self.dtype)
        out_raster.SetGeoTransform(self._georef_info.geo_transform)
        out_band = out_raster.GetRasterBand(1)
        out_band.WriteArray(self._griddata)

        out_raster.SetProjection(self._georef_info.projection)
        out_band.FlushCache()

    def load(self, filename): #TODO: make this a class method?
        
        self.label = filename.split('/')[-1].split('.')[0]

        gdal_dataset = gdal.Open(filename)
        band = gdal_dataset.GetRasterBand(1)
        nodata = band.GetNoDataValue()
        self._griddata = band.ReadAsArray() 

        if nodata is not None:
            nodata_index = np.where(self._griddata == nodata)
            if self.dtype is not np.uint8:
                self._griddata[nodata_index] = np.NAN

        geo_transform = gdal_dataset.GetGeoTransform()
        projection = gdal_dataset.GetProjection()
        nx = gdal_dataset.RasterXSize
        ny = gdal_dataset.RasterYSize

        self._georef_info.geo_transform = geo_transform
        self._georef_info.projection = projection
        self._georef_info.dx = self._georef_info.geo_transform[1]
        self._georef_info.dy = self._georef_info.geo_transform[5]
        self._georef_info.nx = nx 
        self._georef_info.ny = ny
        self._georef_info.xllcenter = self._georef_info.geo_transform[0] + self._georef_info.dx
        self._georef_info.yllcenter = self._georef_info.geo_transform[3] - (self._georef_info.ny+1)*np.abs(self._georef_info.dy)

        self._georef_info.ulx = self._georef_info.geo_transform[0]
        self._georef_info.uly = self._georef_info.geo_transform[3]
        self._georef_info.lrx = self._georef_info.geo_transform[0] + self._georef_info.dx*self._georef_info.nx
        self._georef_info.lry = self._georef_info.geo_transform[3] + self._georef_info.dy*self._georef_info.ny
        
        self.bbox = BoundingBox((self._georef_info.lrx, self._georef_info.lry), (self._georef_info.ulx, self._georef_info.uly))

class DEMGrid(CalculationMixin, BaseSpatialGrid):
    
    # TODO: fix inheritance to use BaseSpatialGrid init
    # XXX: This is here for Python 2.7 compatibility for now
    def __init__(self, filename=None):

        _georef_info = GeorefInfo()

        if filename is not None:
            self._georef_info = _georef_info 
            self.load(filename)
            self._griddata[self._griddata == FLOAT32_MIN] = np.nan
            self.filename = filename
        else:
            self.filename = None 
            self.label = ''
            self._georef_info = _georef_info 
            self._griddata = np.empty((0,0))

    def _fill_nodata(self):
        pass


class Hillshade(BaseSpatialGrid):
    
    def __init__(self, dem):
        
        self._georef_info = dem._georef_info 
        self._griddata = dem._griddata
        self._hillshade = None

    def plot(self, az=315, elev=45):
  
        ls = matplotlib.colors.LightSource(azdeg=az, altdeg=elev)
        self._hillshade = ls.hillshade(self._griddata, vert_exag=1, dx=self._georef_info.dx, dy=self._georef_info.dy)      
        plt.imshow(self._hillshade, alpha=1, cmap='gray', origin='lower')
        plt.show()

