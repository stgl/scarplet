import dem, scarplet

import tasks
form utils import pairs

from s3utils import save_data_to_s3
from manage_workers import broadcast_data, start_multiple_workers, stop_all_workers

import boto
from celery import *

connection = boto.connect_ec2()

dage = 0.5
x = np.linspace(0, 3.5, 3.5/dage)
age_breaks = pairs(x)
n = len([x for x in age_breaks])

start_multiple_workers(connection, n)
# TODO: download data as part of set up?
#broadcast_data(connection)

g = group([tasks.match_chunk.s(a, b) for a, b in age_breaks])
r = g.apply_async()

while r.waiting():
    continue

r.forget()

best_results = compare_fits_from_s3()

save_data_to_s3(best_results, results_filename, bucket_name='scarp-results')
stop_all_workers(connection)
