from fastapi import HTTPException
import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session
from app.schemas.auth import UserCreate, UserLogin
from app.services import create_user, login_user, authenticate_user
from app.services.auth import get_user_by_email
from app.core.security import get_password_hash, verify_password


class TestAuthService:

    @pytest.fixture
    def mock_db(self):
        # Mocking a SQLAlchemy session
        return MagicMock(spec=Session)

    @pytest.fixture
    def mock_user_data(self):
        # Return a mock user object with attributes like email and hashed_password
        mock_user = MagicMock()
        mock_user.email = "test@example.com"
        mock_user.hashed_password = get_password_hash("password123")
        return mock_user

    def test_get_user_by_email(self, mock_db, mock_user_data):
        # Mock the return value of querying the database
        mock_db.query().filter().first.return_value = mock_user_data

        user = get_user_by_email(mock_db, mock_user_data.email)
        assert user is not None
        assert user.email == mock_user_data.email

    def test_create_user_success(self, mock_db, mock_user_data):
        user_create = UserCreate(
            email=mock_user_data.email, password="password123")

        # Mock the behavior of checking if a user already exists
        mock_db.query().filter().first.return_value = None

        with patch("app.core.security.get_password_hash", return_value=mock_user_data.hashed_password):
            new_user = create_user(mock_db, user_create)
            assert new_user is not None
            assert new_user.email == user_create.email
            assert verify_password(user_create.password,
                                   new_user.hashed_password)

    def test_create_user_email_exists(self, mock_db, mock_user_data):
        user_create = UserCreate(
            email=mock_user_data.email, password="password123")

        # Mock the behavior of an existing user in the database
        mock_db.query().filter().first.return_value = mock_user_data

        with pytest.raises(ValueError, match="Email is already registered"):
            create_user(mock_db, user_create)

    def test_authenticate_user_success(self, mock_db, mock_user_data):
        # Mock the return value of querying the database
        mock_db.query().filter().first.return_value = mock_user_data

        authenticated_user = authenticate_user(
            mock_db, mock_user_data.email, "password123")
        assert authenticated_user is not None
        assert authenticated_user.email == mock_user_data.email

    def test_authenticate_user_invalid_password(self, mock_db, mock_user_data):
        # Mock the return value of querying the database
        mock_db.query().filter().first.return_value = mock_user_data

        authenticated_user = authenticate_user(
            mock_db, mock_user_data.email, "wrongpassword")
        assert authenticated_user is None

    def test_login_user_success(self, mock_db, mock_user_data):
        login_data = UserLogin(
            email=mock_user_data.email, password="password123")

        # Mock the behavior of the authentication function
        with patch("app.services.auth.authenticate_user", return_value=mock_user_data):
            token = login_user(mock_db, login_data)
            assert token is not None
            assert "access_token" in token

    def test_login_user_invalid_credentials(self, mock_db, mock_user_data):
        login_data = UserLogin(email=mock_user_data.email,
                               password="wrongpassword")

        with patch("app.services.auth.authenticate_user", return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                login_user(mock_db, login_data)

            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "Invalid credentials"
