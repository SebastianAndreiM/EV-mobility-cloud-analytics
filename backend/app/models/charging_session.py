from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class ChargingSession(Base):
    __tablename__ = "charging_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vehicle_id: Mapped[str] = mapped_column(String(64), index=True)
    charger_id: Mapped[str] = mapped_column(String(64), index=True)
    charger_type: Mapped[str] = mapped_column(String(16), index=True)  # slow/fast/ultra_fast
    connector_type: Mapped[str] = mapped_column(String(32))
    location: Mapped[str] = mapped_column(String(128))

    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    start_battery_percent: Mapped[float] = mapped_column(Float)
    end_battery_percent: Mapped[float] = mapped_column(Float)
    battery_capacity_kwh: Mapped[float] = mapped_column(Float)
    energy_kwh: Mapped[float] = mapped_column(Float)
    charging_power_kw: Mapped[float] = mapped_column(Float)
    average_voltage: Mapped[float] = mapped_column(Float)
    average_current: Mapped[float] = mapped_column(Float)
    temperature_c: Mapped[float] = mapped_column(Float)
    duration_minutes: Mapped[float] = mapped_column(Float)
    cost_eur: Mapped[float] = mapped_column(Float)

    status: Mapped[str] = mapped_column(String(16), index=True)  # completed/interrupted/failed
    is_anomaly: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
