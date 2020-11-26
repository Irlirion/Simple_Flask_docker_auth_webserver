from flask import Flask


def create_app(mode):
    app = Flask(__name__)
    app.config.from_object(mode)
    return app
