import { useEffect, useState } from "react";
import { getSummary, Summary } from "../api/analyticsApi";
import StatCard from "../components/StatCard";
import Loading from "../components/Loading";
import ErrorMessage from "../components/ErrorMessage";

const fmt = (v: number, digits = 1) => Number(v || 0).toFixed(digits);

export default function DashboardPage() {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getSummary()
      .then(setSummary)
      .catch((e) => setError(e?.response?.data?.detail || "Failed to load summary"))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Loading label="Loading dashboard..." />;
  if (error) return <ErrorMessage message={error} />;
  if (!summary) return null;

  return (
    <div className="page">
      <section className="page-hero">
        <p className="eyebrow">EV Mobility Cloud Analytics</p>
        <h1>Dashboard</h1>
        <p className="hero-copy">
          Quick view over generated EV charging sessions, energy usage, charging duration and anomaly rate.
        </p>
      </section>

      <div className="stat-grid">
        <StatCard label="Total Sessions" value={summary.total_sessions} hint="Generated charging sessions" />
        <StatCard label="Avg Duration" value={`${fmt(summary.average_duration)} min`} hint="Mean charging time" />
        <StatCard label="Total Energy" value={`${fmt(summary.total_energy, 0)} kWh`} hint="Energy delivered" />
        <StatCard label="Anomaly Rate" value={`${(summary.anomaly_rate * 100).toFixed(1)}%`} hint="Suspicious sessions" />
      </div>

      <section className="card">
        <div className="card-header">
          <div>
            <h2>Demo flow</h2>
            <p>Generate data, train the models, then test one prediction from the Predict page.</p>
          </div>
        </div>
        <p>
          This project is built like a small cloud product: API, database, Redis rate limit, RabbitMQ queue,
          Celery worker, ML artifacts and a React dashboard.
        </p>
      </section>
    </div>
  );
}
