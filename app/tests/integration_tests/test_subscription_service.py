import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import get_db
from unittest.mock import patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.models import User, Subscription, Base
from app.schemas.subscription import SubscriptionType
from app.core import app_settings
from uuid import uuid4

# Create a test engine and session for SQLite
engine = create_engine(
    app_settings.TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def client(setup_db):
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


@pytest.fixture()
def clear_db_user():
    db = TestingSessionLocal()
    db.query(User).filter(User.email == "test@example.com").delete()
    db.commit()
    yield
    db.query(User).filter(User.email == "test@example.com").delete()
    db.commit()


class TestSubscriptionService:
    @pytest.fixture()
    def create_test_user(self, client):
        # Test user credentials
        user_data = {"email": "test@example.com", "password": "password123"}

        # Attempt to log in first
        login_response = client.post("/api/v1/auth/login/", json=user_data)
        if login_response.status_code == 200:
            return login_response.json()["access_token"]

        # If login fails (user not found), register the user
        register_response = client.post("/api/v1/auth/register/", json=user_data)
        assert register_response.status_code == 201

        # Login again to get the access token
        login_response = client.post("/api/v1/auth/login/", json=user_data)
        assert login_response.status_code == 200
        return login_response.json()["access_token"]

    @patch(
        "app.services.subscription.stripe.Subscription.create",
        return_value={"id": "sub_test_123", "client_secret": "test_client_secret"},
    )
    @patch("stripe.checkout.Session.retrieve")
    def test_create_subscription(
        self, mock_retrieve_session, mock_create_subscription, client, create_test_user
    ):
        # Mock the Stripe subscription creation
        mock_create_subscription.return_value = {
            "id": "sub_test_123",
            "client_secret": "test_client_secret",
        }

        # Set the Authorization header with the token
        headers = {
            "Authorization": create_test_user,
            "Origin": "https://yourdomain.com",
        }

        mock_stripe_session = MagicMock()
        mock_stripe_session.status = "complete"
        mock_stripe_session.customer = "some_customer"
        mock_stripe_session.customer_details = "some_customer_details"
        mock_stripe_session.subscription = "some_subscription"
        mock_stripe_session.customer_email = "test@example.com"
        mock_retrieve_session.stripe_subscription_id = "sub_test_123"

        mock_retrieve_session.return_value = mock_stripe_session

        with patch(
            "app.services.create_checkout_session",
            return_value={
                "client_secret": "test_client_secret",
                "id": "test_session_id",
                "success_url": "https://yourdomain.com/success?session_id={CHECKOUT_SESSION_ID}",
                "cancel_url": "https://yourdomain.com/cancel",
            },
        ):
            response = client.post(
                f"/api/v1/subscription/create-checkout-session?subscription_type="
                f"{SubscriptionType.monthly.value}",
                headers=headers,
            )

            register_response = client.get(
                "api/v1/subscription/stripe-session-status?stripe_session_id=test_session_id&subscription_type=monthly",
                headers=headers,
            )

        print(response, register_response)
        assert response.status_code == 200
        assert response.json()["id"] is not None
        assert response.json()["client_secret"] is not None

        assert register_response.status_code == 200
        assert (
            register_response.json()["message"] == "Subscription created successfully"
        )

    def test_cancel_subscription_user_not_found(self, client, create_test_user):
        # Set the Authorization header with the token
        headers = {
            "Authorization": create_test_user,
            "Origin": "https://yourdomain.com",
        }

        response = client.post(
            f"/api/v1/subscription/cancel-subscription?user_email=nonexistent@example.com",
            headers=headers,
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "User not found."

    def test_cancel_subscription_sucessful(self, client, create_test_user):
        # Set the Authorization hader with the token
        headers = {
            "Authorization": create_test_user,
            "Origin": "https://yourdomain.com",
        }

        mock_stripe_subscription = MagicMock()
        mock_stripe_subscription.status = "canceled"

        with patch("stripe.Subscription.cancel", return_value=mock_stripe_subscription):
            response = client.post(
                "/api/v1/subscription/cancel-subscription?user_email=test@example.com",
                headers=headers,
            )

        assert response.status_code == 200
        assert response.json()["message"] == "Subscription canceled successfully."

    def test_cancel_subscription_no_active_subscription(self, client, create_test_user):
        # Set the Authorization header with the token
        headers = {
            "Authorization": create_test_user,
            "Origin": "https://yourdomain.com",
        }

        response = client.post(
            "/api/v1/subscription/cancel-subscription?user_email=test@example.com",
            headers=headers,
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "User does not have an active subscription."
