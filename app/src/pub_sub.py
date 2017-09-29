# Imports the Google Cloud client library
from google.cloud import pubsub
from config import GCLOUD_PROJECT
# Instantiates a client
from logging import getLogger

logger = getLogger()

TOPIC = 'MyTopic'
SUBSCRIPTION = 'new_events'

topic = f'projects/{GCLOUD_PROJECT}/topics/{TOPIC}'
subscription = f'projects/{GCLOUD_PROJECT}/subscriptions/{SUBSCRIPTION}'


def update_info_callback(message):
    logger.info(message)
    message.ack


publish_client = pubsub.PublisherClient()
subscriber = pubsub.SubscriberClient()

publish_client.publish(topic, b'This is my message.', foo='bar')
subscriber.create_subscription(subscription, topic)
subscription = subscriber.subscribe(subscription)

subscription.open(update_info_callback)
