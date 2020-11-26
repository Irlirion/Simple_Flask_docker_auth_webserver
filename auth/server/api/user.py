from flask_restful import Resource, reqparse

from server.resources import api, user_store, db, errors
from server.utils.functions import generate_token


@api.resource('/user', endpoint='user')
class User(Resource):
    def __init__(self):
        """ Initialize endpoint argument parsers """

        self.parser = {
            'post': reqparse.RequestParser(bundle_errors=True),
        }
        self.init_parser()

    def init_parser(self):
        # POST parser arguments
        self.parser['post'].add_argument('email', trim=True, required=True, help='Email is required')
        self.parser['post'].add_argument('password', required=True, help='Password is required')

    def post(self):
        """ Create a new user account """

        args = self.parser['post'].parse_args()
        print(args)
        if user_store.find_user(email=args['email']):
            return errors.UserAlreadyExist()

        user = user_store.create_user(email=args['email'], password=args['password'])
        db.session.commit()

        token = generate_token(user)
        return {'token': token}
