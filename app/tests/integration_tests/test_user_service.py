import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import get_db
from unittest.mock import patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.models import User, Base
from fastapi import HTTPException
from app.core import app_settings

# Use an in-memory SQLite database for testing


# Create the engine and session maker
engine = create_engine(
    app_settings.TEST_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


@pytest.fixture(scope="module")
def setup_db():
    # Create tables for testing
    Base.metadata.create_all(bind=engine)

    yield

    # Drop tables after tests
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(setup_db):
    def override_get_db():
        # Use the same session for all tests so the in-memory database persists
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


@pytest.fixture
def clear_db_user():
    db = TestingSessionLocal()
    try:
        # Delete any user with the test email before and after the test
        db.query(User).filter(User.email == "test@example.com").delete()
        db.commit()
        yield
        db.query(User).filter(User.email == "test@example.com").delete()
        db.commit()
    finally:
        db.close()


class TestUserService:
    def test_register_user(self, client):
        with patch("app.services.auth.create_user") as mock_create_user:
            mock_create_user.return_value = {"email": "test@example.com"}

            response = client.post(
                "/api/v1/auth/register/", json={"email": "test@example.com", "password": "password123"}
            )

            assert response.status_code == 201
            assert response.json()["message"] == "User created successfully"

    def test_register_user_email_already_exists(self, client):
        with patch("app.services.auth.create_user") as mock_create_user:
            # Make sure the mock correctly simulates an existing user scenario
            def mock_create_user_side_effect(*args, **kwargs):
                raise HTTPException(
                    status_code=400, detail="Email is already registered"
                )

            mock_create_user.side_effect = mock_create_user_side_effect

            response = client.post(
                "/api/v1/auth/register/", json={"email": "test@example.com", "password": "password456"}
            )

            assert response.status_code == 400
            assert response.json()["detail"] == "Email is already registered"

    def test_login_user(self, client):
        with patch("app.services.auth.get_user_by_email") as mock_get_user:
            with patch("app.core.security.verify_password") as mock_verify_password:
                mock_get_user.return_value = {
                    "email": "test@example.com", "password": "hashedpassword"
                }
                mock_verify_password.return_value = True

                response = client.post(
                    "/api/v1/auth/login/", json={"email": "test@example.com", "password": "password123"}
                )

                assert response.status_code == 200
                assert "access_token" in response.json()

    def test_login_user_invalid_credentials(self, client, clear_db_user):
        with patch("app.services.auth.get_user_by_email") as mock_get_user:
            with patch("app.core.security.verify_password") as mock_verify_password:
                mock_get_user.return_value = {"email": "test@example.com"}
                mock_verify_password.return_value = False

                response = client.post(
                    "/api/v1/auth/login/", json={"email": "test@example.com", "password": "wrongpassword"}
                )

                assert response.status_code == 401
                assert response.json()["detail"] == "Invalid credentials"
