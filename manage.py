#! /usr/bin/python3.5

import os

from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand

from app import create_app, db
from app.models import User

# app = create_app('default')

app = create_app(os.environ.get('CONFIG'))

manager = Manager(app)
migrate = Migrate(app, db)

def make_shell_context():
    return dict(
        app = app,
        db = db,
        User = User
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
@manager.command
def runall():
    '''
        Runs Lexo worker(s) on the entire saved user base
    '''

    # from flask import current_app
    from app.main.runner import Runner
    from datetime import datetime

    # WARNING: This is HIGHLY unoptimized; if something breaks, check here first
    for u in db.session.query(User):
        with Runner(u.la_username, u.la_password_encrypted) as r:
            r.login()
            r.query()
            if (r.passed == True):
                u.last_run = datetime.utcnow()

@manager.command
def test():
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner().run(tests)

if __name__ == "__main__":
    manager.run()
