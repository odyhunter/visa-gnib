from google.cloud import pubsub
import os
import configparser

config = configparser.ConfigParser()
config.read(os.environ['CONFIG_PATH'])

GCLOUD_PROJECT = config['app'].get('GCLOUD_PROJECT')
TOPIC_NAME = 'update_date'
SUBSCRIPTION_NAME = 'updates'

TOPIC = f'projects/{GCLOUD_PROJECT}/topics/{TOPIC_NAME}'
SUBSCRIPTION = f'projects/{GCLOUD_PROJECT}/subscriptions/{SUBSCRIPTION_NAME}'

print('Configuration loaded ...')

publisher = pubsub.PublisherClient()
subscriber = pubsub.SubscriberClient()



