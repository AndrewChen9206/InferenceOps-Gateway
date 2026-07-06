import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_key: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    display_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    daily_budget_usd: Mapped[Decimal] = mapped_column(
        Numeric(10, 6), default=Decimal("0.10")
    )
    requests_per_minute: Mapped[int] = mapped_column(Integer, default=60)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    requests: Mapped[list["RequestLog"]] = relationship(back_populates="user")


class ModelPrice(Base):
    __tablename__ = "model_prices"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    model_name: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    input_cost_per_1k_tokens: Mapped[Decimal] = mapped_column(
        Numeric(10, 6), nullable=False
    )
    output_cost_per_1k_tokens: Mapped[Decimal] = mapped_column(
        Numeric(10, 6), nullable=False
    )
    provider_name: Mapped[str] = mapped_column(String(100), default="local-mock")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class RequestLog(Base):
    __tablename__ = "requests"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )

    task_type: Mapped[str] = mapped_column(String(100), nullable=False)
    policy: Mapped[str] = mapped_column(String(100), nullable=False)
    selected_model: Mapped[str] = mapped_column(String(100), nullable=False)

    prompt_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    cache_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    cache_hit: Mapped[bool] = mapped_column(Boolean, default=False)
    fallback_used: Mapped[bool] = mapped_column(Boolean, default=False)
    primary_model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    fallback_model: Mapped[str | None] = mapped_column(String(100), nullable=True)

    estimated_input_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    estimated_output_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    estimated_cost_usd: Mapped[Decimal] = mapped_column(Numeric(12, 8), nullable=False)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False)

    status: Mapped[str] = mapped_column(String(50), nullable=False)
    error_type: Mapped[str | None] = mapped_column(String(100), nullable=True)

    output_preview: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped[User] = relationship(back_populates="requests")
