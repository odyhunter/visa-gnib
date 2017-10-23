import time
import callback
from config import (
    subscriber,
    SUBSCRIPTION,
)

subscription = subscriber.subscribe(SUBSCRIPTION, callback.update_info)


while True:
    time.sleep(60)
