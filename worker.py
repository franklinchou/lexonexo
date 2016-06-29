'''
    Revision no. 2
'''

from redis import StrictRedis
from rq import Worker

from app import create_app, q

import os

def worker():
    listen = ['default']

    app = create_app(os.environ.get('CONFIG'))

    with app.app_context():
        worker = q.get_worker(listen=listen)
        worker.work()

if __name__ == '__main__':
    worker()
