from __future__ import absolute_import, unicode_literals
from celery import Celery
import dem, scarplet
import WindowedTemplate as wt
import time
import numpy as np

app = Celery('scarplet-testing', broker='sqs://')
app.config_from_object('celeryconfig')

data = dem.DEMGrid('synthetic_kt10_1000.tif')

@app.task(ignore_result=False)
def long_function(t):
    A = np.random.randn(100, 100)
    time.sleep(t)
    return A

@app.task
def tsum(M):
    return sum(M[:])

@app.task
def load_data(filename):
    return dem.DEMGrid(filename)

@app.task()
def match_template(d, age, alpha):
    amp, snr = scarplet.calculate_amplitude(data, wt.Scarp, d, age, alpha)
    return TemplateFit(d, age, alpha, amp, snr)

@app.task()
def compare_fits(grids):
    s = grids[0].amp.shape
    best_snr = np.zeros(s)
    best_amp = np.zeros(s)
    best_alpha = np.zeros(s)
    best_age = np.zeros(s)

    for grid in grids:
        best_amp = (best_snr > grid.snr)*best_amp + (best_snr < grid.snr)*grid.amp
        best_alpha = (best_snr > grid.snr)*best_alpha + (best_snr < grid.snr)*grid.alpha
        best_age = (best_snr > grid.snr)*best_age + (best_snr < grid.snr)*grid.age
        best_snr = (best_snr > grid.snr)*best_snr + (best_snr < grid.snr)*grid.snr

    return best_amp, best_age, best_alpha, best_snr

class TemplateFit(object):
    def __init__(self, d, age, alpha, amp, snr):
        self.d = d
        self.age = age 
        self.alpha = alpha
        self.amp = amp
        self.snr = snr