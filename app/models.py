'''
JUL 2016

Unable to reliably implement two way encryption/encoding of Lexis passwords.

THIS SECURITY FEATURE HAS BEEN ABANDONED.
In the event that the hosting site's database is breached, Lexis
username/password pairs stored with this application will be EXPOSED.

Franklin Chou
'''

from flask_login import UserMixin
from flask import current_app

from werkzeug.security import generate_password_hash,\
    check_password_hash

from datetime import datetime

from app import db

from . import login_manager

#------------------------------------------------------------------------------
# USER STORAGE
#------------------------------------------------------------------------------
class User(UserMixin, db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key = True)

    ### Task id links user to queue

    email = db.Column(db.String(64), unique = True, index = True)
    password_hash = db.Column(db.String(128))

    la_username = db.Column(db.String(64), unique = True)
    la_password = db.Column(db.String(128))
    # la_password_encrypted = db.Column(db.String(512))

    confirmed = db.Column(db.Boolean, default = False)

    last_run = db.Column(db.DateTime())

    @property
    def password(self, password):
        raise AttributeError("`password` is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
