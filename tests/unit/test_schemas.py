import pytest
from marshmallow import ValidationError

from api.schemas import UserSchema
from api.models import UserModel

@pytest.fixture
def schema():
    return UserSchema()

def test_user_schema_validation(schema):
    user_dict = {"username": "user", "email": "test@example.com", "password": "abc123"}

    # Test loading (deserialization)
    loaded = schema.load(user_dict)
    assert loaded["username"] == "user"
    assert loaded["email"] == "test@example.com"
    assert "password" in loaded

    # Test dumping (serialization)
    user_obj = UserModel(username="user", email="test@example.com", password="abc123")
    dumped = schema.dump(user_obj)
    assert dumped["username"] == "user"
    assert dumped["email"] == "test@example.com"
    assert "password" not in dumped

def test_missing_required_fields(schema):
    user_dict = {"username": "user"}

    with pytest.raises(ValidationError) as exc_info:
        schema.load(user_dict)

    errors = exc_info.value.messages
    assert "email" in errors
    assert "password" in errors

def test_username_too_short(schema):
    user_dict = {"username": "ab", "email": "test@example.com", "password": "abc123"}

    with pytest.raises(ValidationError) as exc_info:
        schema.load(user_dict)

    errors = exc_info.value.messages
    assert "username" in errors
    assert "Length must be between 3 and 80." in errors["username"][0]

def test_password_too_short(schema):
    user_dict = {"username": "user", "email": "test@example.com", "password": "ab"}

    with pytest.raises(ValidationError) as exc_info:
        schema.load(user_dict)

    errors = exc_info.value.messages
    assert "password" in errors
    assert "Shorter than minimum length 6." in errors["password"][0]

def test_invalid_email_format(schema):
    user_dict = {"username": "user", "email": "not-an-email", "password": "abc123"}

    with pytest.raises(ValidationError) as exc_info:
        schema.load(user_dict)

    errors = exc_info.value.messages
    assert "email" in errors