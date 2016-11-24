#! /bin/bash

celery -A app.jobs.tasks beat --loglevel=info -s ./var/celery/celerybeat-schedule -l debug
