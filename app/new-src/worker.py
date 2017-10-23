import time
import callback
from config import (
    subscriber,
    SUBSCRIPTION,
)

while True:
    subscription = subscriber.subscribe(SUBSCRIPTION, callback=callback.update_info)
    time.sleep(1)
