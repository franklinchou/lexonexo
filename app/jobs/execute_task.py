# from app import queue

# from . import job


from app import queue_instance,\
    redis,\
    db

from ..models import User,\
    TaskStatus,\
    Task


from ..main.runner import Runner

from app.utils import lock

from datetime import datetime

'''
    Execute lexis nexis query
'''
@queue_instance.job()
def execute_lnq(user_id):
    print('reached')
    with lock(redis, user_id):
        user = User.query.get(user_id)
        task = Task.query.get(user.task_id)
        if not task:
            print('Execute query fired with missing target ID %s', (user_id,))
            return

        if task.status not in (TaskStatus.pending, TaskStatus.in_progress):
            print('Execute query fired with completed target ID %s', (user_id,))
            return

        task.date_started = datetime.now()
        task.status = TaskStatus.in_progress
        db.session.add(task)

        # Needed? Commit should be handled on context exit.
        db.session.commit()

#------------------------------------------------------------------------------
    # Run task
#------------------------------------------------------------------------------
        # Can I piggy back off the context created with the lock util?
        with Runner(user.la_username, user.la_password_encrypted) as r:
            r.login()
            r.query()
            if (r.passed == True):
                user.last_run = datetime.now()
