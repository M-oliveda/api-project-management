import jwt
from datetime import timedelta

import pytest
from app.core.security import decode_access_token, verify_password, get_password_hash, create_access_token
from app.core.config import ApplicationSettings


@pytest.fixture
def test_app_settings():
    return ApplicationSettings(
        JWT_SECRET_KEY="test-secret",
        JWT_ALGORITHM="HS256"
    )


class TestSecurity:
    def test_verify_password(self, test_app_settings):
        password = "testpassword"
        hashed_password = get_password_hash(password)
        assert verify_password(password, hashed_password) is True
        assert verify_password(
            "wrongpassword", hashed_password) is False

    def test_get_password_hash(self, test_app_settings):
        password = "testpassword"
        assert get_password_hash(
            password) != get_password_hash(password)

    def test_create_access_token(self, test_app_settings):
        data = {"sub": "testuser"}
        token = create_access_token(data, timedelta(minutes=30))
        assert isinstance(token, str) is True
        payload = jwt.decode(
            token,
            test_app_settings.JWT_SECRET_KEY,
            algorithms=[test_app_settings.JWT_ALGORITHM],
            # Disable signature verification for test purposes
            options={"verify_signature": False}
        )
        assert payload is not None
        assert payload["sub"] == "testuser"

    def test_decode_access_token(self, test_app_settings):
        data = {"sub": "testuser"}
        token = create_access_token(data, timedelta(minutes=30))
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "testuser"

    def test_decode_access_token_expired(self, test_app_settings):
        data = {"sub": "testuser"}
        token = create_access_token(
            data, timedelta(seconds=-1))  # Create an expired token
        with pytest.raises(jwt.ExpiredSignatureError):
            decode_access_token(token)

    def test_decode_access_token_invalid(self, test_app_settings):
        invalid_token = "invalid-token"
        with pytest.raises(jwt.InvalidTokenError):
            decode_access_token(invalid_token)
#
