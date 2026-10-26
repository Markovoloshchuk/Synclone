"""Small contract tests; 

Full API integration tests require a PostgreSQL test database.
    """

from app.core.security import hash_password, verify_password


def test_password_hash_is_not_plaintext():
    password = "a-long-test-password"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong-password", hashed)


def test_password_hash_is_salted():
    password = "a-long-test-password"
    assert hash_password(password) != hash_password(password)
