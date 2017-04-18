from __future__ import absolute_import, unicode_literals
from kombu.entity import Exchange, Queue

CELERY_ACCESS_KEY_ID = 'AKIAI7EYBMIC2O5AU52Q'
CELERY_ACCESS_KEY = 'IQ9ow99uECoTMXB4kolnz8N0XWzTzl82zJ6RlVPe'

CELERY_SQS_ACCESS_KEY_ID = 'AKIAI5SE6SDNUDGU7OAA' 
CELERY_SQS_KEY = 'Q82q2J1Tu+cmntDN2TmvxRCUdFf+JduhlahLA0+9'

# Backend options (S3)
CELERY_RESULT_BACKEND = 'celery_s3.backends.S3Backend'

CELERY_S3_BACKEND_SETTINGS = {
        'aws_access_key_id' : CELERY_SQS_ACCESS_KEY_ID,
        'aws_secret_access_key' : CELERY_SQS_KEY,
        'bucket' : 'scarp-testing',
        }

# Broker URL (Amazon SQS)
BROKER_URL = 'sqs://' + CELERY_SQS_ACCESS_KEY_ID + ':' + CELERY_SQS_KEY + '@'

# Broker options
BROKER_TRANSPORT_OPTIONS = {'queue_name_prefix' : 'test-queue-',
                            'region' : 'us-west-2',
                            'visibility_timeout' : 3600,
                            'polling_interval' : 10}

# Serialization options
CELERY_TASK_SERIALIZER = 'pickle'
CELERY_ACCEPT_CONTENT = ['pickle']
CELERY_RESULT_SERIALIZER = 'pickle'

# Task options
CELERY_IGNORE_RESULT = True
#task_store_errors_even_if_ignored = True

# Queues
CELERY_DEFAULT_QUEUE = 'scarp-queue'
#task_routes = (
#        Queue('default', Exchange('default'), routing_key='default'),
#        Queue('queueA', Exchange('queueA'), routing_key='queueA'),
#        Queue('queueB', Exchange('queueB'), routing_key='queueB'),
#        )
#task_routes = {
#        'match_template':{'queue':'queueA', 'routing_key':'queueA'},
#        'compare_fits':{'queue':'queueB', 'routing_key':'queueB'},
#        }
#
