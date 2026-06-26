"""Unit tests for the synthetic EV data factory (Factory Pattern).
Pure, no DB. Verifies determinism and physical/business constraints."""
from app.patterns.data_generator_factory import DataGeneratorFactory, CHARGER_PROFILES


def test_factory_deterministic_with_same_seed():
    a = DataGeneratorFactory.create(seed=42).generate(20)
    b = DataGeneratorFactory.create(seed=42).generate(20)
    assert [x["energy_kwh"] for x in a] == [x["energy_kwh"] for x in b]


def test_factory_different_seed_differs():
    a = DataGeneratorFactory.create(seed=1).generate(20)
    b = DataGeneratorFactory.create(seed=2).generate(20)
    assert [x["energy_kwh"] for x in a] != [x["energy_kwh"] for x in b]


def test_factory_generates_exact_count():
    assert len(DataGeneratorFactory.create(seed=1).generate(137)) == 137


def test_factory_battery_constraint():
    for r in DataGeneratorFactory.create(seed=1).generate(300):
        assert r["start_battery_percent"] < r["end_battery_percent"]
        assert 0 <= r["start_battery_percent"] <= 100
        assert 0 <= r["end_battery_percent"] <= 100


def test_factory_positive_physical_values():
    for r in DataGeneratorFactory.create(seed=1).generate(300):
        assert r["duration_minutes"] > 0
        assert r["energy_kwh"] > 0
        assert r["charging_power_kw"] > 0
        assert r["average_voltage"] > 0
        assert r["average_current"] > 0


def test_factory_temperature_in_range():
    for r in DataGeneratorFactory.create(seed=1).generate(300):
        assert -10 <= r["temperature_c"] <= 45


def test_factory_charger_type_valid_and_power_matches_profile():
    for r in DataGeneratorFactory.create(seed=4).generate(300):
        assert r["charger_type"] in CHARGER_PROFILES
        lo, hi = CHARGER_PROFILES[r["charger_type"]]["power_range"]
        # anomalies may distort duration, not power; power stays within profile
        assert lo <= r["charging_power_kw"] <= hi


def test_factory_status_values_valid():
    seen = {r["status"] for r in DataGeneratorFactory.create(seed=8).generate(300)}
    assert seen <= {"completed", "interrupted", "failed"}


def test_factory_end_time_after_start_time():
    for r in DataGeneratorFactory.create(seed=6).generate(100):
        assert r["end_time"] > r["start_time"]


def test_factory_cost_non_negative():
    for r in DataGeneratorFactory.create(seed=6).generate(100):
        assert r["cost_eur"] >= 0
