from __future__ import absolute_import, unicode_literals

import os, sys
import boto
from celery import *

import dem, scarplet
from scarplet import TemplateFit
import WindowedTemplate as wt
from WindowedTemplate import Scarp as Template

import time
import datetime
import numpy as np

from timeit import default_timer as timer

app = Celery('scarplet-testing', broker='sqs://')
app.config_from_object('celeryconfig')

#data = dem.DEMGrid('../tests/data/carrizo.tif')
#data = dem.DEMGrid('synthetic_kt10_1000.tif')
data = wt.generate_synthetic_scarp(1, 0, 10, 500, 500)

@app.task(ignore_result=False)
def long_function(t, n=100):
    A = np.random.randn(n, n)
    time.sleep(t)
    return A

@app.task(ignore_result=False)
def add(x, y):
    return x+y

@app.task(ignore_result=False)
def tsum(M):
    return sum(M[:])

@app.task
def load_data(filename):
    return dem.DEMGrid(filename)

def save_results_to_s3(results):
    connection = boto.connect_s3()
    bucket = connection.get_bucket('scarp-tmp', validate=False)
    d = datetime.datetime.now()
    fn = 'tmp_' + d.isoformat() + '.npy'
    key = bucket.new_key(fn)
    np.save(fn, results)
    key.set_contents_from_filename(fn)

@app.task(ignore_result=True)
def match_template(d, age, alpha):
    best_results = load_results_from_s3()
    amp, snr = scarplet.calculate_amplitude(data, wt.Scarp, d, age, alpha)
    this_results = [amp, age, alpha, snr]
    best_results = scarplet.compare_fits(best_results, this_results)
    save_results_to_s3(best_results)

@app.task(ignore_result=False)
def match_chunk(min_age, max_age):
    d = 100
    age_step = 0.5
    ang_step = 2
    nages = (max_age - min_age)/age_step 
    #nangles = (max_ang- min_ang)/ang_step 

    ages = 10**np.linspace(min_age, max_age, num=nages)
    orientations = np.linspace(-np.pi/2, np.pi/2, num=91)

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

            curv = data._calculate_directional_laplacian(this_alpha)
            
            this_amp, this_snr = scarplet.match_template(curv, template)
            mask = t.get_window_limits()
            this_amp[mask] = 0 
            this_snr[mask] = 0

            best_amp = (best_snr > this_snr)*best_amp + (best_snr < this_snr)*this_amp
            best_age = (best_snr > this_snr)*best_age + (best_snr < this_snr)*this_age
            best_alpha = (best_snr > this_snr)*best_alpha + (best_snr < this_snr)*this_alpha
            best_snr = (best_snr > this_snr)*best_snr + (best_snr < this_snr)*this_snr
            
    save_results_to_s3([best_amp, best_age, best_alpha, best_snr])

def get_grid_size():
    return data._griddata.shape

