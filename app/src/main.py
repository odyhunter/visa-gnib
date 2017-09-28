import threading
import time

from retrying import retry

import config
from utils import auto_submission_check
from utils import cleanup
from utils import fetch_appointments
from utils import notification_check

# https://docs.python.org/3.6/library/sched.html
class FetchAppointmentsThread(threading.Thread):
    @retry()
    def run(self):
        while True:
            fetch_appointments(config.VISA_DAYS_UPDATE_RANGE, 'visa')
            fetch_appointments(config.GNIB_DAYS_UPDATE_RANGE, 'gnib')
            time.sleep(config.FETCH_APPOINTMENTS_TIMEOUT)


class NotificationCheckThread(threading.Thread):
    @retry()
    def run(self):
        while True:
            notification_check()
            time.sleep(config.FETCH_APPOINTMENTS_TIMEOUT)


class AutoSubmissionCheckThread(threading.Thread):
    @retry()
    def run(self):
        while True:
            auto_submission_check()
            time.sleep(config.FETCH_APPOINTMENTS_TIMEOUT)


class CleanupThread(threading.Thread):
    @retry()
    def run(self):
        while True:
            cleanup()
            time.sleep(14400)  # 4 hours


# Create and Run Threads

fetchAppointments_t = FetchAppointmentsThread()
fetchAppointments_t.start()

notificationCheck_t = NotificationCheckThread()
notificationCheck_t.start()

cleanup_t = CleanupThread()
cleanup_t.start()

auto_submission_check_t = AutoSubmissionCheckThread()
auto_submission_check_t.start()
