import os
import configparser

class Config(object):
    basedir = './'

    SQLALCHEMY_DATABASE_URI = 'sqlite:///../cards.db'
    SQLALCHEMY_BINDS = {
        'game': 'sqlite://',
    }

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = 'aweiojfeiwjfiewjfwnneionioj'
