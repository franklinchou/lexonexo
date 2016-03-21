from flask.ext.login import UserMixin
from flask import current_app

from werkzeug.security import generate_password_hash,\
    check_password_hash

#------------------------------------------------------------------------------
# 2 way encryption
#------------------------------------------------------------------------------

from Crypto import Random
from Crypto.Cipher import AES

from binascii import hexlify
from binascii import unhexlify

#------------------------------------------------------------------------------

from app import db

from . import login_manager

class User(UserMixin, db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(64), unique = True, index = True)
    password_hash = db.Column(db.String(128))

    la_username = db.Column(db.String(64), unique = True)
    la_password_encrypted = db.Column(db.String(512))
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
#------------------------------------------------------------------------------

    @property
    def la_password(self, la_password):
        raise AttributeError("`la_password` is not a readable attribute")

    @la_password.setter
    def la_password(self, la_password):
        key = current_app.config['LEXIS_VAULT_KEY']
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(key.strip("\'"), AES.MODE_CFB, iv)
        self.la_password_encrypted = hexlify(iv + cipher.encrypt(la_password))

    def use_la_password(self):
        key = current_app.config['LEXIS_VAULT_KEY']
        encrypted = unhexlify(self.la_password_encrypted)
        cipher = AES.new(key.strip("\'"), AES.MODE_CFB, encrypted[:AES.block_size])
        return cipher.decrypt(encrypted)[AES.block_size:]

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
