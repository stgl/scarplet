
import dem
import unittest
import numpy as np
from scipy.special import erf
from osgeo import gdal, osr, ogr

DEFAULT_EPSG = 32610 # UTM 10N


class WindowedTemplateTestCase(unittest.TestCase):
    pass    


class ScarpTestCase(unittest.TestCase):
    pass

class MorletTestCase(unittest.TestCase):
    pass


def generate_synthetic_scarp(a, b, kt, x_max, y_max, de=1, sig2=0, theta=0):
    """ Generate DEM of synthetic scarp for testing """
    
    nx = 2*x_max/de
    ny = 2*y_max/de
    x = np.linspace(-x_max, x_max, num=nx)
    y = np.linspace(-y_max, y_max, num=ny)
    x, y = np.meshgrid(x, y)
    
    xrot = x*np.cos(theta) + y*np.sin(theta)
    yrot = -x*np.sin(theta) + y*np.cos(theta)

    z = -erf(yrot/(2*np.sqrt(kt))) + b*yrot
    z = z + sig2*np.random.randn(ny, nx)

    return set_up_grid(z, de) 

def set_up_grid(data, de):

    ny, nx = data.shape
    synthetic = dem.DEMGrid()
    geo_transform = (0, de, 0, 0, 0, -de) 
    projection = osr.SpatialReference()
    projection.ImportFromEPSG(DEFAULT_EPSG)

    synthetic._griddata = data 
    synthetic._georef_info.geo_transform = geo_transform
    synthetic._georef_info.projection = projection
    synthetic._georef_info.dx = de 
    synthetic._georef_info.dy = de 
    synthetic._georef_info.nx = nx 
    synthetic._georef_info.ny = ny
    synthetic._georef_info.xllcenter = 0 
    synthetic._georef_info.yllcenter = 0 

    return synthetic
