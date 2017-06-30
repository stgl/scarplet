from __future__ import absolute_import, unicode_literals

import os, sys
sys.path.append('../scarplet')

import boto
from celery import *

import dem, scarplet
import WindowedTemplate as wt
from WindowedTemplate import Scarp as Template

import time
import datetime

import numpy as np
import numexpr

from timeit import default_timer as timer

app = Celery('scarplet-testing', broker='sqs://')
app.config_from_object('celeryconfig')

data = dem.DEMGrid('../tests/data/carrizo.tif')
#data = load_data_from 

@app.task(ignore_result=False)
@app.task
def add(x, y):
    return x + y

@app.task(ignore_result=True)
def match_template(d, age, alpha):
    best_results = load_results_from_s3()
    amp, snr = scarplet.calculate_amplitude(data, wt.Scarp, d, age, alpha)
    this_results = [amp, age, alpha, snr]
    best_results = scarplet.compare_fits(best_results, this_results)
    save_results_to_s3(best_results)

@app.task(ignore_result=False)
def match_chunk(min_age, max_age, min_ang=0, max_ang=180, age_step = 0.1):
    d = 100
    ang_step = 1
    nages = (max_age - min_age)/age_step + 1 
    nangles = (max_ang - min_ang)/ang_step 

    ages = 10**np.linspace(min_age, max_age, num=nages)[:-1]
    orientations = np.linspace(-np.pi/2, np.pi/2, num=nangles)

    s = data._griddata.shape 
    best_snr = np.zeros(s)
    best_amp = np.zeros(s)
    best_age = np.zeros(s)
    best_alpha = np.zeros(s)
    ny, nx = s
    de = data._georef_info.dx

    for this_alpha in orientations:
        for this_age in ages:
            
            t = Template(d, this_age, this_alpha, nx, ny, de)
            template = t.template()

            curv = data._calculate_directional_laplacian_numexpr(this_alpha)
            
            this_amp, this_snr = scarplet.match_template_numexpr(curv, template)
            mask = t.get_window_limits()
            this_amp[mask] = 0 
            this_snr[mask] = 0

            best_amp = numexpr.evaluate("(best_snr > this_snr)*best_amp + (best_snr < this_snr)*this_amp")
            best_age = numexpr.evaluate("(best_snr > this_snr)*best_age + (best_snr < this_snr)*this_age")
            best_alpha = numexpr.evaluate("(best_snr > this_snr)*best_alpha + (best_snr < this_snr)*this_alpha")
            best_snr = numexpr.evaluate("(best_snr > this_snr)*best_snr + (best_snr < this_snr)*this_snr")            

    save_results_to_s3([best_amp, best_age, best_alpha, best_snr])

def load_data_from_s3(filename, bucket_name='scarp-tmp'):
    connection = boto.connect_s3()
    bucket = connection.get_bucket(bucket_name, validate=False)
    key = bucket.new_key(filename)
    key.get_contents_to_filename(filename)
    return np.load(filename)

def save_data_to_s3(results, filename=None, bucket_name='scarp-tmp'):
    connection = boto.connect_s3()
    bucket = connection.get_bucket(bucket_name, validate=False)
    d = datetime.datetime.now()
    if not filename:
        filename = 'tmp_' + d.isoformat() + '.npy'
    key = bucket.new_key(filename)
    np.save(filename, results)
    key.set_contents_from_filename(filename)

def save_results_to_s3(results):
    connection = boto.connect_s3()
    bucket = connection.get_bucket('scarp-tmp', validate=False)
    d = datetime.datetime.now()
    filename = 'tmp_' + d.isoformat() + '.npy'
    key = bucket.new_key(filename)
    np.save(filename, results)
    key.set_contents_from_filename(filename)

def compare_fits_from_s3():
    connection = boto.connect_s3()
    bucket = connection.get_bucket('scarp-tmp', validate=False)
    best_results = initialize_results()
    for key in bucket.list():
        key.get_contents_to_filename('tmp.npy')
        this_results = np.load('tmp.npy')
        best_results = scarplet.compare_fits(best_results, this_results)
        key.delete()
    return best_results

def pairs(iterable):
    a, b = itertools.tee(iterable)
    next(b, None)
    return itertools.izip(a, b)

def pairwise(iterable):
    a = iter(iterable)
    return itertools.izip(a, a)

def get_grid_size():
    return data._griddata.shape
