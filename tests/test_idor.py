"""Сценарій 4: горизонтальне розмежування прав (IDOR) → 403 Forbidden."""


def _create_backup(client, headers, clone_id="clone-1"):
    response = client.post(
        "/api/backups",
        headers=headers,
        json={"clone_id": clone_id, "memory_hash": "a" * 32, "size_mb": 10},
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_user_cannot_delete_others_backup(client, user_a_headers, user_b_headers):
    backup_b = _create_backup(client, user_b_headers)
    response = client.delete(f"/api/backups/{backup_b['id']}", headers=user_a_headers)
    assert response.status_code == 403


def test_user_cannot_edit_others_profile(client, user_a_headers, user_b):
    response = client.patch(
        f"/api/users/{user_b['id']}",
        headers=user_a_headers,
        json={"email": "hacked@test.local"},
    )
    assert response.status_code == 403


def test_user_can_edit_own_profile(client, user_a_headers, user_a):
    response = client.patch(
        f"/api/users/{user_a['id']}",
        headers=user_a_headers,
        json={"email": "renamed-a@test.local"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == "renamed-a@test.local"


def test_user_can_delete_own_backup(client, user_a_headers):
    backup_a = _create_backup(client, user_a_headers, "clone-a")
    response = client.delete(f"/api/backups/{backup_a['id']}", headers=user_a_headers)
    assert response.status_code == 200
    listing = client.get("/api/backups", headers=user_a_headers)
    assert listing.json() == []


def test_user_sees_only_own_backups(client, user_a_headers, user_b_headers):
    """Ізоляція даних: список бекапів ніколи не містить чужих записів."""
    _create_backup(client, user_b_headers, "clone-b")

    listing_a = client.get("/api/backups", headers=user_a_headers)
    assert listing_a.json() == []

    listing_b = client.get("/api/backups", headers=user_b_headers)
    assert len(listing_b.json()) == 1
