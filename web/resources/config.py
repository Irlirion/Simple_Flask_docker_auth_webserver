import os


class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.urandom(32)


class Development(Config):
    DEBUG = True


class Testing(Config):
    TESTING = True
