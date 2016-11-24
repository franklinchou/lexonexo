#------------------------------------------------------------------------------
# Schedule
# Franklin Chou
# 20 NOV 2016
#------------------------------------------------------------------------------

from celery.schedules import crontab

broker_url = 'redis://localhost:6379/0'
result_backend = 'redis://localhost:6379/0'

timezone = 'UTC'

beat_schedule = {
    'run-every-eight-hours': {
        'task': 'tasks.run_outstanding_query',
        'schedule': crontab(hour='*/8')
    },
}

