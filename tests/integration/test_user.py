import pytest

@pytest.fixture()
def create_user_details(client):
    username = "user"
    email = "test@example.com"
    password = "abc123"
    client.post(
        "/register",
        json={"username": username, "email": email, "password": password},
    )

    return username, email, password

@pytest.fixture()
def create_user_jwts(client, create_user_details):
    _, email, password = create_user_details
    response = client.post(
        "/login",
        json={"email": email, "password": password},
    )

    return response.json['access_token'], response.json['refresh_token']

def test_register_user(client):
    username = "user"
    email = "test@example.com"
    response = client.post(
        "/register",
        json={"username": username, "email": email, "password": "abc123"},
    )

    assert response.status_code == 201
    assert response.json == {"message": "User created successfully."}


def test_register_user_already_exists(client):
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

def test_register_user_missing_data(client):
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

def test_get_user_details(client, create_user_details):
    response = client.get(
        "/user/1",  # assume user id is 1
    )

    assert response.status_code == 200
    assert response.json == {
        "id": 1,
        "email": create_user_details[1],
    }

def test_get_user_details_missing(client):
    response = client.get(
        "/user/23",
    )

    assert response.status_code == 404
    assert response.json == {"code": 404, "status": "Not Found"}

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