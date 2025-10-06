import os
from flask import Flask
from dotenv import load_dotenv

from api.config import Config
from api.extensions import api, jwt, db, migrate
# from app.resources.test import blp as TestBlueprint
# from app.resources.user import blp as UserBlueprint
# from api import jwt_callbacks

def create_app():
    app = Flask(__name__)
    load_dotenv()

    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    api.init_app(app)
    jwt.init_app(app)

    # api.register_blueprint(TestBlueprint)
    # api.register_blueprint(UserBlueprint)

    return app