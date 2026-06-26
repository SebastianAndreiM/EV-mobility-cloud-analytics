from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Integer, String, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class PredictionLog(Base):
    __tablename__ = "prediction_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(Integer, index=True, nullable=True)
    model_version: Mapped[str] = mapped_column(String(64))
    input_payload: Mapped[dict] = mapped_column(JSON)
    predicted_duration_minutes: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )
