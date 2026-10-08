"""Сценарій 2: успішна аутентифікація (200) та помилки входу (401)."""


def test_register_login_and_me(client):
    created = client.post(
        "/api/auth/register",
        json={"email": "new@test.local", "password": "password123"},
    )
    assert created.status_code == 201
    assert created.json()["role"] == "user"
    # Хеш пароля ніколи не потрапляє у відповідь
    assert "hashed_password" not in created.json()

    login = client.post(
        "/api/auth/login",
        json={"username": "new@test.local", "password": "password123"},
    )
    assert login.status_code == 200
    body = login.json()
    assert body["token_type"] == "bearer"
    assert isinstance(body["access_token"], str) and body["access_token"]

    me = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {body['access_token']}"},
    )
    assert me.status_code == 200
    assert me.json()["email"] == "new@test.local"
    assert me.json()["role"] == "user"


def test_login_wrong_password(client):
    client.post(
        "/api/auth/register",
        json={"email": "u@test.local", "password": "password123"},
    )
    response = client.post(
        "/api/auth/login",
        json={"username": "u@test.local", "password": "wrong-password"},
    )
    assert response.status_code == 401


def test_login_unknown_user(client):
    response = client.post(
        "/api/auth/login",
        json={"username": "ghost@test.local", "password": "password123"},
    )
    assert response.status_code == 401


def test_duplicate_registration_conflict(client):
    payload = {"email": "dup@test.local", "password": "password123"}
    assert client.post("/api/auth/register", json=payload).status_code == 201
    assert client.post("/api/auth/register", json=payload).status_code == 409


def test_short_password_validation(client):
    response = client.post(
        "/api/auth/register",
        json={"email": "short@test.local", "password": "123"},
    )
    assert response.status_code == 422
