from flask import Flask, render_template

from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from config import config

#------------------------------------------------------------------------------
# Automated task queue
#------------------------------------------------------------------------------
from celery import Celery
#------------------------------------------------------------------------------

bootstrap = Bootstrap()
db = SQLAlchemy()

# celery = Celery()


login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'

#------------------------------------------------------------------------------
# Automated task queue
#------------------------------------------------------------------------------
def create_celery(app):
    celery = Celery(
                app.import_name,
                backend=app.config['CELERY_RESULT_BACKEND'],
                broker=app.config['CELERY_BROKER_URL']
            )
    celery.conf.update(app.config)

    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery
#------------------------------------------------------------------------------

def create_app(config_name):
    app = Flask(__name__)

    # Do I always have to strip quotes from conifg vars taken from env?
    config_name = config_name.strip('\'')

    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)
    # celery.conf.update(app.config)
    # celery = create_celery(app)

    bootstrap.init_app(app)
    login_manager.init_app(app)


#------------------------------------------------------------------------------
    # SSLify
#------------------------------------------------------------------------------
    if not app.config['SSL_DISABLE']:
        from flask_sslify import SSLify
        sslify = SSLify(app)
#------------------------------------------------------------------------------

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

    return app
#------------------------------------------------------------------------------

