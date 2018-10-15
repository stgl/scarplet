# -*- coding: utf-8
""" Classes for loading digital elevation models as numeric grids """

import numexpr
import numpy as np
import os
import sys

import matplotlib
import matplotlib.pyplot as plt

from copy import copy
from osgeo import gdal, gdalconst

from rasterio.fill import fillnodata

from scarplet.utils import BoundingBox

sys.path.append('/usr/bin')
try:
    import gdal_merge
except ImportError as e:
    print('ImportError: ' + str(e))
    print('Can\'t import gdal_merge. GDAL binaries may not be installed.')


sys.setrecursionlimit(10000)

FLOAT32_MIN = np.finfo(np.float32).min
GDAL_DRIVER_NAME = 'GTiff'


class CalculationMixin(object):
    """Mix-in class for grid calculations"""

    def __init__(self):

        pass

    def _calculate_slope(self):
        """Calculate gradient of grid in x and y directions.

        Pads boundary so as to return slope grids of same size as object's
        grid data

        Returns
        -------
            slope_x : numpy array
                slope in x direction
            slope_y : numpy array
                slope in y direction
        """

        dx = self._georef_info.dx
        dy = self._georef_info.dy

        PAD_DX = 2
        PAD_DY = 2

        self._pad_boundary(PAD_DX, PAD_DY)
        z_pad = self._griddata

        slope_x = (z_pad[1:-1, 2:] - z_pad[1:-1, :-2]) / (2 * dx)
        slope_y = (z_pad[2:, 1:-1] - z_pad[:-2, 1:-1]) / (2 * dy)

        return slope_x, slope_y

    def _calculate_laplacian(self):
        """Calculate curvature of grid in y direction.
        """

        return self._calculate_directional_laplacian(0)

    def _calculate_directional_laplacian(self, alpha):
        """Calculate curvature of grid in arbitrary direction.

        Parameters
        ----------
            alpha : float
                direction angle (azimuth) in radians. 0 is north or y-axis.

        Returns
        -------
            del2s : numpy array
                grid of curvature values
        """

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

        del2z = d2z_dx2 * np.cos(alpha) ** 2 - 2 * d2z_dxdy * np.sin(alpha) \
            * np.cos(alpha) + d2z_dy2 * np.sin(alpha) ** 2
        del2z[nan_idx] = np.nan

        return del2z

    def _calculate_directional_laplacian_numexpr(self, alpha):
        """Calculate curvature of grid in arbitrary direction.

        Optimized with numexpr expressions.

        Parameters
        ----------
            alpha : float
                direction angle (azimuth) in radians. 0 is north or y-axis.

        Returns
        -------
            del2s : numpyarray
                grid of curvature values
        """

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

        del2z = numexpr.evaluate("d2z_dx2*cos(alpha)**2 - \
                2*d2z_dxdy*sin(alpha)*cos(alpha) + d2z_dy2*sin(alpha)**2")
        del2z[nan_idx] = np.nan

        return del2z

    def _estimate_curvature_noiselevel(self):
        """Estimate noise level in curvature of grid as a function of direction.

        Returns
        -------
            angles : numpy array
                array of orientations (azimuths) in radians
            mean : float
                array of mean curvature in correponding direction
            sd : float
                array of curvature standard deviation in correponding direction
        """

        from scipy import ndimage

        angles = np.linspace(0, np.pi, num=180)

        mean = []
        sd = []

        for alpha in angles:
            del2z = self._calculate_directional_laplacian(alpha)
            lowpass = ndimage.gaussian_filter(del2z, 100)
            highpass = del2z - lowpass
            mean.append(np.nanmean(highpass))
            sd.append(np.nanstd(highpass))

        return angles, mean, sd

    def _pad_boundary(self, dx, dy):
        """Pad grid boundary with reflected boundary conditions.
        """

        self._griddata = np.pad(self._griddata, pad_width=(dy, dx),
                                mode='reflect')
        self.padded = True
        self.pad_dx = dx
        self.pad_dy = dy

        ny, nx = self._griddata.shape

        self._georef_info.nx = nx
        self._georef_info.ny = ny
        self._georef_info.xllcenter -= dx
        self._georef_info.yllcenter -= dy


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


class BaseSpatialGrid(GDALMixin):
    """Base class for spatial grid"""

    dtype = gdalconst.GDT_Float32

    def __init__(self, filename=None):

        _georef_info = GeorefInfo()

        if filename is not None:
            self._georef_info = _georef_info
            self.load(filename)
            self.filename = filename
        else:
            self.filename = None
            self._georef_info = _georef_info
            self._griddata = np.empty((0, 0))

    def is_contiguous(self, grid):
        """Returns true if grids are contiguous or overlap

        Parameters
        ----------
            grid : BaseSpatialGrid
        """

        return self.bbox.intersects(grid.bbox)

    def merge(self, grid):
        """Merge this grid with another BaseSpatialGrid.

        Wrapper argound gdal_merge.py.

        Parameters
        ----------
            grid : BaseSpatialGrid

        Returns
        -------
            merged_grid : BaseSpatialGrid
        """

        if not self.is_contiguous(grid):
            raise ValueError("ValueError: Grids are not contiguous")

        # XXX: this is hacky, eventually implement as native GDAL
        sys.argv = ['', self.filename, grid.filename]
        gdal_merge.main()
        merged_grid = BaseSpatialGrid('out.tif')
        merged_grid._griddata[merged_grid._griddata == FLOAT32_MIN] = np.nan
        os.remove('out.tif')

        return merged_grid

    def plot(self, **kwargs):
        """Plot grid data

        Keyword args:
            Any valid keyword argument for matplotlib.pyplot.imshow
        """

        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.imshow(self._griddata, **kwargs)

    def save(self, filename):
        """Save grid as georeferenced TIFF
        """

        ncols = self._georef_info.nx
        nrows = self._georef_info.ny

        driver = gdal.GetDriverByName(GDAL_DRIVER_NAME)
        out_raster = driver.Create(filename, ncols, nrows, 1, self.dtype)
        out_raster.SetGeoTransform(self._georef_info.geo_transform)
        out_band = out_raster.GetRasterBand(1)
        out_band.WriteArray(self._griddata)

        proj = self._georef_info.projection.ExportToWkt()
        out_raster.SetProjection(proj)
        out_band.FlushCache()

    def load(self, filename):
        """Load grid from file
        """

        self.label = filename.split('/')[-1].split('.')[0]

        gdal_dataset = gdal.Open(filename)
        band = gdal_dataset.GetRasterBand(1)
        nodata = band.GetNoDataValue()
        self._griddata = band.ReadAsArray().astype(float)

        if nodata is not None:
            nodata_index = np.where(self._griddata == nodata)
            if self.dtype is not np.uint8:
                self._griddata[nodata_index] = np.nan

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
        self._georef_info.xllcenter = self._georef_info.geo_transform[0] \
            + self._georef_info.dx
        self._georef_info.yllcenter = self._georef_info.geo_transform[3] \
            - (self._georef_info.ny+1) \
            * np.abs(self._georef_info.dy)

        self._georef_info.ulx = self._georef_info.geo_transform[0]
        self._georef_info.uly = self._georef_info.geo_transform[3]
        self._georef_info.lrx = self._georef_info.geo_transform[0] \
            + self._georef_info.dx*self._georef_info.nx
        self._georef_info.lry = self._georef_info.geo_transform[3] \
            + self._georef_info.dy*self._georef_info.ny
        self.bbox = BoundingBox((self._georef_info.lrx, self._georef_info.lry),
                                (self._georef_info.ulx, self._georef_info.uly))


class DEMGrid(CalculationMixin, BaseSpatialGrid):
    """Class representing grid of elevation values"""

    def __init__(self, filename=None):

        _georef_info = GeorefInfo()

        if filename is not None:
            self._georef_info = _georef_info
            self.load(filename)
            self._griddata[self._griddata == FLOAT32_MIN] = np.nan
            self.nodata_value = np.nan
            self.filename = filename.split('/')[-1]
            self.shape = self._griddata.shape
            self.is_interpolated = False
        else:
            self.filename = None
            self.label = ''
            self.shape = (0, 0)
            self._georef_info = _georef_info
            self._griddata = np.empty((0, 0))
            self.is_interpolated = False

    def plot(self, color=True, **kwargs):
        fig, ax = plt.subplots(1, 1, **kwargs)

        hs = Hillshade(self)
        hs.plot()

        if color:
            im = ax.imshow(self._griddata, alpha=0.75, cmap='terrain')
            plt.colorbar(im, ax=ax, shrink=0.75, label='Elevation')

        ax.tick_params(direction='in')
        ax.set_xlabel('x')
        ax.set_ylabel('y')

    def _fill_nodata(self):
        """Fill nodata values in elevation grid by interpolation.

        Wrapper around GDAL/rasterio's FillNoData, fillnodata methods
        """

        if ~np.isnan(self.nodata_value):
            nodata_mask = self._griddata == self.nodata_value
        else:
            nodata_mask = np.isnan(self._griddata)
        self.nodata_mask = nodata_mask

        # XXX: GDAL (or rasterio) FillNoData takes mask with 0s at nodata
        num_nodata = np.sum(nodata_mask)
        prev_nodata = np.nan
        while num_nodata > 0 or num_nodata == prev_nodata:
            mask = np.isnan(self._griddata)
            col_nodata = np.sum(mask, axis=0).max()
            row_nodata = np.sum(mask, axis=1).max()
            dist = max(row_nodata, col_nodata) / 2
            self._griddata = fillnodata(self._griddata,
                                        mask=~mask,
                                        max_search_distance=dist)
            prev_nodata = copy(num_nodata)
            num_nodata = np.sum(np.isnan(self._griddata))

        self.is_interpolated = True

    def _fill_nodata_with_edge_values(self):
        """Fill nodata values using swath edge values by row,"""

        if ~np.isnan(self.nodata_value):
            nodata_mask = self._griddata == self.nodata_value
        else:
            nodata_mask = np.isnan(self._griddata)
        self.nodata_mask = nodata_mask

        for row in self._griddata:
            idx = np.where(np.isnan(row)).min()
            fill_value = row[idx]
            row[np.isnan(row)] = fill_value

        self.is_interpolated = True


class Hillshade(BaseSpatialGrid):
    """Class representing hillshade of DEM"""

    def __init__(self, dem):
        """Load DEMGrid object as Hillshade
        """

        self._georef_info = dem._georef_info
        self._griddata = dem._griddata
        self._hillshade = None

    def plot(self, az=315, elev=45):
        """Plot hillshade

        Paramaters
        ----------
            az : float
                azimuth of light source in degrees
            elev : float
                elevation angle of light source in degrees
        """

        ax = plt.gca()
        ls = matplotlib.colors.LightSource(azdeg=az, altdeg=elev)
        self._hillshade = ls.hillshade(self._griddata, vert_exag=1,
                                       dx=self._georef_info.dx,
                                       dy=self._georef_info.dy)
        ax.imshow(self._hillshade, alpha=1, cmap='gray', origin='lower')
