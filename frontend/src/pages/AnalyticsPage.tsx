import { useEffect, useState } from "react";
import {
  BarChart, Bar, LineChart, Line, XAxis, YAxis, Tooltip,
  ResponsiveContainer, CartesianGrid,
} from "recharts";
import { getDailyEnergy, getChargerPerformance } from "../api/analyticsApi";
import Loading from "../components/Loading";

export default function AnalyticsPage() {
  const [daily, setDaily] = useState<any[]>([]);
  const [perf, setPerf] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getDailyEnergy(), getChargerPerformance()])
      .then(([d, p]) => {
        setDaily(d);
        setPerf(p.slice(0, 10));
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Loading label="Loading analytics..." />;

  return (
    <div className="page">
      <section className="page-hero">
        <p className="eyebrow">KPIs and operational data</p>
        <h1>Analytics</h1>
        <p className="hero-copy">
          Charts for daily energy and charger performance. Simple, but useful enough for a technical demo.
        </p>
      </section>

      <section className="chart-card">
        <div className="card-header">
          <div>
            <h2>Daily Energy</h2>
            <p>Energy delivered per day from all generated sessions.</p>
          </div>
        </div>
        <div className="chart-body">
          <ResponsiveContainer>
            <LineChart data={daily}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.18)" />
              <XAxis dataKey="day" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid rgba(148,163,184,0.25)", borderRadius: 12 }} />
              <Line type="monotone" dataKey="total_energy" stroke="#38bdf8" strokeWidth={3} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section className="chart-card">
        <div className="card-header">
          <div>
            <h2>Charger Performance</h2>
            <p>Top 10 chargers by number of sessions.</p>
          </div>
        </div>
        <div className="chart-body">
          <ResponsiveContainer>
            <BarChart data={perf}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.18)" />
              <XAxis dataKey="charger_id" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid rgba(148,163,184,0.25)", borderRadius: 12 }} />
              <Bar dataKey="sessions" fill="#22c55e" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>
    </div>
  );
}
