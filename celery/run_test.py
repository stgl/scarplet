import dem
import scarplet
from WindowedTemplate import generate_synthetic_scarp

import tasks
from celery import *

import numpy as no
import matplotlib.pyplot as plt


#hd = [tasks.add.s(i, i) for i in range(10)]
#cb = tasks.tsum.s()
#res = chord(hd)(cb)
#
#print('generic chord works...')
#print(res.get())
#
#print('moving on to template matching test...')
data = generate_synthetic_scarp(1, 0, 10, 200, 200)

d = 100
max_age = 3 
age_step = 0.5
num_ages = max_age/age_step
ang_step = 2
num_angles = 180/ang_step + 1
ages = 10**np.linspace(0, max_age, num=num_ages)
angles = np.linspace(-np.pi/2, np.pi/2, num=num_angles)

res = tasks.calculate_best_fit_parameters()

for param in res:
    plt.figure()
    plt.imshow(param._griddata)
    plt.title(param.name)
    plt.show(block=False)

#scarplet.save_results(data, res, base_dir='results/')

#res.forget()
