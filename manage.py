#! /usr/bin/python3.5

import os

from flask_script import Manager,\
    Shell,\
    Command,\
    Option

from flask_migrate import Migrate, MigrateCommand

from app import create_app, db

# from app.queue import Queue

from app.jobs.lnq import Lnq
from datetime import datetime


from app.models import User

# app = create_app('default')

app = create_app(os.environ.get('CONFIG'))

manager = Manager(app)
migrate = Migrate(app, db)

def make_shell_context():
    return dict(
        app = app,
        db = db,
        User = User,
    )

manager.add_command(
    "shell",
    Shell(
        make_context = make_shell_context
    )
)

manager.add_command(
    "db",
    MigrateCommand
)


"""
    Note:
    If executing locally, must first start postgres db, execute:

    `systemctl start postgresql.service`

    WARNING: System will prompt for admin password
"""
class Force(Command):
    '''
        Force:
        Allows manual override of workers.

        WARNING: This function is for testing/development only; do NOT use
        in production.
    '''

    option_list = (
        Option('--user','-u', dest='user_id'),
        Option('--all', '-a', dest='force_all')
    )

    def run(self, user_id, force_all):
        if (force_all is None and user_id is None):
            print('ERROR: `force` function must be called using an argument')
        elif (force_all == 'true'):
            for u in db.session.query(User):
                lnq = Lnq()
                lnq.delay(u.la_username, u.la_password)
                if (lnq.passed == True):
                    u.last_run = datetime.utcnow()
        elif user_id:
            u = User.query.filter_by(id=user_id).first()
            lnq = Lnq()
            lnq.delay(u.la_username, u.la_password)
            if (lnq.passed == True):
                u.last_run = datetime.utcnow()
        else:
            print('Undefined option detected.')

manager.add_command(
    "force",
    Force
)


@manager.command
def test():
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner().run(tests)

if __name__ == "__main__":
    manager.run()
