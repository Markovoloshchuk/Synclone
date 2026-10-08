"""Сценарій 1: анонімний доступ до захищених маршрутів → 401 Unauthorized."""

VALID_BACKUP = {
    "clone_id": "clone-x",
    "memory_hash": "abcdef1234567890",
    "size_mb": 5,
}


def test_me_requires_auth(client):
    assert client.get("/api/users/me").status_code == 401


def test_backups_require_auth(client):
    assert client.get("/api/backups").status_code == 401
    assert client.post("/api/backups", json=VALID_BACKUP).status_code == 401
    assert client.delete("/api/backups/1").status_code == 401


def test_admin_requires_auth(client):
    assert client.get("/api/admin/users").status_code == 401
    assert client.get("/api/admin/stats").status_code == 401


def test_garbage_token_rejected(client):
    response = client.get(
        "/api/users/me", headers={"Authorization": "Bearer not-a-real-jwt"}
    )
    assert response.status_code == 401


def test_public_resources_still_available(client):
    """Публічні ресурси не потребують авторизації."""
    assert client.get("/health").status_code == 200
    assert client.get("/login.html").status_code == 200
    assert client.get("/register.html").status_code == 200
