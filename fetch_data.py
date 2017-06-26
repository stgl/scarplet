"""
Tools for downloading and stitching DEM rasters from OpenTopography holdings
"""

import os, sys, shutil
import numpy as np

import requests
import urllib
from urllib2 import Request

from bs4 import BeautifulSoup

from osgeo import gdal, ogr, osr

from copy import copy

sys.path.append('/usr/bin')
import gdal_merge

def combine_all_overlapping_grids(data_dir):
    pass

def download_datasets(base_url = 'https://cloud.sdsc.edu/v1/AUTH_opentopography/Raster/NCAL/NCAL_be/', 
                    dest_dir='/media/rmsare/data/ot_data/', 
                    nfiles=None):
    dataset_names = list_folders_from_url(base_url)
    # Delete dupes from OT holdings
    dataset_names = [n for n in dataset_names if '_1' not in n]
           
    if nfiles is None:
        nfiles = len(dataset_names)
    #nfiles = 1000
    print("Processing {:d}/{:d} files".format(nfiles, len(dataset_names)))
    dataset_names = dataset_names[0:nfiles]
    
    #print("Downloading rasters...")
    #for fn in dataset_names:
    #    download_directory(os.path.join(base_url, fn))

    datasets = np.array([file_info(dest_dir + fn) for fn in dataset_names])

    return datasets
def download_directory(url, working_dir='/media/rmsare/data/ot_data/'):
    """
    Download all files in a remote directory. Does not descend into 
    subdirectories.
    """
    s = url.split('/')
    dir_name = working_dir + s[-1]

    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
    if not os.path.exists(dir_name + '/w001001.adf'): #TODO: Make this a chksum and loop until complete?
        file_names = list_files_from_url(url)
        for fn in file_names:
            if not os.path.exists(os.path.join(dir_name, fn)):
                urllib.urlretrieve(os.path.join(url, fn), os.path.join(dir_name, fn))

def download_directory_recursive(utl, working_dir='/media/rmsare/data/arra_data/'):
    pass

def find_matching_files(base_file, datasets, nx, ny, working_dir='/media/rmsare/data/ot_data/'):
    """
    Find matching filenames by EarthScope survey naming conventions.
    Survey data are named by the convention:

    ccXXX_YYYY.fmt

    where:  - "cc" is a data code ('u' for unfiltered, 'fg' for filtered ground 
              returns only, etc)
            - "XXX" and "YYYY" are the most siginificant digits of the dataset's
              lower left corner (XXX000, YYYY000) in UTM 10N coordinate system

    directories for gridded data use the convention "ccXXX_YYYY/"
    """
    s = base_file.filename.split('/')[-1].split('_')
    llx = int(s[0][2:5])*1000
    lly = int(s[1][0:4])*1000

    code = 'fg'
    names = [form_dataset_name(code, llx + dx*1000, lly + dy*1000) 
                     for dx in range(-nx,nx) for dy in range(-ny,ny)]
    
    # TODO: find a Pythonic way to do this
    matching_files = [f for f in datasets if f.filename in names]

    return matching_files

def expand_to_contiguous_grids(base_file, nrows, ncols):
    """
    Find all contiguous grids within nrows, cols of a central grid.

    Assumes grids are saved in a projection with bounding box information.
    """

    contiguous_grids = []
    for i in xrange(-nrows/2, nrows/2):
        for j in xrange(-ncols/2, ncols/2):
            this_llx = base_file.llx + 1000*j
            this_lly = base_file.lly + 1000*i
            this_file = [d for d in datasets if d.llx == this_llx and d.lly == this_lly] 
            if len(this_file) != 0:
                contiguous_grids.append(this_file[0])
     
    return contiguous_grids

def form_dataset_name(code, llx, lly, working_dir='/media/rmsare/data/ot_data/'):
    """
    Form valid dataset directory using OpenTopography bulk raster naming convention
    for EarthScope data.
    """

    return working_dir + code + str(llx / 1000) + '_' + str(lly / 1000)

def merge_grids(files, outfilename='merged.tif', nodata_value='-9999', working_dir='/media/rmsare/data/fixed_merged_data/'):
    # TODO: fix gdal_merge argv
    #sys.argv = ['-o', outfilename, '-init', nodata_value, '-a_nodata', nodata_value] + filenames
    #print("Merging:")
    #print([f.filename.split('/')[-1] for f in files])

    # TODO: add file parameter, don't hard-code ArcInfo grid file
    sys.argv = [f.filename + '/w001001.adf' for f in files]
    gdal_merge.main()
    
    for f in files:
        f.times_processed += 1

def list_files_from_url(url):
    """
    List all files and folders from a remote directory. Ignores hidden files.

    Assumes the URL returns an HTML directory listing.
    """
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
    """
    List all folders from a remote directory. Ignores all files and hidden 
    files and folders.

    Assumes the URL returns an HTML directory listing.
    """

    request = Request(url)
    page = requests.get(url).text 
    soup = BeautifulSoup(page, 'html.parser')
    links = soup.find_all('a')
    file_names = []

    for link in links:
        fn = link.get('href')
        if fn[-1] == '/' and fn[0] != '.':
            file_names.append(fn[0:-1])
    
    return file_names

def sort_by_utm_northing(files):
    """
    Sorts list of grid files by lower left UTM coordinates 
    in descending order.

    Geographically northeasternmost grids come first.
    """

    NE = np.array([(f.lly, -f.llx) for f in files], dtype=[('y', '>i4'), ('-x', '>i4')])
    idx = np.argsort(NE, order=('y', '-x'))[::-1]

    return files[idx]

class file_info:
    """ 
    A class holding information about a GDAL file.
    Designed after gdal_merge.py 
    """

    def __init__(self, filename):
        f = gdal.Open(filename)

        self.filename = filename
        self.times_processed = 0

        self.xsize = f.RasterXSize
        self.ysize = f.RasterYSize
        self.projection = f.GetProjection()
        self.geotransform = f.GetGeoTransform()

        self.ulx = self.geotransform[0]
        self.uly = self.geotransform[3]
        self.lrx = self.geotransform[0] + self.geotransform[1]*self.xsize
        self.lry = self.geotransform[3] + self.geotransform[5]*self.ysize
        self.llx = self.lrx
        self.lly = self.uly

def merge_datasets(datasets,
          nrows=10,
          ncols=8,
          dest_dir='/media/rmsare/data/ot_data/',
          working_dir='/media/rmsare/data/fixed_merged_data/'):

    #base_url = 'https://cloud.sdsc.edu/v1/AUTH_opentopography/Raster/SoCAL/SoCAL_be/'

    base_file = datasets[0]
    processed = np.array([x.times_processed >= 2 for x in datasets])

    while not processed.all():
        base_file = datasets[np.logical_not(processed)][0]
        files_to_merge = expand_to_contiguous_grids(base_file, nrows, ncols)
        files_to_merge = [f for f in files_to_merge if f.times_processed < 2]
        
        print("Merging rasters...")
        print("Base raster: " + base_file.filename)
                
        merged_filename = working_dir + base_file.filename.split('/')[-1] + '_merged.tif'
        if not os.path.exists(merged_filename) and len(files_to_merge) > 1:
            print("Merging " + str(len(files_to_merge)) + " files")
            merge_grids(files_to_merge)
            print("Saving merged file...")
            shutil.move('out.tif', merged_filename)
        else:
            for f in files_to_merge:
                f.times_processed += 1
            print("Merged file exists or no unprocessed files to merge. Moving on to next grid...")
        
        # XXX: bug here - what if base_filename alternates between two files?
        base_file.times_processed += 1
        processed = np.array([x.times_processed >= 2 for x in datasets])
        #delete_files(files_to_merge)

if __name__ == "__main__":
    datasets = download_datasets()
    datasets = sort_by_utm_northing(datasets)
    merge_datasets(datasets)
