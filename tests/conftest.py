import pytest
import fakeredis

from api import create_app
from api.extensions import db
from api.services import blocklist
from types import SimpleNamespace

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
def mock_redis(monkeypatch):
    fake_redis = fakeredis.FakeRedis()
    monkeypatch.setattr(blocklist, "redis_client", fake_redis)

    yield fake_redis

@pytest.fixture(autouse=True) # autouse=True to apply to all tests
def mock_email_queue(monkeypatch, app):
    def fake_enqueue(*args, **kwargs):
        # simulate successful enqueue
        return None

    fake_queue = SimpleNamespace(enqueue=fake_enqueue) # create a simple object with enqueue method
    monkeypatch.setattr(app, "email_queue", fake_queue)

    yield fake_queue