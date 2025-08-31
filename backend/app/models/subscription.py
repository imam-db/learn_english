"""
Subscription and payment models for freemium monetization
"""

from sqlalchemy import (
    Boolean, Column, String, Text, Integer, 
    ForeignKey, Index, CheckConstraint,
    Numeric
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from .base import Base


class Subscription(Base):
    """User subscription management"""
    
    __tablename__ = "subscriptions"
    
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Subscription details
    plan_type = Column(String(50), default="free", nullable=False)
    status = Column(String(20), default="active", nullable=False)
    
    # Billing
    billing_cycle = Column(String(20), nullable=True)  # monthly, yearly
    price = Column(Numeric(10, 2), default=0, nullable=False)
    currency = Column(String(3), default="IDR", nullable=False)
    
    # Dates
    started_at = Column(String, nullable=False)
    current_period_start = Column(String, nullable=False)
    current_period_end = Column(String, nullable=False)
    canceled_at = Column(String, nullable=True)
    ended_at = Column(String, nullable=True)
    
    # Trial
    trial_start = Column(String, nullable=True)
    trial_end = Column(String, nullable=True)
    is_trial = Column(Boolean, default=False, nullable=False)
    
    # Payment gateway integration
    external_subscription_id = Column(String(255), nullable=True)  # Midtrans, etc.
    payment_method = Column(String(50), nullable=True)
    
    # Usage tracking (for free tier limits)
    daily_lessons_used = Column(Integer, default=0, nullable=False)
    last_usage_reset = Column(String, nullable=True)  # Date of last daily reset
    
    # Metadata
    subscription_metadata = Column(JSONB, default=dict)
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")
    payment_transactions = relationship("PaymentTransaction", back_populates="subscription")
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "plan_type IN ('free', 'pro', 'premium', 'enterprise')",
            name="valid_plan_type"
        ),
        CheckConstraint(
            "status IN ('active', 'canceled', 'expired', 'suspended', 'pending')",
            name="valid_subscription_status"
        ),
        CheckConstraint(
            "billing_cycle IN ('monthly', 'yearly', 'lifetime') OR billing_cycle IS NULL",
            name="valid_billing_cycle"
        ),
        CheckConstraint(
            "currency IN ('IDR', 'USD')",
            name="valid_currency"
        ),
        CheckConstraint(
            "price >= 0",
            name="valid_price"
        ),
        CheckConstraint(
            "daily_lessons_used >= 0",
            name="valid_daily_usage"
        ),
        Index("idx_subscriptions_user", "user_id"),
        Index("idx_subscriptions_status", "status"),
        Index("idx_subscriptions_plan", "plan_type"),
        Index("idx_subscriptions_external", "external_subscription_id"),
        Index("idx_subscriptions_period", "current_period_start", "current_period_end"),
    )


class PaymentTransaction(Base):
    """Payment transaction records"""
    
    __tablename__ = "payment_transactions"
    
    subscription_id = Column(
        UUID(as_uuid=True),
        ForeignKey("subscriptions.id", ondelete="CASCADE"),
        nullable=False
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Transaction details
    transaction_type = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False)
    
    # Amount
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="IDR", nullable=False)
    
    # Payment gateway details
    payment_method = Column(String(50), nullable=False)
    gateway = Column(String(50), nullable=False)  # midtrans, gopay, ovo, etc.
    external_transaction_id = Column(String(255), nullable=True)
    gateway_response = Column(JSONB, default=dict)
    
    # Timestamps
    initiated_at = Column(String, nullable=False)
    completed_at = Column(String, nullable=True)
    failed_at = Column(String, nullable=True)
    
    # Billing period covered by this transaction
    billing_period_start = Column(String, nullable=True)
    billing_period_end = Column(String, nullable=True)
    
    # Metadata
    description = Column(Text, nullable=True)
    invoice_number = Column(String(100), nullable=True)
    receipt_url = Column(String(500), nullable=True)
    
    # Refund information
    refunded_amount = Column(Numeric(10, 2), default=0, nullable=False)
    refunded_at = Column(String, nullable=True)
    refund_reason = Column(Text, nullable=True)
    
    # Relationships
    subscription = relationship("Subscription", back_populates="payment_transactions")
    user = relationship("User")
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "transaction_type IN ('subscription', 'upgrade', 'renewal', 'refund', 'chargeback')",
            name="valid_transaction_type"
        ),
        CheckConstraint(
            "status IN ('pending', 'processing', 'completed', 'failed', 'canceled', 'refunded')",
            name="valid_transaction_status"
        ),
        CheckConstraint(
            "gateway IN ('midtrans', 'gopay', 'ovo', 'dana', 'bank_transfer', 'credit_card')",
            name="valid_payment_gateway"
        ),
        CheckConstraint(
            "amount > 0",
            name="valid_transaction_amount"
        ),
        CheckConstraint(
            "refunded_amount >= 0 AND refunded_amount <= amount",
            name="valid_refunded_amount"
        ),
        Index("idx_payment_transactions_subscription", "subscription_id"),
        Index("idx_payment_transactions_user", "user_id"),
        Index("idx_payment_transactions_status", "status"),
        Index("idx_payment_transactions_external", "external_transaction_id"),
        Index("idx_payment_transactions_gateway", "gateway"),
        Index("idx_payment_transactions_date", "initiated_at"),
    )