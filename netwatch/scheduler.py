"""Module for running scheduled NetWatch jobs.

This module processes NetWatch alerts according to their
frequency.

Todo:
    * Find a way to process alerts in parallel and shut down those processes immediately
"""

import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from croniter import croniter

from netwatch.common import process_alert
from netwatch.store import store


class Scheduler:
    """A job scheduler for running NetWatch jobs.

    Attributes:
        stop_scheduler (threading.Event): Event for stopping the
            scheduler from another thread.
        thread (threading.Thread): Thread for running scheduler handler.
        executor (concurrent.futures.ThreadPoolExecutor): Executor
            for running scheduled NetWatch Alerts in parallel.
    """

    def __init__(self):
        self.stop_scheduler = threading.Event()
        self.thread = threading.Thread(target=self._scheduler_handler, args=())
        self.executor = ThreadPoolExecutor(3)

    def start(self):
        """Starts the scheduler"""

        self.stop_scheduler.clear()
        self.thread.start()

    def stop(self):
        """Stops the scheduler"""

        self.stop_scheduler.set()
        self.thread.join()
        self.executor.shutdown()

    def _scheduler_handler(self):
        while not self.stop_scheduler.is_set():
            jobs = []

            for alert in store.get_alerts():
                time = datetime.now()
                time = datetime(
                    time.year, time.month, time.day, time.hour, time.minute
                )  # no seconds value
                itr = croniter(alert.frequency, time)

                if time == itr.get_current(datetime):
                    jobs.append(alert.id)

            if len(jobs) > 0:
                self.executor.submit(process_alert, (jobs))

            self.stop_scheduler.wait(60)
