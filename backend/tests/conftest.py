import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import main as app_module
from app.database.base import Base
from app.database.connection import get_db
from app.main import app


@pytest.fixture
def client(monkeypatch):
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestSession = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=test_engine)
    monkeypatch.setattr(app_module, "engine", test_engine)
    monkeypatch.setattr(app_module, "SessionLocal", TestSession)

    def override_get_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=test_engine)
        test_engine.dispose()


def register_and_login(client: TestClient, username: str) -> str:
    email = f"{username}@example.com"
    response = client.post(
        "/api/auth/register",
        json={"username": username, "email": email, "password": "test-password-123"},
    )
    assert response.status_code == 201
    response = client.post(
        "/api/auth/login",
        data={"username": username, "password": "test-password-123"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]
