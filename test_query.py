#------------------------------------------------------------------------------
# Query test
# Franklin Chou
# 01 NOV 2016
#------------------------------------------------------------------------------

# IMPORT
from app.jobs import task
from app.jobs.automation_exception import InvalidLanding

from app.models import User

from app import create_app

from datetime import datetime as DT
from datetime import timedelta

#------------------------------------------------------------------------------

def call_job():
    try:
        task.get_points('franklinchou', 'Fillmore234!!')
        # task.get_points('franklin.chou', '4107htkdh3xG')
    except InvalidLanding as e:
        raise

def run_query():
    try:
        time_threshold = DT.now() - timedelta(hours=2)
        u = User.query.filter(User.last_run < time_threshold)
        for record in u:
            task.get_points.delay(record.la_username, record.la_password)
    except:
        raise

def create_context():
    # Create application context
    create_app('devel').app_context().push()

if __name__ == "__main__":

    create_context()
    # call_job()

    run_query()

