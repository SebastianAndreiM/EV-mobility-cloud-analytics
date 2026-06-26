from collections import defaultdict

from app.patterns.unit_of_work import UnitOfWork


class AnalyticsService:
    async def summary(self) -> dict:
        async with UnitOfWork() as uow:
            sessions = await uow.charging.all_for_training()
        n = len(sessions)
        if n == 0:
            return {k: 0 for k in [
                "total_sessions", "average_duration", "average_energy", "average_power",
                "anomaly_rate", "completion_rate", "total_energy", "total_cost"]}
        total_energy = sum(s.energy_kwh for s in sessions)
        total_cost = sum(s.cost_eur for s in sessions)
        anomalies = sum(1 for s in sessions if s.is_anomaly)
        completed = sum(1 for s in sessions if s.status == "completed")
        return {
            "total_sessions": n,
            "average_duration": round(sum(s.duration_minutes for s in sessions) / n, 2),
            "average_energy": round(total_energy / n, 2),
            "average_power": round(sum(s.charging_power_kw for s in sessions) / n, 2),
            "anomaly_rate": round(anomalies / n, 4),
            "completion_rate": round(completed / n, 4),
            "total_energy": round(total_energy, 2),
            "total_cost": round(total_cost, 2),
        }

    async def charger_performance(self) -> list[dict]:
        async with UnitOfWork() as uow:
            sessions = await uow.charging.all_for_training()
        groups = defaultdict(list)
        for s in sessions:
            groups[(s.charger_type, s.charger_id)].append(s)
        out = []
        for (ctype, cid), items in groups.items():
            k = len(items)
            out.append({
                "charger_type": ctype,
                "charger_id": cid,
                "sessions": k,
                "avg_energy": round(sum(i.energy_kwh for i in items) / k, 2),
                "avg_duration": round(sum(i.duration_minutes for i in items) / k, 2),
                "avg_power": round(sum(i.charging_power_kw for i in items) / k, 2),
            })
        return sorted(out, key=lambda x: x["sessions"], reverse=True)

    async def daily_energy(self) -> list[dict]:
        async with UnitOfWork() as uow:
            sessions = await uow.charging.all_for_training()
        days = defaultdict(lambda: {"total_energy": 0.0, "sessions": 0})
        for s in sessions:
            key = s.start_time.date().isoformat()
            days[key]["total_energy"] += s.energy_kwh
            days[key]["sessions"] += 1
        return [
            {"day": d, "total_energy": round(v["total_energy"], 2), "sessions": v["sessions"]}
            for d, v in sorted(days.items())
        ]

    async def anomalies(self) -> list:
        async with UnitOfWork() as uow:
            return await uow.charging.anomalies()
