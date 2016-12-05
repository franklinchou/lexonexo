web: gunicorn manage:app --log-file=-

celery_beat: celery -A app.jobs.tasks beat --loglevel=info -l debug

# scalable
celery_worker: celery -A app.jobs.tasks worker --loglevel=info

# uncomment for consolidated worker/scheduler
# celery: celery -A app.jobs.tasks worker --beat --loglevel=info
