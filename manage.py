#! /usr/bin/python3.5

#------------------------------------------------------------------------------
# Franklin Chou
# Manage script
# Revision 3
#------------------------------------------------------------------------------

"""
    Database-------------------------------------------------------------------

    If executing locally, must first start postgres db, execute:

    `systemctl start postgresql.service`

    WARNING: System will prompt for admin password

    Queue----------------------------------------------------------------------

    Execute `redis.sh`
"""

import os

from flask_script import Manager,\
    Shell,\
    Command,\
    Option

from flask_migrate import Migrate, MigrateCommand

from app import create_app, db
from app.models import User
from datetime import datetime

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



@manager.command
def test():
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner().run(tests)

if __name__ == "__main__":
    manager.run()
