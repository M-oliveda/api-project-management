from fastapi import APIRouter, HTTPException, Request, Depends, Response
from sqlalchemy.orm import Session
from app.db import get_db
from app.services import (
    create_checkout_session,
    get_stripe_session,
    create_subscription,
    cancel_subscription,
)
from app.schemas import Token, SubscriptionCheckoutInformation
from app.services.auth import verify_token
from app.models.subscription import SubscriptionType
from app.core.security import decode_access_token

router = APIRouter()


@router.post("/create-checkout-session")
async def create_checkout_session_endpoint(
    request: Request, subscription_type: SubscriptionType, db: Session = Depends(get_db)
) -> SubscriptionCheckoutInformation:
    token = request.headers.get("Authorization")
    if not token or not verify_token(
        db, Token(access_token=token, token_type="bearer")
    ):
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        # Create a Stripe checkout session
        checkout_session = create_checkout_session(
            "{request_obj}/return?session_id={CHECKOUT_SESSION_ID}".format(
                request_obj=request.headers.get("Origin"),
                CHECKOUT_SESSION_ID="{CHECKOUT_SESSION_ID}",
            ),
            subscription_type,
            decode_access_token(token)["sub"],
        )

        if checkout_session.id is None or checkout_session.client_secret is None:
            raise HTTPException(
                status_code=400, detail="Failed to create checkout session"
            )

        return SubscriptionCheckoutInformation(
            id=checkout_session.id, client_secret=checkout_session.client_secret
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/stripe-session-status")
async def check_stripe_session_status(
    stripe_session_id: str,
    subscription_type: SubscriptionType,
    db: Session = Depends(get_db),
):
    from stripe import Subscription

    session = get_stripe_session(stripe_session_id)
    if session is None:
        raise HTTPException(status_code=400, detail="Invalid session ID")

    if session.status == "complete":
        if (
            session.customer is None
            or session.customer_details is None
            or session.subscription is None
            or session.customer_email is None
        ):
            raise HTTPException(
                status_code=400, detail="Invalid customer details")

        subscription_id = (
            session.subscription.id
            if isinstance(session.subscription, Subscription)
            else session.subscription
        )

        subscription = create_subscription(
            db, session.customer_email, subscription_id, subscription_type
        )

        if subscription is None:
            raise HTTPException(
                status_code=400, detail="Subscription creation failed")

        return {
            "message": "Subscription created successfully",
            "subscription": subscription,
        }

    return Response({"message": "Subscription creation failed."}, status_code=400)


@router.post("/cancel-subscription")
async def cancel_subscription_endpoint(
    request: Request, user_email: str, db: Session = Depends(get_db)
):
    token = request.headers.get("Authorization")
    if not token or not verify_token(
        db, Token(access_token=token, token_type="bearer")
    ):
        raise HTTPException(status_code=401, detail="Unauthorized")

    return cancel_subscription(db, user_email)
