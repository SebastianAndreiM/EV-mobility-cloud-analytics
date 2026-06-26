import { useState, FormEvent } from "react";
import { predictDuration, PredictInput } from "../api/mlApi";
import ErrorMessage from "../components/ErrorMessage";

const initial: PredictInput = {
  charger_type: "fast",
  start_battery_percent: 20,
  end_battery_percent: 80,
  battery_capacity_kwh: 64,
  charging_power_kw: 50,
  temperature_c: 20,
  average_voltage: 400,
  average_current: 125,
};

export default function PredictionPage() {
  const [form, setForm] = useState<PredictInput>(initial);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");

  const validate = (): string => {
    if (form.start_battery_percent >= form.end_battery_percent)
      return "Start battery must be lower than end battery";
    if (form.battery_capacity_kwh <= 0) return "Battery capacity must be positive";
    if (form.charging_power_kw <= 0) return "Charging power must be positive";
    return "";
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setResult(null);
    const v = validate();
    if (v) {
      setError(v);
      return;
    }
    try {
      const res = await predictDuration(form);
      setResult(res);
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Prediction failed");
    }
  };

  const num = (k: keyof PredictInput) => (e: any) =>
    setForm({ ...form, [k]: Number(e.target.value) });

  return (
    <div className="page">
      <section className="page-hero">
        <p className="eyebrow">Model serving</p>
        <h1>Predict Charging Duration</h1>
        <p className="hero-copy">
          Protected prediction endpoint with request logging and rate limiting.
        </p>
      </section>
      <section className="card">
        <form className="prediction-form" onSubmit={handleSubmit} aria-label="predict-form">
          <div>
            <label htmlFor="charger_type">Charger type</label>
            <select id="charger_type" value={form.charger_type}
              onChange={(e) => setForm({ ...form, charger_type: e.target.value })}>
              <option value="slow">slow</option>
              <option value="fast">fast</option>
              <option value="ultra_fast">ultra_fast</option>
            </select>
          </div>
          <div>
            <label htmlFor="start">Start battery %</label>
            <input id="start" type="number" value={form.start_battery_percent} onChange={num("start_battery_percent")} />
          </div>
          <div>
            <label htmlFor="end">End battery %</label>
            <input id="end" type="number" value={form.end_battery_percent} onChange={num("end_battery_percent")} />
          </div>
          <div>
            <label htmlFor="cap">Battery capacity kWh</label>
            <input id="cap" type="number" value={form.battery_capacity_kwh} onChange={num("battery_capacity_kwh")} />
          </div>
          <div>
            <label htmlFor="power">Charging power kW</label>
            <input id="power" type="number" value={form.charging_power_kw} onChange={num("charging_power_kw")} />
          </div>
          <div>
            <label htmlFor="temp">Temperature °C</label>
            <input id="temp" type="number" value={form.temperature_c} onChange={num("temperature_c")} />
          </div>
          <div>
            <label htmlFor="volt">Avg voltage</label>
            <input id="volt" type="number" value={form.average_voltage} onChange={num("average_voltage")} />
          </div>
          <div>
            <label htmlFor="curr">Avg current</label>
            <input id="curr" type="number" value={form.average_current} onChange={num("average_current")} />
          </div>
          <div className="full-row">
            <ErrorMessage message={error} />
          </div>
          <div className="full-row">
            <button type="submit">Predict</button>
          </div>
        </form>
        {result && (
          <div className="result" role="status">
            <h2>{result.predicted_duration_minutes} minutes</h2>
            <p>Model: {result.model_version}</p>
            <p>{result.confidence_note}</p>
          </div>
        )}
      </section>
    </div>
  );
}
