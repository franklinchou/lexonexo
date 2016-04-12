import argparse
import sys

import os

from multiprocessing import Process

def main(argv=sys.argv[1:]):

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--scheduler',
        dest = 'scheduler',
        action = 'store_true',
        default = True
    )

    args = parser.parse_args(argv)

    children = []
    for n in range(len(sys.argv)):
        children.append(
            Process(
                target = worker,
            )
        )

    if args.scheduler:
        children.append(
            Process(
                target = scheduler,
            )
        )

    for process in children:
        process.start()

    for process in children:
        process.join()

def scheduler(debug=False):
    from app import create_app, queue_instance

    app = create_app(os.environ.get('CONFIG'))
    print('[LEXONEXO] RQ scheduler started')
    with app.app_context():
        scheduler = queue_instance.get_scheduler()
        scheduler.run()

def worker(listen=(), debug=True):
    from app import create_app, queue_instance

    app = create_app(os.environ.get('CONFIG'))
    with app.app_context():
        worker = queue_instance.get_worker(listen=listen)
        worker.work()

if __name__ == '__main__':
    main()
