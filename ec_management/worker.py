from multiprocessing import Process
import boto
from celery import *


class BaseWorker(Process):
    pass


class MatchWorker(BaseWorker):
    pass


class CompareWorker(BaseWorker):
    pass
