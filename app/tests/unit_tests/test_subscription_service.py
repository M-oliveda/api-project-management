import pytest
from unittest.mock import patch, MagicMock
from app.services import create_subscription, cancel_subscription
from app.schemas.subscription import SubscriptionType
from app.models import User, Subscription
from fastapi import HTTPException
from datetime import datetime, timezone
from uuid import uuid4

# Mock data for tests
MOCK_USER_EMAIL = "test@example.com"
MOCK_STRIPE_SUBSCRIPTION_ID = "sub_test_123"
MOCK_USER_ID = uuid4()
MOCK_SUBSCRIPTION_ID = "mock-subscription-id"


def mock_user():
    # Mock a User object
    user = MagicMock()
    user.id = MOCK_USER_ID
    user.email = MOCK_USER_EMAIL
    user.subscription_id = None
    return user


def mock_subscription():
    # Mock a Subscription object
    subscription = MagicMock()
    subscription.id = MOCK_SUBSCRIPTION_ID
    subscription.user_id = MOCK_USER_ID
    subscription.stripe_subscription_id = MOCK_STRIPE_SUBSCRIPTION_ID
    subscription.is_active = True
    return subscription


@pytest.fixture
def db_session():
    # Mock database session
    session = MagicMock()
    session.delete = MagicMock()
    session.commit = MagicMock()
    session.refresh = MagicMock()
    return session


class TestSubscription:

    def test_create_subscription(self, db_session):
        # Mock the user and subscription
        user = mock_user()
        subscription = mock_subscription()

        # Mock the query and filtering methods
        # First call returns user, second returns no subscription
        db_session.query().filter().first.side_effect = [user, None]

        with patch('app.services.create_subscription', return_value=subscription):
            response = create_subscription(
                db=db_session,
                user_email=MOCK_USER_EMAIL,
                stripe_subscription_id=MOCK_STRIPE_SUBSCRIPTION_ID,
                subscription_type=SubscriptionType.monthly
            )

        # Assertions
        assert response.user_id == MOCK_USER_ID
        assert response.subscription_type == SubscriptionType.monthly
        assert response.is_active is True
        db_session.add.assert_called_once()
        db_session.commit.assert_called()
        db_session.refresh.assert_called()

    def test_create_subscription_user_not_found(self, db_session):
        # Mock no user found
        db_session.query().filter().first.return_value = None

        with pytest.raises(HTTPException) as excinfo:
            create_subscription(
                db=db_session,
                user_email="nonexistent@example.com",
                stripe_subscription_id=MOCK_STRIPE_SUBSCRIPTION_ID,
                subscription_type=SubscriptionType.monthly
            )

        assert excinfo.value.status_code == 404
        assert excinfo.value.detail == "User not found."

    def test_create_subscription_user_already_subscribed(self, db_session):
        user = mock_user()
        subscription = mock_subscription()

        # Mock the query and filtering methods
        # First call returns user, second returns active subscription
        db_session.query().filter().first.side_effect = [user, subscription]

        with pytest.raises(HTTPException) as excinfo:
            create_subscription(
                db=db_session,
                user_email=MOCK_USER_EMAIL,
                stripe_subscription_id=MOCK_STRIPE_SUBSCRIPTION_ID,
                subscription_type=SubscriptionType.monthly
            )

        assert excinfo.value.status_code == 400
        assert excinfo.value.detail == "User already has an active subscription."

    @patch("stripe.Subscription.cancel", return_value=MagicMock(status="canceled"))
    def test_cancel_subscription_successful(self, db_session):
        # Set up the mock user and subscription
        user = mock_user()
        subscription = mock_subscription()

        # Mock the query and filtering methods
        db_session.query().filter().first.side_effect = [
            user, subscription]

        # Call the actual function being tested
        response = cancel_subscription(db_session, user.email)

        # Assertions
        assert response is not None
        assert response.get("message") == "Subscription canceled successfully."

        # Ensure delete is called with the mock subscription object
        # db_session.delete.assert_called_once_with(subscription)
        assert db_session.commit.call_count == 1

    @patch('stripe.Subscription.cancel')
    def test_cancel_subscription_user_not_found(stripe_cancel_mock, db_session):
        # Mock no user found
        db_session.query().filter().first.return_value = None

        with pytest.raises(HTTPException) as excinfo:
            cancel_subscription(db_session, "nonexistent@example.com")

        assert excinfo.value.status_code == 404
        assert excinfo.value.detail == "User not found."

    @patch('stripe.Subscription.cancel')
    def test_cancel_subscription_no_active_subscription(stripe_cancel_mock, db_session):
        user = mock_user()

        # Mock the query and filtering methods
        # First call returns user, second returns no active subscription
        db_session.query().filter().first.side_effect = [user, None]

        with pytest.raises(HTTPException) as excinfo:
            cancel_subscription(db_session, MOCK_USER_EMAIL)

        assert excinfo.value.status_code == 404
        assert excinfo.value.detail == "User does not have an active subscription."
