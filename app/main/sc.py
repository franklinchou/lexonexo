#------------------------------------------------------------------------------
# This is, hopefully, where the magic happens.
# Scheduled Lexis Nexis searches.
#------------------------------------------------------------------------------


from redis import Redis
from rq_scheduler import Scheduler

from datetime import datetime, timedelta

from random import randint

####
from . import main

from flask import current_app

from . runner import Runner
from ..models import User
####

# Open a connection to the Redis server
rs = Redis()

# Create a scheduler register'd w/Redis server
scheduler = Scheduler(
    connection = rs
)

def get_next_run(user_lastrun):

    now = datetime.now()

    # If user is new, lastrun is unset; set nextrun.
    # If the user's last run date is over two days old, the record is STALE;
    #   set the run time to be within 15 minutes of current time.
    if user_lastrun is None or user_lastrun.date() + timedelta(days=2) < now.date():
        next_run = now + timedelta(minutes=randint(1, 15))

    if user_lastrun:
        next_run = user_lastrun + timedelta(days=1)

        # Don't run any script 15 minutes prior to midnight.
        seconds = randint(1, 85500)

        # Convert seconds, to hours, minutes, seconds
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)

        next_run = next_run.replace(hour=h, minute=m, second=s)

    return next_run

def add_to_queue(email, user_lastrun):
    # rs.set(email, user_lastrun)

    # Exposure to this function should only be when the user first registers.
    # assert(user_lastrun is None)

    next_run = get_next_run(user_lastrun)

    if next_run:
        scheduler.enqueue_at(
            next_run,
            run,
            email
        )
    else:
        print('No next-run date can be set or determined for user, {}.'.format(email))

def run(email):
    with current_app.app_context():
        u = User.query.filter_by(email=email).first()

    with Runner(u.la_username, u.la_password_encrypted) as r:
        r.login()
        r.query()
        if (r.passed == True):
            u.last_run = datetime.utcnow()

            # Once executed, add the item back to the queue
            add_to_queue(u.email, u.last_run)
