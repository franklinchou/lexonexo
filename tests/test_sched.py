import unittest

from flask import current_app

from app import create_app

from .app.models import User

class SchedulerTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('default')
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()


    def test_available(self):
        # try:

    def test_nextrun(self):
        u = User.query.filter_by(id=3).first()
        if u.last_run is None:
            print('Last run not set, nothing to do.')

