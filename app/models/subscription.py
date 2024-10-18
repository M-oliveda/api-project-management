from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class SubscriptionType(str, Enum):
    monthly = "monthly"
    annual = "annual"


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[UUID] = mapped_column(primary_key=True, index=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    stripe_subscription_id: Mapped[str] = mapped_column(nullable=False)
    subscription_type: Mapped[SubscriptionType] = mapped_column(
        SQLEnum(SubscriptionType), nullable=False
    )
    start_date: Mapped[datetime] = mapped_column(
        default=datetime.now(timezone.utc), nullable=False
    )
    end_date: Mapped[datetime] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
