import os
import redis
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()
api = Api()
jwt = JWTManager()
redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))