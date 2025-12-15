import pytest
from flask_jwt_extended import create_access_token, decode_token
from datetime import timedelta

@pytest.fixture
def mock_email_queue(mocker):
    mock_queue = mocker.Mock()
    mocker.patch("api.resources.user.email_queue", mock_queue)
    return mock_queue

@pytest.fixture
def create_user_details(client, mock_email_queue):
    username = "user"
    email = "test@example.com"
    password = "abc123"
    client.post(
        "/register",
        json={"username": username, "email": email, "password": password},
    )

    return username, email, password

@pytest.fixture
def create_user_jwts(client, create_user_details):
    _, email, password = create_user_details
    response = client.post(
        "/login",
        json={"email": email, "password": password},
    )

    return response.json['access_token'], response.json['refresh_token']

def test_register_user(client, mock_email_queue):
    username = "user"
    email = "test@example.com"
    response = client.post(
        "/register",
        json={"username": username, "email": email, "password": "abc123"},
    )

    assert response.status_code == 201
    assert response.json == {"message": "User created successfully."}

    mock_email_queue.enqueue.assert_called_once()
    args, _ = mock_email_queue.enqueue.call_args
    assert args[0].__name__ == "send_user_registration_email"
    assert args[1] == "test@example.com"
    assert args[2] == "user"

def test_register_user_already_exists(client, mock_email_queue):
    username = "user"
    email = "test@example.com"
    client.post(
        "/register",
        json={"username": username, "email": email, "password": "abc123"},
    )

    response = client.post(
        "/register",
        json={"username": username, "email": email, "password": "abc123"},
    )

    assert response.status_code == 409
    assert (
        response.json['message'] == "A user with that email already exists."
    )

def test_register_user_missing_data(client, mock_email_queue):
    response = client.post(
        "/register",
        json={},
    )

    assert response.status_code == 422
    assert "password" in response.json['errors']['json']
    assert "username" in response.json['errors']['json']

def test_login_user(client, create_user_details):
    _, email, password = create_user_details
    response = client.post(
        "/login",
        json={"email": email, "password": password},
    )

    assert response.status_code == 200
    assert response.json['access_token']

def test_login_user_bad_password(client, create_user_details):
    _, email, _ = create_user_details
    response = client.post(
        "/login",
        json={"email": email, "password": "bad_password"},
    )

    assert response.status_code == 401
    assert response.json["message"] == "Invalid credentials."

def test_login_user_bad_email(client, create_user_details):
    _, _, password = create_user_details
    response = client.post(
        "/login",
        json={"email": "bad@email.com", "password": password},
    )

    assert response.status_code == 401
    assert response.json["message"] == "Invalid credentials."

def test_logout_user(client, create_user_jwts):
    response = client.post(
        "/logout",
        headers={"Authorization": f"Bearer {create_user_jwts[1]}"},
    )

    assert response.status_code == 200
    assert response.json["message"] == "Successfully logged out."

def test_logout_user_twice(client, create_user_jwts):
    client.post(
        "/logout",
        headers={"Authorization": f"Bearer {create_user_jwts[1]}"},
    )
    response = client.post(
        "/logout",
        headers={"Authorization": f"Bearer {create_user_jwts[1]}"},
    )

    assert response.status_code == 401
    assert response.json == {
        "message": "The token has been revoked.",
        "error": "token_revoked",
    }

def test_logout_user_no_token(client):
    response = client.post(
        "/logout",
    )

    assert response.status_code == 401
    assert response.json['message'] == "Request does not contain an access token."

def test_logout_user_invalid_token(client):
    response = client.post(
        "/logout",
        headers={"Authorization": "Bearer bad_token"},
    )

    assert response.status_code == 401
    assert response.json == {
        "error": "invalid_token",
        "message": "Signature verification failed.",
    }

def test_logout_user_adds_token_to_blocklist(client, create_user_jwts, mock_redis):
    refresh_token = create_user_jwts[1]

    response = client.post(
        "/logout",
        headers={"Authorization": f"Bearer {refresh_token}"}
    )

    assert response.status_code == 200
    assert response.json['message'] == "Successfully logged out."

    decoded = decode_token(refresh_token)
    jti = decoded['jti']

    assert mock_redis.exists(f"blocklist:{jti}") == 1

def test_refresh_token_invalid(client):
    response = client.post(
        "/refresh",
        headers={"Authorization": "Bearer bad_jwt"},
    )

    assert response.status_code == 401

def test_refresh_token(client, create_user_jwts):
    response = client.post(
        "/refresh",
        headers={"Authorization": f"Bearer {create_user_jwts[1]}"},
    )

    assert response.status_code == 200
    assert response.json['access_token']

# Dev endpoint tests

def test_expired_token_callback(client):
    expired_token = create_access_token(
        identity="1",
        expires_delta=timedelta(seconds=-1)
    )
    response = client.get(
        "/protected",
        headers={"Authorization": f"Bearer {expired_token}"}
    )

    assert response.status_code == 401
    assert response.json['error'] == "token_expired"
    assert response.json['message'] == "The token has expired."

def test_protected_with_access_token(client, create_user_jwts):
    response = client.get(
        "/protected", 
        headers={"Authorization": f"Bearer {create_user_jwts[0]}"}
    )
    
    assert response.status_code == 200
    assert response.json['message'] == "This is a protected endpoint."

def test_protected_without_token(client):
    response = client.get("/protected")

    assert response.status_code == 401
    assert response.json['error'] == "authorization_required"

def test_fresh_protected_with_non_fresh_token(client, create_user_jwts):
    response = client.post(
        "/refresh", 
        headers={"Authorization": f"Bearer {create_user_jwts[1]}"}
    )
    response = client.get(
        "/fresh-protected", 
        headers={"Authorization": f"Bearer {response.json['access_token']}"}
    )

    assert response.status_code == 401
    assert response.json['error'] == "fresh_token_required"

def test_fresh_protected_with_fresh_token(client, create_user_jwts):
    response = client.get(
        "/fresh-protected", 
        headers={"Authorization": f"Bearer {create_user_jwts[0]}"}
    )

    assert response.status_code == 200
    assert response.json['message'] == "This is a protected endpoint. You used a fresh token to access it."

def test_get_user_details(client, create_user_details):
    response = client.get(
        "/users/1",  # assume user id is 1
    )

    assert response.status_code == 200
    assert response.json == {
        "id": 1,
        "email": create_user_details[1],
    }

def test_get_user_details_missing(client):
    response = client.get(
        "/users/23",
    )

    assert response.status_code == 404
    assert response.json == {"code": 404, "status": "Not Found"}