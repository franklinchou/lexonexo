from flask.ext.wtf import Form

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

    password = PasswordField(
        'Password',
        validators = [
            Required(),
            EqualTo(
                'password_verify',
                message = 'Passwords must match'
            )
        ]
    )

    password_verify = PasswordField(
        'Confirm password',
        validators = [
            Required()
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
