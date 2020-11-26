from flask_restful import Resource, reqparse

from server.resources import api, user_store, db, errors, cache
from server.resources.errors import UserDoesntExist
from server.resources.models import Text, User
from server.utils.functions import generate_token


@api.resource('/db', endpoint='db')
class DB(Resource):
    def __init__(self):
        """ Initialize endpoint argument parsers """

        self.parser = {
            'post': reqparse.RequestParser(bundle_errors=True),
        }
        self.init_parser()

    def init_parser(self):
        # POST parser arguments
        self.parser['post'].add_argument('text', trim=True, required=True, help='Text is required')
        self.parser['post'].add_argument('token', trim=True, required=True, help='Token is required')

    def post(self):
        args = self.parser['post'].parse_args()
        user: User = cache.get(args['token'])
        if user is None:
            return UserDoesntExist()
        Text(user_id=user.id, text=args['text'])
        db.session.commit()

        return {"status": "successful"}
