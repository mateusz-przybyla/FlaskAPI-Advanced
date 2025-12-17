import pytest
import fakeredis

from api import create_app
from api.extensions import db

@pytest.fixture
def app():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "JWT_SECRET_KEY": "test-secret"
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
        db.engine.dispose()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def db_session(app):
    with app.app_context():
        yield db.session

@pytest.fixture(autouse=True)
def mock_redis(mocker):
    """
    Global fake Redis for JWT blocklist.
    Prevents real Redis connections during tests.
    """
    fake_redis = fakeredis.FakeRedis()
    mocker.patch("api.services.blocklist.redis_client", fake_redis)
    return fake_redis