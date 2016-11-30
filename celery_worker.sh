#! /bin/bash

# 20 NOV 2016

# In production for a single dyno setup, worker and beat will be run in the
# same process.

celery -A app.jobs.tasks worker --loglevel=info
