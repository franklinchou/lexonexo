from redis import StrictRedis

from rq import Worker

from rq import Queue as QT

class Queue(object):
    def init_app(self, app, db):

        self.app = app
        self.db = None

        self.cxn =\
            StrictRedis.from_url(
                app.config['REDIS_URL']
            )

    def get_worker(self, listen = ()):
        if not listen:
            pass

        return Worker(
            [
                QT(k, connection = self.cxn)
                for k in listen
            ],
            connection = self.cxn,
        )
