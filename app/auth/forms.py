from flask_wtf import Form

from wtforms import StringField,\
    PasswordField,\
    BooleanField,\
    SubmitField

from wtforms import ValidationError
from wtforms.validators import Required,\
    Length,\
    Regexp,\
    EqualTo

from ..models import User

#------------------------------------------------------------------------------
# 03 DEC 2016
# Imported to give launchtime flexibility over email domains accepted.
#------------------------------------------------------------------------------
import os
from app import config
#------------------------------------------------------------------------------

class LoginForm(Form):
    email = StringField(
        'Email',
        validators = [
            Required(),
            Length(5, 64)
        ]
    )

    password = PasswordField(
        'Password',
        validators = [
            Required()
        ]
    )

    submit = SubmitField('Login')

class RegistrationForm(Form):
    # Is there any better way to do this? It's very messy/not elegant.
    shu_only = config[os.environ.get('CONFIG').strip('\'')].SHU_ONLY

    if (shu_only == True):
        email = StringField(
            'Email',
            validators = [
                Required(),
                Length(5, 64),
                Regexp(
                    "^([a-zA-Z])*[\.]([a-zA-Z])*@{1}(student\.shu\.edu|shu.edu)$",
                    message = 'Please use your Seton Hall email'
                )
            ]
        )
    else:
        email = StringField(
            'Email',
            validators = [
                Required(),
                Length(5, 64)
            ]
        )

    lexis_username = StringField(
        "Lexis Username",
        validators = [
            Required()
        ]
    )

    lexis_password = PasswordField(
        "Lexis Password",
        validators = [
            Required()
        ]
    )

    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')
