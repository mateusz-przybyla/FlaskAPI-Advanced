from flask import Flask
from dotenv import load_dotenv

from api.config import Config
from api.extensions import api, jwt, db, migrate, email_queue
from api.resources.test import blp as TestBlueprint
from api.resources.user import blp as UserBlueprint
from api import jwt_callbacks

def create_app(test_config=None):
    app = Flask(__name__)
    load_dotenv()

    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)
    api.init_app(app)
    jwt.init_app(app)

    api.register_blueprint(TestBlueprint)
    api.register_blueprint(UserBlueprint)

    app.email_queue = email_queue

    return app