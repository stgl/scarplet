import dem
import tasks
from celery import *

carrizo = dem.DEMGrid('tests/data/carrizo.tif')

d = 100
max_age = 10**3.5
age_step = 1
num_ages = max_age/age_step
num_angles = 180
ages = np.linspace(0, max_age, num=num_ages)
angles = np.linspace(-np.pi/2, np.pi/2, num=num_angles)

template_fits = [tasks.match_template.s(carrizo, d, age, alpha) for age in ages for alpha in angles]
compare_callback = tasks.compare_fits.s()

res = chord(template_fits)(compare_callback)


