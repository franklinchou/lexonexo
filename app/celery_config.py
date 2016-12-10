#------------------------------------------------------------------------------
# Schedule
# Franklin Chou
# 20 NOV 2016
#------------------------------------------------------------------------------

from celery.schedules import crontab

timezone = 'UTC'

beat_schedule = {
    'run-every-eight-hours': {
        'task': 'tasks.run_outstanding_query',
        'schedule': crontab(hour='*/8')
    },
}

task_soft_time_limit = 60

"""
    04 DEC 2016
    Set value to true to allow underlying task to throw exception
"""
task_eager_propogates = True
