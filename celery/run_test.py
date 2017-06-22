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

res = tasks.calculate_best_fit_parameters()

for param in res:
    plt.figure()
    plt.imshow(param._griddata)
    plt.title(param.name)
    plt.show(block=False)

#scarplet.save_results(data, res, base_dir='results/')

#res.forget()
