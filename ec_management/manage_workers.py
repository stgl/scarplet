
import boto
from boto.manage.cmdshell import sshclient_from_instance

AWS_KEY = 'aws-scarp'
AWS_KEY_PATH = '/home/rmsare/aws_keys/aws-scarp.pem'
AWS_REGION = 'us-west-2'
AWS_SECURITY_GROUP = 'aws-scarp'

AWS_AMI_INSTANCE_ID = ''

INSTANCE_NUMBER = 1
PATH_TO_SETUP = '/home/rmsare/src/scarplet-python/setup.sh'

def broadcast_data(connection):
    res = connection.get_all_reservations()
    instances = res[0].get_instances()
    for i in instances:
        run_command(i, "python download_current_data.py")
        
def run_command(instance, command):
    client = sshclient_from_instance(instance, AWS_KEY_PATH, user_name='ubuntu')
    status, stdout, stderr = client.run(command)
    if status != 0:
        print("Download failed for instance " + str(i.id))
        print("Status: {:d}".format(status))
        print(stderr)
    else:
        print("Download complete for instance " + str(i.id))

def start_worker(connection):
    with f as open(PATH_TO_SETUP, 'r'):
        setup_script = f.read()

    res = connection.run_instances(
            AWS_AMI_INSTANCE_ID,
            key_name=AWS_KEY,
            instance_type=AWS_INSTANCE_TYPE,
            security_groups=[AWS_SECURITY_GROUP],
            user_data=setup_script
            )

    instance = res.instances[0]
    connection.create_tags([instance.id], {"Name" : "aws-scarp{:d}".format(INSTANCE_NUMBER)})

