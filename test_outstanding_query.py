"""
    05 DEC 2016
    Attempt to fix celery scheduled query; suspect import error to be the problem
"""


from app.jobs import tasks

from app import create_app
from app.jobs import tasks

def create_context():
    create_app('devel').app_context().push()


if __name__ == "__main__":
    create_context()
    tasks.run_outstanding_query.delay()

