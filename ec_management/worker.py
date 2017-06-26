from multiprocessing import Process
import boto
from celery import *


class BaseWorker(Process):
    def __init__(self):
        self.queue = 'default-queue'


class MatchWorker(BaseWorker):
    def __init__(self):
        self.queue = 'scarp-search-queue'


class AggregationWorker(BaseWorker):
    def __init__(self):
        self.queue = 'scarp-aggregate-queue'
