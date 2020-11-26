import os


class Config(object):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CACHE_TYPE = "simple"


class Development(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    CACHE_TYPE = "memcached"
    CACHE_MEMCACHED_SERVERS = ["cache:11211"]
    CACHE_KEY_PREFIX = "flask_auth"


class Testing(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
