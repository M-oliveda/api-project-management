from datetime import datetime, timedelta
from app.schemas.subscription import SubscriptionType


def get_end_subscription(start_date: datetime, subscription_type: SubscriptionType):
    if subscription_type == SubscriptionType.monthly:
        return start_date + timedelta(days=30)
    elif subscription_type == SubscriptionType.annual:
        return start_date + timedelta(days=365)
    else:
        raise ValueError("Invalid subscription type")
