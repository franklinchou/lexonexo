#! /bin/bash

# 20 NOV 2016

celery -A app.jobs.tasks worker --loglevel=info
