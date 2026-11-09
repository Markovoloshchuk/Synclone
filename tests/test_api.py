import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.core.security import create_access_token, get_password_hash
from app.main import app
from app.models.user import User, UserRole

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


async def override_get_db():
    async with TestSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def ac():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


@pytest.fixture
async def normal_user_token():
    async with TestSessionLocal() as session:
        user = User(
            email="user@example.com",
            full_name="Regular User",
            password_hash=get_password_hash("password123"),
            role=UserRole.USER,
            is_active=True,
        )
        session.add(user)
        await session.commit()
    return create_access_token(data={"sub": "user@example.com", "role": UserRole.USER})


@pytest.fixture
async def admin_user_token():
    async with TestSessionLocal() as session:
        admin = User(
            email="admin@example.com",
            full_name="Admin User",
            password_hash=get_password_hash("adminpassword123"),
            role=UserRole.ADMIN,
            is_active=True,
        )
        session.add(admin)
        await session.commit()
    return create_access_token(
        data={"sub": "admin@example.com", "role": UserRole.ADMIN}
    )


# --- ТЕСТИ АВТЕНТИФІКАЦІЇ ТА ДОСТУПУ ---


@pytest.mark.asyncio
async def test_register_user(ac: AsyncClient):
    response = await ac.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "securepassword123",
            "full_name": "New User",
            "role": "user",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert "id" in data


@pytest.mark.asyncio
async def test_login_success_and_failure(ac: AsyncClient):
    async with TestSessionLocal() as session:
        user = User(
            email="login@example.com",
            full_name="Login Test",
            password_hash=get_password_hash("correctpassword"),
            role=UserRole.USER,
            is_active=True,
        )
        session.add(user)
        await session.commit()

    # 1. Успішний вхід (200 OK)
    response = await ac.post(
        "/api/v1/auth/login",
        json={"email": "login@example.com", "password": "correctpassword"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

    # 2. Невдалий вхід -> 401 Unauthorized
    response_fail = await ac.post(
        "/api/v1/auth/login",
        json={"email": "login@example.com", "password": "wrongpassword"},
    )
    assert response_fail.status_code == 401


@pytest.mark.asyncio
async def test_anonymous_access_forbidden(ac: AsyncClient):
    response = await ac.get("/api/v1/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_vertical_role_separation(ac: AsyncClient, normal_user_token: str):
    response = await ac.get(
        "/api/v1/admin/users", headers={"Authorization": f"Bearer {normal_user_token}"}
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_access_allowed(ac: AsyncClient, admin_user_token: str):
    response = await ac.get(
        "/api/v1/admin/users", headers={"Authorization": f"Bearer {admin_user_token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_horizontal_privilege_separation_idor(
    ac: AsyncClient, normal_user_token: str
):
    response = await ac.patch(
        "/api/v1/admin/users/1/role?role=admin",
        headers={"Authorization": f"Bearer {normal_user_token}"},
    )
    assert response.status_code == 403
