#! /bin/bash

celery -A app.jobs.lnq worker --loglevel=info
