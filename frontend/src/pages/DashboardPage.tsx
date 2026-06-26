import { useEffect, useState } from "react";
import { getSummary, Summary } from "../api/analyticsApi";
import StatCard from "../components/StatCard";
import Loading from "../components/Loading";
import ErrorMessage from "../components/ErrorMessage";

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

  if (loading) return <Loading />;
  if (error) return <ErrorMessage message={error} />;
  if (!summary) return null;

  return (
    <div>
      <h1>Dashboard</h1>
      <div className="stat-grid">
        <StatCard label="Total Sessions" value={summary.total_sessions} />
        <StatCard label="Avg Duration (min)" value={summary.average_duration} />
        <StatCard label="Total Energy (kWh)" value={summary.total_energy} />
        <StatCard label="Anomaly Rate" value={`${(summary.anomaly_rate * 100).toFixed(1)}%`} />
      </div>
    </div>
  );
}
