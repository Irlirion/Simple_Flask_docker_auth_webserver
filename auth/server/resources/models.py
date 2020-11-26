from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

from server.resources import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(256), unique=True, nullable=False)
    password_hash = Column(String(100), nullable=False)

    def __init__(self, email, password, **kwargs):
        self.email = email
        self.password = password

    def __repr__(self):
        return "<User {}:{}>".format(self.id, self.email)

    @hybrid_property
    def password(self):
        return self.password_hash

    @password.setter
    def password(self, credentials):
        self.password_hash = generate_password_hash(credentials)

    @hybrid_method
    def authorize(self, credentials):
        return check_password_hash(self.password_hash, credentials)


class Text(db.Model):
    __tablename__ = 'texts'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id))
    text = Column(String(256), nullable=False)
