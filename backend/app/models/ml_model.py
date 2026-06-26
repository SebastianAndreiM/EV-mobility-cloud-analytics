from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class MLModelMetric(Base):
    __tablename__ = "ml_model_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    model_type: Mapped[str] = mapped_column(String(32), index=True)  # duration/anomaly
    model_version: Mapped[str] = mapped_column(String(64))
    artifact_path: Mapped[str] = mapped_column(String(255))

    mae: Mapped[float | None] = mapped_column(Float, nullable=True)
    rmse: Mapped[float | None] = mapped_column(Float, nullable=True)
    r2: Mapped[float | None] = mapped_column(Float, nullable=True)
    training_rows: Mapped[int] = mapped_column(Integer, default=0)
    trained_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )
