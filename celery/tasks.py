from __future__ import absolute_import, unicode_literals

from celery import *

import dem, scarplet
from scarplet import TemplateFit
import WindowedTemplate as wt

import time
import numpy as np

from timeit import default_timer as timer

app = Celery('scarplet-testing', broker='sqs://')
app.config_from_object('celeryconfig')

#data = dem.DEMGrid('carrizo.tif')
#data = dem.DEMGrid('synthetic_kt10_1000.tif')
data = wt.generate_synthetic_scarp(1, 0, 10, 200, 200)

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

@app.task(ignore_result=False)
def match_template(d, age, alpha):
    amp, snr = scarplet.calculate_amplitude(data, wt.Scarp, d, age, alpha)
    return TemplateFit(d, age, alpha, amp, snr)

