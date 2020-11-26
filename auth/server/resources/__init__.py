from flask_caching import Cache
from flask_login import LoginManager
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

from server.utils.datastore import SQLAlchemyUserDatastore

''' Application resources '''
db = SQLAlchemy()
api = Api()
login_manager = LoginManager()
cache = Cache()

''' User store '''
from server.resources import models
user_store = SQLAlchemyUserDatastore(db, models.User)

''' Api endpoints '''
from server.api.auth import Authentication
from server.api.user import User
from server.api.db import DB
