
from app.config import redis
from app.utils import lock

from ..models import User

from datetime import datetime

from ..main.runner import Runner

'''
    Execute lexis nexis query
'''
@queue.job
def execute_lnq(user_id):

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
        print('reached')
        with Runner (user.la_username, user.la_password_encrypted) as r:
            r.login()
            r.query()
            if (r.passed == True):
                user.last_run = datetime.now()
