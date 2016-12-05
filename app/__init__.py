#------------------------------------------------------------------------------
# Franklin Chou
# Initialize python application
# Last modified 02 DEC 2016
#------------------------------------------------------------------------------

import os

from flask import Flask, render_template

from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from config import config

#------------------------------------------------------------------------------
# Automated task queue
#------------------------------------------------------------------------------
from celery import Celery
from celery.schedules import crontab
#------------------------------------------------------------------------------

bootstrap = Bootstrap()
db = SQLAlchemy()

# Create Celery object
# celery = Celery(__name__)

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'

def create_app(config_name):
    app = Flask(__name__)

    # Do I always have to strip quotes from config vars taken from env?
    config_name = config_name.strip('\'')

    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)

    # celery.config_from_object('celery_config')

    bootstrap.init_app(app)
    login_manager.init_app(app)


#------------------------------------------------------------------------------
# SSLify
#------------------------------------------------------------------------------
    if not app.config['SSL_DISABLE']:
        from flask_sslify import SSLify
        sslify = SSLify(app)

#------------------------------------------------------------------------------
# attach routes
#------------------------------------------------------------------------------
    from .public import public as public_blueprint
    app.register_blueprint(
        public_blueprint
    )

    from .main import main as main_blueprint
    app.register_blueprint(
        main_blueprint
    )

    from .auth import auth as auth_blueprint
    app.register_blueprint(
        auth_blueprint,
        url_prefix = '/auth'
    )

#------------------------------------------------------------------------------
# Prepare production environment
#------------------------------------------------------------------------------
    destroy_celery_schedule_file()
    create_var_file()
#------------------------------------------------------------------------------

    return app

def create_var_file():
    """
        03 DEC 2016
        Having trouble with creating the ghostdriverlog via heroku bash.
        The changes seem not to persist, SOLVED by creating the logfile server-
        side upon application launch in production.
    """
    basepath = os.path.dirname(os.path.dirname(__file__))

    ghostdriver_log_path = os.path.join(basepath, 'var', 'ghostdriver')

    if not os.path.exists(ghostdriver_log_path):
        os.makedirs(ghostdriver_log_path)

    ghostdriver_log_filename = 'ghostdriver.log'
    open(os.path.join(ghostdriver_log_path, ghostdriver_log_filename), 'w')

def destroy_celery_schedule_file():
    """

    """

    basepath = os.path.dirname(os.path.dirname(__file__))

    celery_schedule_path = os.path.join(basepath, 'var', 'celery', 'celerybeat-schedule')

    if os.path.isfile(celery_schedule_path):
        os.remove(celery_schedule_path)
