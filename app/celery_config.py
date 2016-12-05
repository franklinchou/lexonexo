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
        'schedule': crontab(minute='*/1')
    },
}

