"""
Utilities for S3 data transfer
"""

import boto
import datetime
import numpy as np

def load_data_from_s3(filename, bucket_name='scarp-tmp'):
    connection = boto.connect_s3()
    bucket = connection.get_bucket(bucket_name, validate=False)
    key = bucket.new_key(filename)
    key.get_contents_to_filename(filename)
    return np.load(filename)

def download_data_from_s3(filename, bucket_name='scarp-tmp'):
    connection = boto.connect_s3()
    bucket = connection.get_bucket(bucket_name, validate=False)
    key = bucket.new_key(filename)
    key.get_contents_to_filename(filename)

def save_data_to_s3(data, filename=None, bucket_name='scarp-tmp'):
    connection = boto.connect_s3()
    bucket = connection.get_bucket(bucket_name, validate=False)
    if not filename:
        d = datetime.datetime.now()
        filename = 'tmp_' + d.isoformat() + '.npy'
    key = bucket.new_key(filename)
    np.save(filename, data)
    key.set_contents_from_filename(filename)

