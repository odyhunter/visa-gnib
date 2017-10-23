# pubsub reference 
https://cloud.google.com/pubsub/docs/quickstart-cli

1. gcloud init
2. gcloud components install beta
3. gcloud beta pubsub topics create TOPIC_NAME
4. gcloud beta pubsub subscriptions create --topic TOPIC_NAME SUBSCRIPTION_NAME
5. gcloud beta pubsub topics publish TOPIC_NAME "hello"
6. gcloud beta pubsub subscriptions pull --auto-ack SUBSCRIPTION_NAME

PubSub config:

TOPIC_NAME = fetch_appointments

SUBSCRIPTION_NAME = sub_fetch_appointments  