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

data = dem.DEMGrid('carrizo.tif')
#data = dem.DEMGrid('synthetic_kt10_1000.tif')
#data = wt.generate_synthetic_scarp(1, 0, 10, 200, 200)

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

def calculate_best_fit_parameters(d=100):

    max_age = 3 
    age_step = 0.5
    num_ages = max_age/age_step
    ang_step = 2
    num_angles = 180/ang_step + 1
    ages = 10**np.linspace(0, max_age, num=num_ages)
    angles = np.linspace(-np.pi/2, np.pi/2, num=num_angles)
    
    start = timer()
    job = group([match_template.s(d, age, alpha) for age in ages for alpha in angles])
    res = job.apply_async()

    results = scarplet.compare_fits(data, res.join())

    res.forget()
    t_tot = timer() - start

    print("Template matching complete")
    print("-"*30)
    #print("Time for async fits:\t " + "{:.1f}".format(t_fits) + " s")
    #print("Time for comparison:\t " + "{:.1f}".format(t_comp) + " s")
    print("Total time:\t\t " + "{:.1f}".format(t_tot) + " s")

    return results

