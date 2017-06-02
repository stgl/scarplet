"""
Tools for downloading and stitching DEM rasters from OpenTopography holding
"""

import os, sys

import requests
import urllib
from urllib2 import Request

from bs4 import BeautifulSoup

from osgeo import gdal, ogr, osr

sys.path.append('/usr/bin')
import gdal_merge

#def download(filename):

def download_directory(url, working_dir='/media/rmsare/data/ot_data/'):
    s = url.split('/')
    dir_name = working_dir + s[-2]
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
        file_names = list_files_from_url(url)
        for fn in file_names:
            if not os.path.exists(os.path.join(dir_name, fn)):
                urllib.urlretrieve(os.path.join(url, fn), os.path.join(dir_name, fn))

def find_matching_files(dataset_name, nx, ny, working_dir='data/'):
    """
    Find matching filenames by NCAL survey naming conventions.
    Survey data are named by the convention:

    ccXXX_YYYY.fmt

    where:  - "cc" is a data code ('u' for unfiltered, 'fg' for filtered ground 
              returns only, etc)
            - "XXX" and "YYYY" are the most siginificant digits of the data's
              lower left corner (XXX000, YYYY000) in UTM 10N coordinate system

    directories for gridded data use the convention "ccXXX_YYYY/"
    """
    s = dataset_name.split('_')
    llx = int(s[0][2:5])*1000
    lly = int(s[1][0:4])*1000

    code = 'fg'
    names = [form_dataset_name(code, llx + dx*1000, lly + dy*1000) 
                     for dx in range(-nx,nx) for dy in range(-ny,ny)]
    
    # TODO: find a Pythonic way to do this
    matching_names = []
    for fn in names:
        if os.path.exists(os.path.join(working_dir, fn)):
            matching_names.append(fn)

    return matching_names

def form_dataset_name(code, llx, lly):
    return code + str(llx / 1000) + '_' + str(lly / 1000)

def merge_grids_from_names(filenames, outfilename='merged.tif', nodata_value='-9999'):
    # TODO: fix gdal_merge argv
    #sys.argv = ['-o', outfilename, '-init', nodata_value, '-a_nodata', nodata_value] + filenames
    sys.argv = filenames
    gdal_merge.main()

def list_files_from_url(url):
    url = url.replace(' ', '%20')
    request = Request(url)
    page = requests.get(url).text 
    soup = BeautifulSoup(page, 'html.parser')
    links = soup.find_all('a')
    file_names = []

    for link in links:
        fn = link.get('href')
        if fn[0] != '.':
            file_names.append(fn)
    
    return file_names

def list_folders_from_url(url):
    request = Request(url)
    page = requests.get(url).text 
    soup = BeautifulSoup(page, 'html.parser')
    links = soup.find_all('a')
    file_names = []

    for link in links:
        fn = link.get('href')
        if fn[-1] == '/' and fn[0] != '.':
            file_names.append(fn)
    
    return file_names

class file_info:
    """ A class holding information abotu a GDAL file.
        Designed after gdal_merge.py """

    def init_from_name(self, filename):
        f = gdal.Open(filename)

        self.filename = filename
        self.xsize = f.RasterXSize
        self.ysize = f.RasterYSize
        self.projection = f.GetProjection()
        self.geotransform = f.GetGeoTransform()

        self.ulx = self.geotransform[0]
        self.uly = self.geotransform[3]
        self.lrx = self.geotransform[0] + self.geotransform[1]*self.xsize
        self.lry = self.geotransform[3] + self.geotransform[5]*self.ysize

if __name__ == "__main__":
    base_url = 'https://cloud.sdsc.edu/v1/AUTH_opentopography/Raster/NCAL/NCAL_be/'
    
    print("Downloading rasters...")
    dataset_names = list_folders_from_url(base_url)
    for fn in dataset_names[0:50]:
        download_directory(os.path.join(base_url, fn))

    print("Merging rasters ...")
    # TODO: add working dir as parameter
    # TODO: add file parameter, don't hard-code ArcInfo grid file
    #files_to_merge = ['data/' + dataset_names[offset+i] + 'w001001.adf' for i in range(num_tiles)]
    base_filename = dataset_names[0]
    files_to_merge = find_matching_files(base_filename, nx=20, ny=20)
    print("Base raster: " + base_filename)
    print("Merging " + str(len(files_to_merge)) + " files")
    dest_dir = '/media/rmsare/data/ot_data/'
    files_to_merge = [dest_dir + fn + '/w001001.adf' for fn in files_to_merge]
    merge_grids_from_names(files_to_merge)
    # TODO: get gdal_merge argv working and remove this hack
