import dem
import numpy as np
import scarplet as sl

from osgeo import gdal, osr, ogr
import matplotlib.pyplot as plt
from matplotlib import cm

from scipy.special import erf

from WindowedTemplate import Scarp, ShiftedLeftFacingUpperBreakScarp

DEFAULT_EPSG = 32610 # UTM 10N


def generate_synthetic_scarp(a, b, kt, x_max, y_max, de=1, sig2=0, theta=0):
    """ Generate DEM of synthetic scarp for testing """
    
    nx = int(2 * x_max / de)
    ny = int(2 * y_max / de)
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

def fit_plot_offset(data, dx, ax, color):

    res = sl.calculate_best_fit_parameters_serial(data, ShiftedLeftFacingUpperBreakScarp, scale, dx=dx, dy=0)
    ax[1].plot(res[0][20, :], '-', color=color)
    ax[2].plot(res[1][20, :], '-', color=color)
    ax[3].plot(res[2][20, :], '-', color=color)
    ax[4].plot(res[3][20, :], '-', color=color)

    idx = np.where(res[3][20, :] == np.nanmax(res[3][20, :]))[0][0]
    ax[0].plot(idx, data._griddata[20, idx], 'k*', ms=20)
    ax[2].plot(idx, res[0][20, idx], '*', color=color, mec=color, ms=20)
    ax[2].plot(idx, res[1][20, idx], '*', color=color, mec=color, ms=20)
    ax[3].plot(idx, res[2][20, idx], '*', color=color, mec=color, ms=20)
    ax[4].plot(idx, res[3][20, idx], '*', color=color, mec=color, ms=20)

    return idx, res[0][20, idx], res[1][20, idx], res[2][20, idx], res[3][20, idx]


scale = 10

#data = generate_synthetic_scarp(5, 0, 10, 20, 20)
#data._griddata = np.fliplr(data._griddata.T)

data = generate_synthetic_scarp(5, -0.05, 10, 20, 20)
data._griddata[data._griddata < 0] = 0

data._griddata = np.fliplr(data._griddata.T)

results = []

fig, ax = plt.subplots(5, 1, figsize=(5, 20))
ax[0].plot(data._griddata[20, :], 'k-')

res = sl.calculate_best_fit_parameters_serial(data, Scarp, scale)
ax[1].plot(res[0][20, :], 'k-')
ax[2].plot(res[1][20, :], 'k-')
ax[3].plot(res[2][20, :], 'k-')
ax[4].plot(res[3][20, :], 'k-')

idx = np.where(res[3][20, :] == np.nanmax(res[3][20, :]))[0][0]
ax[0].plot(idx, data._griddata[20, idx], 'k*', ms=20)
ax[1].plot(idx, res[0][20, idx], 'k*', ms=20)
ax[2].plot(idx, res[1][20, idx], 'k*', ms=20)
ax[3].plot(idx, res[2][20, idx], 'k*', ms=20)
ax[4].plot(idx, res[3][20, idx], 'k*', ms=20)

results.append([0, idx, res[0][20, idx], res[1][20, idx], res[2][20, idx], res[3][20, idx]])

cmap = cm.get_cmap('RdBu_r')
offsets = np.arange(-10, 11, 1)
n = len(offsets)
for i, dx in enumerate(offsets):
    color = cmap(i / n)
    idx, amp, kt, ang, snr = fit_plot_offset(data, dx, ax, color)
    results.append([dx, idx, amp, kt, ang, snr])

for row in results:
    print('{}\t{:.2f}\t{:.2f}\t{:.2f}\t{:.2f}\t{:.2f}'.format(*row))
