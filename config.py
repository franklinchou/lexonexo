# -*- coding: utf-8 -*-

import os

from celery.schedules import crontab

basedir = os.path.abspath(
    os.path.dirname(__file__)
)

class Config:
    SECRET_KEY          = os.environ.get('SECRET_KEY')
    # WTF_CSRF_ENABLED    = True

    PROJ_NAME           = 'Lexo\u00A0Nexo'

    SQLALCHEMY_COMMIT_ON_TEARDOWN   = True
    SQLALCHEMY_TRACK_MODIFICATIONS  = False

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG       = True
    SSL_DISABLE = True
    MY_UNAME    = os.environ.get('MY_UNAME')
    MY_PWD      = os.environ.get('MY_PWD')

    # Changed local database to mirror remote
    DATABASE_URL = os.environ.get('DATABASE_URL').strip('\'')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL

class ProductionConfig(Config):
    DEBUG       = False
    SSL_DISABLE = False

    CSRF_ENABLED = True

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    REDIS_URL = os.environ.get('REDIS_URL')

#------------------------------------------------------------------------------
# Configs
#------------------------------------------------------------------------------
config = {
    'default': DevelopmentConfig,

    'devel' : DevelopmentConfig,
    'production': ProductionConfig
}
