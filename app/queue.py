from redis import StrictRedis

# from rq_scheduler import Scheduler

from datetime import datetime, timedelta

from rq import Worker
from rq import Queue as RQ

# default job timeout; one day in seconds
ONE_DAY = 86400

from functools import wraps

class Queue(object):
    def init_app(self, app, db):
        self.config = {
            'queues' : app.config['QUEUES'],
            'routes' : app.config['QUEUE_ROUTES'],
            'default_queue' : app.config['QUEUE_DEFAULT'],
            'schedule' : app.config['QUEUE_SCHEDULE'],
        }

        self.app = app
        self.db = db

        self.connection = StrictRedis.from_url(
            app.config['REDIS_URL']
        )

    def get_queue_name(self, job):
        return self.config['routes'].get(job, self.config['default_queue'])

    def add_to_queue(self, job, args=(), kwargs={}, **opts):
        queue =\
            RQ(
                self.get_queue_name(job),
                connection = self.connection
            )

        return queue.enqueue_call(
            job,
            args = args,
            kwargs = kwargs,
            result_ttl = 0,
            timeout = ONE_DAY,
            **opts
        )

    def apply(self, job, args=(), kwargs={}, **opts):
        queue =\
            RQ(
                self.get_queue_name(job),
                connection = self.connection,
                async = False
            )

        return queue.enqueue_call(
            job,
            args = args,
            kwargs = kwargs,
            result_ttl = 0,
            timeout = ONE_DAY,
            **opts
        )

    def job(self, *args, **kwargs):
        def wrapped(function):
            @wraps(function)
            def inner(*args, **kwargs):
                try:
                    rv = function(*args, **kwargs)
                except:
                    self.db.session.rollback()
                    raise
                else:
                    self.db.session.commit()
                    return rv
            return inner
        return wrapped

    # def get_scheduler(self, interval = None):
    def get_scheduler(self):
        scheduler =\
            Scheduler(
                connection = self.connection,
                queue = self,
                # interval = interval
            )

        for job, job_config in self.config['schedule'].items():
            scheduler.add(job, **job_config)
        return scheduler

    def get_worker(self, listen = ()):

        if not listen:
            listen = self.config['queues']

        # sentry?
        #   probably used for error handling

        return Worker(
            [
                RQ(k, connection = self.connection)
                for k in listen
            ],
            # exception_handlers = exception_handlers,
            connection = self.connection,
        )

class Scheduler(object):
    schedule_key = 'rq:schedule'

    def __init__(self, connection, queue):
        self.connection = connection
        self.queue = queue
        self.schedule = {}

    def get_next_run(job_last_run):
        from random import randint
        now = datetime.now()

        # If the job has never been run OR if the job is STALE,
        #   schedule the job to be run within 15 minutes of the current time
        if job_last_run is None or job_last_run.date() + timedelta(days=2) < now.date():
            next_run = now + timedelta(minutes = randint(1, 15))

        if job_last_run:
            next_run = job_last_run + timedelta(days = 1)

            seconds = randint(1, 85500)

            # Convert seconds to hours, minues, seconds
            m, s = divmod(seconds, 60)
            h, m = divmod(m, 60)

            next_run = next_run.replace(hour = h, minute = m, second = s)

        return next_run

    def add(self, job, job_last_run):
        next_run = get_next_run(job_last_run)
        print('Scheduled for ' + next_run)
        self.connection.zadd(self.schedule_key, next_run, job)

    def run(self):
        # Find jobs scheduled in the future
        while True:
            pending =\
                set(
                    self.connection.zrangebyscore(
                        self.schedule_key,
                        float(datetime.now().strftime('%s.%f')),
                        '+inf'
                    )
                )

            for job, job_config in self.schedule.items():
                if job in pending:
                    continue
                timestamp = datetime.now() + timedelta(seconds = job_config['seconds'])
                self.connection.zadd(self.schedule_key, timestamp, job)
                self.queue.add_to_queue(job)

        # sleep(self.interval)
