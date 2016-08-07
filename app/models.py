#------------------------------------------------------------------------------
# JUL 2016
#
# Unable to reliably implement two way encryption/encoding of Lexis passwords.
#
# THIS SECURITY FEATURE HAS BEEN ABANDONED.
# In the event that the hosting site's database is breached, Lexis
# username/password pairs stored with this application will be EXPOSED.
#------------------------------------------------------------------------------

from flask_login import UserMixin
from flask import current_app

from werkzeug.security import generate_password_hash,\
    check_password_hash

from datetime import datetime

#------------------------------------------------------------------------------
# Encryption
#
# JUL 2016
# WARNING! FEATURE ABANDONED
#------------------------------------------------------------------------------

# from Crypto import Random
# from Crypto.Cipher import AES

# from binascii import hexlify
# from binascii import unhexlify

#------------------------------------------------------------------------------

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

#------------------------------------------------------------------------------
    # Lexis password storage

    # JUL 2016
    # WARNING! FEATURE ABANDONED
#------------------------------------------------------------------------------

    # @property
    # def la_password(self, la_password):
    #    raise AttributeError("`la_password` is not a readable attribute")


    # @la_password.setter
    # def la_password(self, la_password):
    #    key = current_app.config['LEXIS_VAULT_KEY']
    #    iv = Random.new().read(AES.block_size)
    #    cipher = AES.new(key.strip("\'"), AES.MODE_CFB, iv)
    #    self.la_password_encrypted = hexlify(iv + cipher.encrypt(la_password))

    # def use_la_password(self):
    #    key = current_app.config['LEXIS_VAULT_KEY']

    #    print(self.la_password_encrypted)

    #    encrypted_unhexd = unhexlify(self.la_password_encrypted)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#------------------------------------------------------------------------------
# TASK STORAGE
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# Status labels
#------------------------------------------------------------------------------
class TaskStatus(object):
    pending = 0
    in_progress = 1
    finished = 2

    cancelled = 3
    failed = 4

    unknown = 5

    @classmethod
    def get_label(cls, status):
        return STATUS_LABELS[status]

    @classmethod
    def label_to_id(cls, label):
        return STATUS_LABELS_REV[label]

STATUS_LABELS = {
    TaskStatus.pending : 'pending',
    TaskStatus.in_progress : 'in_progress',
    TaskStatus.finished : 'complete',

    TaskStatus.cancelled : 'cancelled',
    TaskStatus.failed : 'failed',

    TaskStatus.unknown : 'unknown',
}

STATUS_LABELS_REV = {
    v : k for k, v in STATUS_LABELS.items()
}

#------------------------------------------------------------------------------
# Table for storing queued tasks (& status)
#------------------------------------------------------------------------------

class Task(db.Model):
    __tablename__ = 'tasks'

    # index by user_id
    __table_args__ = (
        db.Index('idx_task_user_id', 'user_id'),
    )

    id = db.Column(db.Integer, primary_key = True)

    # app_id

    user_id =\
        db.Column(
            db.Integer,
            db.ForeignKey('users.id', ondelete = "CASCADE"),
            nullable = False
        )

    status = db.Column(db.Integer, nullable = False)

    date_created =\
        db.Column(
            db.DateTime,
            default = datetime.utcnow,
            nullable = False
        )

    status = db.Column(db.Integer, nullable = False)

    forced = db.Column(db.Boolean)

    date_started = db.Column(db.DateTime)
    date_complete = db.Column(db.DateTime)

    @property
    def was_forced(self):
        return self.forced

    @property
    def status_label(self):
        return STATUS_LABELS.get(self.status, 'unknown')

    @property
    def duration(self):
        if not (self.date_complete and self.date_started):
            return
        return float('%.2f' % (self.date_complete - self.date_started).total_seconds())
