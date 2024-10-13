from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models import User, Subscription
from app.schemas.subscription import SubscriptionCreate, SubscriptionType, SubscriptionResponse
from datetime import datetime, timezone
import stripe
from app.core import app_settings
from app.utils.subscription import get_end_subscription


stripe.api_key = app_settings.STRIPE_SECRET_KEY


def create_subscription(db: Session, user_email: str, stripe_subscription_id: str, subscription_type: SubscriptionType):
    user = db.query(User).filter(User.email == user_email).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found.")

    user_already_subscribe = db.query(Subscription).filter(
        Subscription.user_id == user.id).first()

    if user_already_subscribe and user_already_subscribe.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="User already has an active subscription.")

    subscription_data = SubscriptionCreate(
        user_id=user.id, stripe_subscription_id=stripe_subscription_id, subscription_type=subscription_type)

    subscription = Subscription(
        user_id=user.id,
        stripe_subscription_id=subscription_data.stripe_subscription_id,
        subscription_type=subscription_data.subscription_type,
        start_date=datetime.now(timezone.utc),
        end_date=get_end_subscription(datetime.now(timezone.utc),
                                      subscription_data.subscription_type),
        is_active=True,
    )

    db.add(subscription)
    db.commit()
    db.refresh(subscription)

    user.subscription_id = subscription.id
    db.commit()
    db.refresh(user)

    return SubscriptionResponse(
        user_id=subscription.user_id,
        subscription_type=subscription.subscription_type,
        start_date=subscription.start_date,
        end_date=subscription.end_date,
        is_active=subscription.is_active,
    )


def cancel_subscription(db: Session, user_email: str):
    user = db.query(User).filter(User.email == user_email).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found.")

    user_unactive_subscription = db.query(Subscription).filter(
        Subscription.user_id == user.id,
        Subscription.is_active == True).first()
    if not user_unactive_subscription or not user_unactive_subscription.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not have an active subscription."
        )

    subscription_canceled = stripe.Subscription.cancel(
        user_unactive_subscription.stripe_subscription_id)

    if subscription_canceled.status != "canceled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to cancel subscription."
        )

    db.delete(user_unactive_subscription)
    db.commit()
    user.subscription_id = None
    db.commit()

    return {"message": "Subscription canceled successfully."}


def create_checkout_session(return_url: str, subscription_type: SubscriptionType, customer_email: str):
    stripe.api_key = app_settings.STRIPE_SECRET_KEY

    if subscription_type == SubscriptionType.monthly:
        price_id = app_settings.STRIPE_MONTHLY_PRICE_ID
    elif subscription_type == SubscriptionType.annual:
        price_id = app_settings.STRIPE_ANNUAL_PRICE_ID
    else:
        raise ValueError("Invalid subscription type")
    try:
        session = stripe.checkout.Session.create(
            ui_mode='embedded',
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode="subscription",
            return_url=return_url,
            customer_email=customer_email
        )
        return session
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def get_stripe_session(session_id: str):
    session = stripe.checkout.Session.retrieve(session_id)
    return session
