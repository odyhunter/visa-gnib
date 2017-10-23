import time
import callback
from config import (
    subscriber,
    SUBSCRIPTION,
)

subscription = subscriber.subscribe(SUBSCRIPTION)
subscription.open(callback.update_info)

while True:
    time.sleep(60)
