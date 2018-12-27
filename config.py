import os


class DevelopmentConfig:

    # Flask
    DEBUG = True

    # SQLAlchemy
    POSTGRES = {
    'user': 'maruyamasoryou',
    'pw': 'password',
    'db': 'flasksake',
    'host': 'localhost',
    'port': '5432',
    }

    SQLALCHEMY_DATABASE_URI = 'postgresql://%(user)s:\
%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False


Config = DevelopmentConfig