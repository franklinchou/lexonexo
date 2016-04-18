import os

from app import create_app
from app import queue_instance

# from rq import Worker

def worker():
    listen = ['default']

    a = create_app(os.environ.get('CONFIG'))

    with a.app_context():
        worker = queue_instance.get_worker(listen = listen)
        worker.work()

if __name__ == '__main__':
    worker()
