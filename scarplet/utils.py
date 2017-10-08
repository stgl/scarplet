"""
Utility classes and funcitons for template matching framework.
"""

import dem
import numpy as np

from itertools import product

class BoundingBox(object):

    def __init__(self, lr, ul):

        self.lrx = lr[0]
        self.lry = lr[1]
        self.lr = lr

        self.ulx = ul[0]
        self.uly = ul[1]
        self.ul = ul

        self.llx = ul[0]
        self.lly = lr[1]
        self.ll = (self.llx, self.lly)

        self.urx = lr[0]
        self.ury = ul[1]
        self.ur = (self.urx, self.ury)

        self.corners = [self.ul, self.ll, self.ur, self.lr] 

    def contains(self, point):

        intersect_x = point[0] >= self.ulx and point[0] <= self.lrx
        intersect_y = point[1] >= self.lry and point[1] <= self.uly

        return intersect_x and intersect_y

    def intersects(self, bbox):
        
        for corner in bbox.corners:
            if self.contains(corner):
                return True

        return False

    def intersection(self, bbox):
        pass
       # if not self.intersects(bbox):
       #     raise ValueError("Bounding boxes do not intersect")

       # interior_points = []
       # for corner in bbox.corners:
       #     if self.contains(corner):
       #         interior_points.append(corner)
       # 
       # if len(interior_points) == 1:
       #     dists = [np.linalg.norm(interior_points[0] - x) for x in self.corners]
       #     idx = np.where(dists == np.min(dists))
       #     interior_points.append(self.corners[idx])

       # return BoundingBox(new_lr, new_ul)

def neighbors(filename, offset=2):
    x = int(filename[2:5])
    y = int(filename[6:10])
    offsets = product(np.arange(-offset + 1, offset), np.arange(-offset + 1, offset))
    filenames = [form_valid_filename(x + dx, y + dy) for dx, dy in offsets]
    return filenames

def form_valid_filename(x, y):
    return 'fg' + str(x) + '_' + str(y) + '.tif'

def pad_with_neighboring_values(filename, pad, data_dir='/media/rmsare/GALLIUMOS/data/ot_data/tif/2m/'):
    src_data = dem.DEMGrid(data_dir + filename)._griddata
    ny, nx = src_data.shape
    padded_shape = (ny + 2*pad, nx + 2*pad)
    dest_data = np.zeros(padded_shape)

    grids = neighbors(filename)
    for i, f in enumerate(grids):
        if i == 4:
            src_data = dem.DEMGrid(data_dir + filename)._griddata
            dest_data[pad:ny + pad, pad:nx + pad] = src_data
        else:
            if os.path.exists(data_dir + f):
                src_data = dem.DEMGrid(data_dir + f)._griddata
            else:
                src_data = np.nan * np.ones((ny, nx))

            if i == 0: # SW corner
                pad_values = src_data[0:pad, -pad:]
                dest_data[pad + ny:2*pad + ny, 0:pad] = pad_values 
            elif i == 1: # W edge 
                pad_values = src_data[:, -pad:]
                dest_data[pad:nx + pad, 0:pad] = pad_values 
            elif i == 2: # NW corner
                pad_values = src_data[-pad:, -pad:]
                dest_data[0:pad, 0:pad] = pad_values 
            elif i == 3: # S edge 
                pad_values = src_data[0:pad, :]
                dest_data[pad + ny:2*pad + ny, pad:pad + nx] = pad_values 
            elif i == 5: # N edge 
                pad_values = src_data[-pad:, :]
                dest_data[0:pad, pad:pad + nx] = pad_values 
            elif i == 6: # SE corner
                pad_values = src_data[0:pad, 0:pad]
                dest_data[pad + ny:2*pad + ny, pad + nx:2*pad + nx] = pad_values 
            elif i == 7: # E edge 
                pad_values = src_data[:, 0:pad]
                dest_data[pad:pad + ny, pad + nx:2*pad + nx] = pad_values 
            elif i == 8: # NE corner
                pad_values = src_data[-pad:, 0:pad]
                dest_data[0:pad, pad + ny: 2*pad + ny] = pad_values 

    return dest_data

