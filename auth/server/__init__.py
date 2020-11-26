import os

from flask import Flask, Blueprint
from flask_cors import CORS
from flask_migrate import Migrate
from healthcheck import HealthCheck, EnvironmentDump

from server.resources import api, db, login_manager, cache
from server.resources.utils import db_available

client = os.getenv('CLIENT_ORIGIN', '*')
migrate = Migrate()
router = Blueprint('api', 'api__module', url_prefix='/api')
cors = CORS(origin=client, headers=['access-control-allow-origin'])


def create_app(mode):
    """ Generate application instance based on configuration mode """

    app = Flask(__name__)
    app.config.from_object(mode)
    migrate.init_app(app, db)
    cache.init_app(app)
    cors.init_app(app)
    attach_monitor(app)
    login_manager.init_app(app)
    api.init_app(router)
    app.register_blueprint(router)
    with app.app_context():
        db.init_app(app)
        db.create_all()
    return app


def attach_monitor(app):
    """ Attach status and environment endpoints for monitoring site health """
    health = HealthCheck(app, '/status')
    envdump = EnvironmentDump(
        app,
        '/env',
        include_os=False, include_config=False,
        include_process=False, include_python=False
    )

    health.add_check(db_available)
