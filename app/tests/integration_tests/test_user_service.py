import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import get_db, SessionLocal
from unittest.mock import patch
from sqlalchemy import delete
from app.models import User, Base
from app.db import engine


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    # Set up database state before the tests run
    # Create all tables if they do not exist
    Base.metadata.create_all(bind=engine)

    yield

    # Teardown logic to clean up the database after tests
    # Drop all tables after tests
    Base.metadata.drop_all(bind=engine, checkfirst=True)


@pytest.fixture
def client():
    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


@pytest.fixture(autouse=False)
def clear_db_uer():
    with get_db().__next__().__enter__() as db:
        db.query(User).filter(User.email == "test@example.com").delete()
        db.commit()


def test_register_user(client):
    with patch("app.services.auth.create_user") as mock_create_user:
        mock_create_user.return_value = {"email": "test@example.com"}

        response = client.post(
            "/api/v1/auth/register/", json={"email": "test@example.com", "password": "password123"})

        assert response.status_code == 201
        assert response.json()["message"] == "User created successfully"


def test_register_user_email_already_exists(client):
    with patch("app.services.create_user") as mock_create_user:
        mock_create_user.side_effect = ValueError(
            "Email is already registered")

        response = client.post(
            "/api/v1/auth/register/", json={"email": "test@example.com", "password": "password456"})

        assert response.status_code == 400
        assert response.json()["detail"] == "Email is already registered"


def test_login_user(client):
    with patch("app.services.auth.get_user_by_email") as mock_get_user:
        with patch("app.core.security.verify_password") as mock_verify_password:
            mock_get_user.return_value = {"email": "test@example.com"}
            mock_verify_password.return_value = True

            response = client.post(
                "/api/v1/auth/login/", json={"email": "test@example.com", "password": "password123"})

            assert response.status_code == 200
            assert "access_token" in response.json()


def test_login_user_invalid_credentials(client):
    with patch("app.services.auth.get_user_by_email") as mock_get_user:
        with patch("app.core.security.verify_password") as mock_verify_password:
            mock_get_user.return_value = {"email": "test@example.com"}
            mock_verify_password.return_value = False

            response = client.post(
                "/api/v1/auth/login/", json={"email": "test@example.com", "password": "wrongpassword"})

            assert response.status_code == 401
            assert response.json()["detail"] == "Invalid credentials"
