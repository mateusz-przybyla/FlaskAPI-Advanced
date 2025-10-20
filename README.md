# FlaskAPI-Advanced

Advanced Flask REST API boilerplate with JWT authentication, PostgreSQL, Redis, background jobs, Mailgun integration and tests.

---

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
    - [Local setup](#local-setup)
    - [Docker setup](#docker-setup)
- [Database Schema](#database-schema)
- [Endpoints](#endpoints)
    - [Auth](#auth)
    - [Test auth](#test-auth)
    - [User management (dev only)](#user-management-dev-only)
- [Validation and Errors](#validation-and-errors)
- [Background Jobs and emails](#background-jobs-and-emails)
- [Testing](#testing)

---

## Features

- JWT authentication (access + refresh tokens)
- Token revocation stored in **Redis**
- PostgreSQL database with **SQLAlchemy** and **Flask-Migrate**
- Background job queue using **RQ** and **Redis**
- Email sending via **Mailgun API**
- API documentation with **Swagger UI** (via Flask-Smorest) available at [`/swagger-ui`](http://localhost:5000/swagger-ui)
- Database migrations with **Flask-Migrate / Alembic**
- Environment variable support via `.env` / `.flaskenv`
- Docker and docker-compose setup
- Unit and integration tests with **pytest**

---

## Requirements

- Python 3.13
- Flask
- Flask-Smorest
- SQLAlchemy
- Flask-SQLAlchemy
- Flask-Migrate
- Flask-JWT-Extended
- Passlib
- python-dotenv
- Redis
- requests
- rq
- psycopg2
- Docker & Docker Compose

See [requirements.txt](requirements.txt) and [requirements-dev.txt](requirements-dev.txt).

---

## Installation

### Local setup

- Clone repository

```bash
git clone https://github.com/mateusz-przybyla/FlaskAPI-Advanced.git
cd FlaskAPI-Advanced
```

- Create virtual environment (Windows Powershell)

```bash
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

- Install dependencies

```bash
pip install -r requirements-dev.txt
```

- Copy and configure environment variables

```bash
copy .env.example .env (Windows Powershell)
# then edit .env and set your values, e.g.:

# --- Flask / JWT ---
JWT_SECRET_KEY=your_jwt_secret_key

# --- Database (PostgreSQL) ---
DATABASE_URL=postgresql://postgres:password@host.docker.internal:5432/flask-api
DB_USERNAME=postgres
DB_PASSWORD=password
DB_DATABASE=flask-api

# --- Redis ---
REDIS_URL=redis://host.docker.internal:6379

# --- Mailgun ---
MAILGUN_API_KEY=your-mailgun-api-key
MAILGUN_DOMAIN=your-domain.mailgun.org
```

Note:
If you’re using Docker Desktop (on Windows or macOS), host.docker.internal allows containers to communicate with the host machine.

- Start Redis, Database and Worker via Docker

```bash
docker compose up -d db redis rq_worker 
```

- Initialize database

```bash
flask db upgrade
```

- Run the Flask app

```bash
flask run
```

App will start at: http://localhost:5000

### Docker setup

- Copy environment variables file

```bash
copy .env.example .env (Windows Powershell)
# then edit .env and set your values, e.g.:

# --- Flask / JWT ---
JWT_SECRET_KEY=your_jwt_secret_key

# --- Database (PostgreSQL) ---
DATABASE_URL=postgresql://postgres:password@db:5432/flask-api
DB_USERNAME=postgres
DB_PASSWORD=password
DB_DATABASE=flask-api

# --- Redis ---
REDIS_URL=redis://redis:6379

# --- Mailgun ---
MAILGUN_API_KEY=your-mailgun-api-key
MAILGUN_DOMAIN=your-domain.mailgun.org
```

- Build image and start container

```bash
docker compose up -d --build
```

- Run migrations inside container

```bash
docker compose exec web flask db upgrade
```

- Check logs

```bash
docker compose logs -f
```

- Stop and remove containers

```bash
docker compose down
```

---

## Database Schema

![](/readme/database-schema.jpg)

---

## Endpoints

### Auth

- **POST** `/register`\
  Register a new user.\
  **Request:** `{ "username": "mateusz", "email": "user@example.com", "password": "secret123" }`\
  **Response:** `{ "message": "User created successfully." }`, `201 Created`\
  **Errors:**
    - `409 Conflict` → email already exists
    - `500 Internal Server Error` → database issue

- **POST** `/login`\
  Authenticate user and return tokens.\
  **Request:** `{ "email": "user@example.com", "password": "secret123" }`\
  **Response:** `{ "access_token": "...", "refresh_token": "..." }`, `200 OK`\
  **Errors:**
    - `401 Unauthorized` → invalid credentials

- **POST** `/refresh`\
  Get new access token using refresh token.\
  **Headers:** `Authorization: Bearer <refresh_token>`\
  **Response:** `{ "access_token": new_token}`, `200 OK`\
  **Errors:**
    - `401 Unauthorized` → expired/invalid/blacklisted refresh token

- **POST** `/logout`\
  Revoke current refresh token.\
  **Headers:** `Authorization: Bearer <refresh_token>`\
  **Response:** `{ "message": "Successfully logged out." }`, `200 OK`

### Test Auth

Endpoints for verifying JWT behavior:

- **GET** `/guest` → open for everyone (no token required)
- **GET** `/protected` → requires valid access token
- **GET** `/fresh-protected` → requires fresh token (i.e. directly from login, not from refresh)

### User management (dev only)

- **GET** `/user/<id>`\
  Fetch user by id.\
  **Response:** `200 OK` → with user data\
  **Errors:** 
    - `404 Not Found` → if user doesnt't exist
- **DELETE** `/user/<id>`\
  Delete user.\
  **Response:** `{ "message": "User deleted." }`, `200 OK`\
  **Errors:**
    - `404 Not Found` → if user doesnt't exist
    - `500 Internal Server Error` → on database issue

---

## Validation and Errors

- Common JWT errors (always return `401 Unauthorized`)
    - Missing token

    ```json
    {
        "message": "Request does not contain an access token.",
        "error": "authorization_required"
    }
    ```

    - Invalid token

    ```json
    {
        "message": "Signature verification failed.",
        "error": "invalid_token"
    }
    ```

    - Expired token

    ```json
    {
        "message": "The token has expired.",
        "error": "token_expired"
    }
    ```    

    - Revoked token

    ```json
    {
        "message": "The token has been revoked.",
        "error": "token_revoked"
    }
    ```  

    - Non-fresh token on fresh-only endpoint

    ```json
    {
        "message": "The token is not fresh.",
        "error": "fresh_token_required"
    }
    ```      

- Validation errors (`422 Unprocessable Entity`)

  If request body fails schema validation (Marshmallow), errors are returned per field:

    ```json
    {
        "email": ["Not a valid email address."],
        "password": ["Shorter than minimum length 6."]
    }
    ```

- Resource errors
    - Duplicate user (`409 Conflict`)

    ```json
    {
        "message": "A user with that email already exists."
    }
    ```

    - User not found (`404 Not Found`)

    ```json
    {
        "message": "User not found."
    }
    ```

    - Database errors (`500 Internal Server Error`)

    ```json
    {
        "message": "An error occurred while creating the user."
    }
    ```

---

## Background Jobs and Emails

The api integrates RQ (Redis Queue) for background task processing.

- Example job: send welcome email after user registration.
- Worker defined in mail_worker.py listens to the emails queue.

Example flow:

- User registers
- Flask api enqueues job → Redis
- mail_worker picks job → sends email via Mailgun

## Testing

Run all tests:

```bash
pytest -v
```

Run all tests with coverage:

```bash
pytest -v --cov=api tests/
```

Run all tests with coverage via Docker:

```bash
docker-compose exec web pytest -v --cov=api tests/
```

Test structure:
- `tests/unit/` → models, schemas, helpers
- `tests/integration/` → auth flow, protected endpoints