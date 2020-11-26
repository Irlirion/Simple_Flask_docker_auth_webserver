from uuid import uuid4

from flask import current_app as app

from server.resources import cache


def generate_token(user):
    token: str = uuid4().hex
    app.logger.debug(f"Generate token: {token}")
    app.logger.debug(f"Setting cache key: {token} value: {user}")
    ret = cache.set(token, user, timeout=10000)
    app.logger.debug(f"Cache is set: {ret}")
    return token
