"""Factory Pattern for synthetic EV charging session generation.

Deterministic when a seed is supplied. Produces dicts ready to be mapped to
ChargingSession rows, satisfying business constraints:
  start_battery < end_battery, duration > 0, energy > 0, realistic temperature.
"""
from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone

CHARGER_PROFILES = {
    "slow": {"power_range": (3.0, 7.4), "connectors": ["Type2"], "price": 0.25},
    "fast": {"power_range": (11.0, 50.0), "connectors": ["Type2", "CCS"], "price": 0.45},
    "ultra_fast": {"power_range": (100.0, 350.0), "connectors": ["CCS", "CHAdeMO"], "price": 0.65},
}
LOCATIONS = ["Cluj-Napoca", "Bucharest", "Berlin", "Munich", "Vienna", "Amsterdam"]
STATUSES = ["completed", "completed", "completed", "interrupted", "failed"]


class EVDataFactory:
    def __init__(self, seed: int | None = None):
        self.rng = random.Random(seed)

    def _one(self, idx: int) -> dict:
        charger_type = self.rng.choice(list(CHARGER_PROFILES.keys()))
        profile = CHARGER_PROFILES[charger_type]
        power = round(self.rng.uniform(*profile["power_range"]), 1)

        capacity = self.rng.choice([40.0, 52.0, 64.0, 77.0, 100.0])
        start_batt = round(self.rng.uniform(5, 60), 1)
        end_batt = round(self.rng.uniform(start_batt + 5, 100), 1)
        end_batt = min(end_batt, 100.0)

        energy = round((end_batt - start_batt) / 100.0 * capacity, 2)
        energy = max(energy, 0.1)

        # duration from energy and power, with noise
        base_minutes = (energy / power) * 60.0
        duration = round(max(base_minutes * self.rng.uniform(0.9, 1.3), 1.0), 1)

        voltage = round(self.rng.uniform(360, 420) if charger_type != "slow"
                        else self.rng.uniform(220, 240), 1)
        current = round((power * 1000) / voltage, 1)
        temperature = round(self.rng.uniform(-5, 40), 1)

        status = self.rng.choice(STATUSES)
        is_anomaly = self.rng.random() < 0.05
        if is_anomaly:
            # distort one signal to create a detectable anomaly
            duration = round(duration * self.rng.uniform(2.5, 4.0), 1)

        start_time = datetime.now(timezone.utc) - timedelta(
            days=self.rng.randint(0, 29), minutes=self.rng.randint(0, 1440)
        )
        end_time = start_time + timedelta(minutes=duration)
        cost = round(energy * profile["price"], 2)

        return {
            "vehicle_id": f"EV-{self.rng.randint(1000, 9999)}",
            "charger_id": f"CHG-{charger_type[:1].upper()}-{self.rng.randint(100, 999)}",
            "charger_type": charger_type,
            "connector_type": self.rng.choice(profile["connectors"]),
            "location": self.rng.choice(LOCATIONS),
            "start_time": start_time,
            "end_time": end_time,
            "start_battery_percent": start_batt,
            "end_battery_percent": end_batt,
            "battery_capacity_kwh": capacity,
            "energy_kwh": energy,
            "charging_power_kw": power,
            "average_voltage": voltage,
            "average_current": current,
            "temperature_c": temperature,
            "duration_minutes": duration,
            "cost_eur": cost,
            "status": status,
            "is_anomaly": is_anomaly,
        }

    def generate(self, count: int) -> list[dict]:
        return [self._one(i) for i in range(count)]


class DataGeneratorFactory:
    """Factory entry point."""

    @staticmethod
    def create(seed: int | None = None) -> EVDataFactory:
        return EVDataFactory(seed=seed)
