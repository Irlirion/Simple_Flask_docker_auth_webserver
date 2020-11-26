from typing import Tuple

from flask import current_app as app
from flask_restful import Resource, reqparse, fields, marshal
from flask import jsonify

from server.resources import api, user_store, errors, cache
from server.resources.models import User
from server.utils.functions import generate_token


def login(email: str, password: str) -> dict:
    """  Login with identity and credentials """
    app.logger.debug(f"Login user with email: {email}, password: {password}")
    user: User = user_store.find_user(email=email)
    app.logger.debug(f"Find user: {user}")

    if user is None or not user.authorize(password):
        app.logger.debug("Error: InvalidCredentials")

        return errors.InvalidCredentials()
    app.logger.debug("User in")

    token = generate_token(user)

    response: dict = {'token': token}
    app.logger.debug(f"Response: {response}")
    return response


def check(token: str) -> Tuple[dict, int]:
    app.logger.debug(f"Checking token: {token}")
    user: User = cache.get(token)

    app.logger.debug(f"Find user: {user}")
    if user is None:
        app.logger.debug("Error UserDoesntExist")

        return errors.UserDoesntExist()
    response: dict = marshal(user, resource_fields)
    app.logger.debug(f"Response {response}")
    return response, 200


resource_fields = {
    'email': fields.String,
}


@api.resource('/auth', endpoint='auth')
class Authentication(Resource):
    """ Initialize endpoint argument parsers """

    def __init__(self):
        self.parser = {
            'get': reqparse.RequestParser(bundle_errors=True),
            'post': reqparse.RequestParser(bundle_errors=True),
        }
        self.init_parser()

    def init_parser(self):
        # POST parser arguments
        self.parser['get'].add_argument('token', trim=True, required=True, help='Token is required')
        # PUT parser arguments
        self.parser['post'].add_argument('email', required=True, help='Email is required')
        self.parser['post'].add_argument('password', required=True, help='Password is required')

    def get(self):
        args = self.parser['get'].parse_args()
        return check(args['token'])

    def post(self):
        args = self.parser['post'].parse_args()
        return login(**args)
