from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    credentials: Mapped[list["AuthCredential"]] = relationship(
        back_populates="account", cascade="all, delete-orphan"
    )


class AuthCredential(Base):
    __tablename__ = "auth_credentials"
    # one credential per (account, provider): a user has at most one local
    # password, at most one Google identity, etc.
    __table_args__ = (
        UniqueConstraint("account_id", "provider", name="uq_account_provider"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id", ondelete="CASCADE"), index=True, nullable=False
    )
    provider: Mapped[str] = mapped_column(String(32), default="local", index=True)
    # For provider="local" this holds the bcrypt hash. For OAuth providers it
    # would hold the provider's subject id and hashed_password stays null.
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    provider_subject: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    account: Mapped["Account"] = relationship(back_populates="credentials")