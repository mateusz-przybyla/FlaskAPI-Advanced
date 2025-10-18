import pytest
from marshmallow import ValidationError

from api.schemas import UserSchema, UserRegisterSchema
from api.models import UserModel

# -------------------------
# Fixtures
# -------------------------
@pytest.fixture
def base_schema():
    return UserSchema()

@pytest.fixture
def register_schema():
    return UserRegisterSchema()

# -------------------------
# Tests for UserSchema (email + password only)
# -------------------------
def test_user_schema_valid_data(base_schema):
    user_dict = {"email": "test@example.com", "password": "abc123"}

    # deserialization (load)
    loaded = base_schema.load(user_dict)
    assert loaded['email'] == "test@example.com"
    assert loaded['password'] == "abc123"

    # serialization (dump)
    user_obj = UserModel(username="user", email="test@example.com", password="abc123")
    dumped = base_schema.dump(user_obj)
    assert dumped['email'] == "test@example.com"
    assert "password" not in dumped

def test_user_schema_missing_fields(base_schema):
    user_dict = {"email": "test@example.com"}  # missing password

    with pytest.raises(ValidationError) as exc_info:
        base_schema.load(user_dict)

    errors = exc_info.value.messages
    assert "password" in errors

def test_user_schema_password_too_short(base_schema):
    user_dict = {"email": "test@example.com", "password": "abc"}

    with pytest.raises(ValidationError) as exc_info:
        base_schema.load(user_dict)

    errors = exc_info.value.messages
    assert "password" in errors
    assert "Shorter than minimum length 6." in errors["password"][0]

def test_user_schema_invalid_email(base_schema):
    user_dict = {"username": "user", "email": "not-an-email", "password": "abc123"}

    with pytest.raises(ValidationError) as exc_info:
        base_schema.load(user_dict)

    errors = exc_info.value.messages
    assert "email" in errors

# -------------------------
# Tests for UserRegisterSchema (extends UserSchema + username)
# -------------------------
def test_register_schema_valid_data(register_schema):
    user_dict = {"username": "user", "email": "test@example.com", "password": "abc123"}

    loaded = register_schema.load(user_dict)
    assert loaded['username'] == "user"
    assert loaded['email'] == "test@example.com"

    user_obj = UserModel(username="user", email="test@example.com", password="abc123")
    dumped = register_schema.dump(user_obj)
    assert dumped['username'] == "user"
    assert dumped['email'] == "test@example.com"
    assert "password" not in dumped

def test_register_schema_missing_username(register_schema):
    user_dict = {"email": "test@example.com", "password": "abc123"}

    with pytest.raises(ValidationError) as exc_info:
        register_schema.load(user_dict)

    errors = exc_info.value.messages
    assert "username" in errors

def test_register_schema_username_too_short(register_schema):
    user_dict = {"username": "ab", "email": "test@example.com", "password": "abc123"}

    with pytest.raises(ValidationError) as exc_info:
        register_schema.load(user_dict)

    errors = exc_info.value.messages
    assert "username" in errors
    assert "Length must be between 3 and 80." in errors["username"][0]