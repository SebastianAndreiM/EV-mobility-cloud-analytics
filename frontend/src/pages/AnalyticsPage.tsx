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

  if (loading) return <Loading />;

  return (
    <div>
      <h1>Analytics</h1>
      <h2>Daily Energy</h2>
      <div style={{ width: "100%", height: 300 }}>
        <ResponsiveContainer>
          <LineChart data={daily}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="day" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="total_energy" stroke="#2563eb" />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <h2>Charger Performance (top 10 by sessions)</h2>
      <div style={{ width: "100%", height: 300 }}>
        <ResponsiveContainer>
          <BarChart data={perf}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="charger_id" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="sessions" fill="#16a34a" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
