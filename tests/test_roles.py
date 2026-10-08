"""Сценарій 3: вертикальне розмежування ролей → 403 Forbidden."""


def test_user_gets_403_on_admin_routes(client, user_a_headers, user_a):
    """Звичайний користувач не має доступу до жодного /api/admin/*."""
    for url in ("/api/admin/users", "/api/admin/backups", "/api/admin/stats"):
        response = client.get(url, headers=user_a_headers)
        assert response.status_code == 403, url

    response = client.patch(
        f"/api/admin/users/{user_a['id']}",
        headers=user_a_headers,
        json={"is_active": False},
    )
    assert response.status_code == 403


def test_admin_gets_200_on_admin_routes(client, admin_headers):
    """Адміністратор проходить на ті самі маршрути."""
    response = client.get("/api/admin/users", headers=admin_headers)
    assert response.status_code == 200

    stats = client.get("/api/admin/stats", headers=admin_headers)
    assert stats.status_code == 200
    # Щонайменше сід-адміністратор має бути в базі
    assert stats.json()["users"] >= 1


def test_admin_can_deactivate_user(client, admin_headers, user_a):
    response = client.patch(
        f"/api/admin/users/{user_a['id']}",
        headers=admin_headers,
        json={"is_active": False},
    )
    assert response.status_code == 200
    assert response.json()["is_active"] is False

    # Деактивований користувач більше не може увійти → 401
    login = client.post(
        "/api/auth/login",
        json={"username": "user-a@test.local", "password": "password123"},
    )
    assert login.status_code == 401
