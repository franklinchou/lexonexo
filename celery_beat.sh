#! /bin/bash

celery -A app.jobs.lnq beat --loglevel=info -s ./var/celery/celerybeat-schedule
