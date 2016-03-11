import os

from flask.ext.sqlalchemy import SQLAlchemy

basedir = os.path.abspath(
    os.path.dirname(__file__)
)

class Config:
    SECRET_KEY          = os.environ.get('SECRET_KEY')
    WTF_CSRF_ENABLED    = True

    PROJ_NAME           = 'Lexo Nexo'

#------------------------------------------------------------------------------
# Lexis specific
#------------------------------------------------------------------------------

    LEXIS_BASE_URL      = 'https://advance.lexis.com'
    LEXIS_LOGIN_TARGET  = 'https://signin.lexisnexis.com/lnaccess/app/signin/aci/la'

    LEXIS_QUERY         = '88 NJ 529'
    LEXIS_QUERY_CHECK   = LEXIS_QUERY.replace(" ", "+")

    LEXIS_VAULT_KEY     = os.environ.get('LEXIS_VAULT_KEY')

#------------------------------------------------------------------------------

    SQLALCHEMY_COMMIT_ON_TEARDOWN   = True
    SQLALCHEMY_TRACK_MODIFICATIONS  = False

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG       = True
    MY_UNAME    = os.environ.get('MY_UNAME')
    MY_PWD      = os.environ.get('MY_PWD')

    SQLALCHEMY_DATABASE_URI = 'sqlite:////' +\
        os.path.join(
            basedir,
            'database',
            'database.sqlite'
        )

class ProductionConfig(Config):
    DEBUG       = False

    DATABASE_URI            = os.environi.get('DATABASE_URL')
    SQLALCHEMY_DATABASE_URI = DATABASE_URI

config = {
    'default': DevelopmentConfig,

    'production': ProductionConfig
}
