from pydantic import BaseModel, UUID4
from datetime import datetime
from app.models.subscription import SubscriptionType


class SubscriptionBase(BaseModel):
    user_id: UUID4
    subscription_type: SubscriptionType


class SubscriptionCreate(SubscriptionBase):
    stripe_subscription_id: str


class SubscriptionCheckoutInformation(BaseModel):
    id: str
    client_secret: str


class SubscriptionResponse(BaseModel):
    user_id: UUID4
    subscription_type: SubscriptionType
    start_date: datetime
    end_date: datetime
    is_active: bool
