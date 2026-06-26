import { useEffect, useState } from "react";
import { getSessions, generateData, deleteAllSessions, ChargingSession, SessionFilters } from "../api/dataApi";
import Loading from "../components/Loading";
import ErrorMessage from "../components/ErrorMessage";

export default function SessionsPage() {
  const [items, setItems] = useState<ChargingSession[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filters, setFilters] = useState<SessionFilters>({ page: 1, page_size: 20 });
  const [count, setCount] = useState(5000);
  const [seed, setSeed] = useState(42);

  const load = (f: SessionFilters) => {
    setLoading(true);
    getSessions(f)
      .then((res) => {
        setItems(res.items);
        setTotal(res.total);
      })
      .catch((e) => setError(e?.response?.data?.detail || "Failed"))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load(filters);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleGenerate = async () => {
    await generateData(count, seed);
    load(filters);
  };

  const handleDelete = async () => {
    await deleteAllSessions();
    load(filters);
  };

  const applyFilter = (patch: Partial<SessionFilters>) => {
    const next = { ...filters, ...patch, page: 1 };
    setFilters(next);
    load(next);
  };

  return (
    <div className="page">
      <section className="page-hero">
        <p className="eyebrow">ETL demo</p>
        <h1>Charging Sessions</h1>
        <p className="hero-copy">
          Generate synthetic EV sessions, store them in PostgreSQL and filter the data used by analytics and ML.
        </p>
      </section>

      <section className="card">
        <div className="card-header">
          <div>
            <h2>Generate data</h2>
            <p>Use a fixed seed when you want the same demo data every time.</p>
          </div>
        </div>
        <div className="toolbar">
          <input type="number" aria-label="count" value={count}
            onChange={(e) => setCount(Number(e.target.value))} />
          <input type="number" aria-label="seed" value={seed}
            onChange={(e) => setSeed(Number(e.target.value))} />
          <button onClick={handleGenerate}>Generate</button>
          <button className="danger-button" onClick={handleDelete}>Delete All</button>
        </div>
      </section>

      <section className="card">
        <div className="card-header">
          <div>
            <h2>Sessions table</h2>
            <p>Total: {total}</p>
          </div>
          <div className="toolbar">
            <select aria-label="charger_type" onChange={(e) => applyFilter({ charger_type: e.target.value || undefined })}>
              <option value="">All chargers</option>
              <option value="slow">Slow</option>
              <option value="fast">Fast</option>
              <option value="ultra_fast">Ultra fast</option>
            </select>
            <label>
              <input type="checkbox" onChange={(e) => applyFilter({ anomaly_only: e.target.checked })} />
              Anomalies only
            </label>
          </div>
        </div>
        <ErrorMessage message={error} />
        {loading ? (
          <Loading />
        ) : (
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>ID</th><th>Vehicle</th><th>Charger</th><th>Type</th>
                  <th>Energy</th><th>Duration</th><th>Status</th><th>Anomaly</th>
                </tr>
              </thead>
              <tbody>
                {items.map((s) => (
                  <tr key={s.id}>
                    <td>{s.id}</td><td>{s.vehicle_id}</td><td>{s.charger_id}</td>
                    <td>{s.charger_type}</td><td>{s.energy_kwh}</td>
                    <td>{s.duration_minutes}</td><td>{s.status}</td>
                    <td>{s.is_anomaly ? "⚠️" : ""}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
