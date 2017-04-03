
import unittest
import math
import numpy as np
from osgeo import gdal, osr, ogr


DEFAULT_EPSG = 32610 # UTM 10N

class WindowedTemplateTestCase(unittest.TestCase):





class ScarpTestCase(unittest.TestCase):


class MorletTestCase(unittest.TestCase):




def generate_synthetic_scarp(a, b, kt, nx, ny, de=1, sig2=0, theta=0):
    """ Generate DEM of synthetic scarp for testing """
    
    x = np.linspace(-nx/2, nx/2, num=nx)
    y = np.linspace(-ny/2, ny/2, num=ny)
    xv, yv = np.meshgrid(x, y)
    
    xrot = xv*np.cos(theta) + yv*np.sin(theta)
    yrot = -xv*np.sin(theta) + yv*np.cos(theta)
    

    z = -math.erf(yrot/(2*np.sqrt(kt))) + b*yrot
    z = z + sig2*np.random((ny, nx))

    synthetic = dem.DEMGrid()
    geo_tranform = (0, de, 0, 0, 0, -de) 
    projection = osr.SpatialReference()
    projection.ImportFromEPSG(DEFAULT_EPSG)

    synthetic._griddata = z
    synthetic._georef_info.geo_transform = geo_transform
    synthetic._georef_info.projection = projection
    synthetic._georef_info.dx = de 
    synthetic._georef_info.dy = de 
    synthetic._georef_info.nx = nx 
    synthetic._georef_info.ny = ny
    synthetic._georef_info.xllcenter = 0 
    synthetic._georef_info.yllcenter = 0 

    return synthetic


