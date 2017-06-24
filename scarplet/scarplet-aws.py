import dem, scarplet

import tasks
from utils import save_data_to_s3

import boto
from celery import *

g = group([tasks.match_chunk.s(a, b) for a, b in age_breaks])
r = g.apply_async()

while r.waiting():
    continue

r.forget()

best_results = compare_fits_from_s3()

save_data_to_s3(best_results, bucket_name='scarp-results')

