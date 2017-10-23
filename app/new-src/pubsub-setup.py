publisher.create_topic(TOPIC)
subscriber.create_subscription(SUBSCRIPTION, TOPIC)
subscription = subscriber.subscribe(SUBSCRIPTION)

