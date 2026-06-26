import { useState, useEffect } from "react";
import {
  trainDuration, trainAnomaly, getMetrics, detectAnomalies,
  Metrics, AnomalyDetectionResult,
} from "../api/mlApi";
import ErrorMessage from "../components/ErrorMessage";

export default function MLTrainingPage() {
  const [message, setMessage] = useState("");
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [metricsError, setMetricsError] = useState("");
  const [anomalies, setAnomalies] = useState<AnomalyDetectionResult | null>(null);
  const [anomalyError, setAnomalyError] = useState("");

  const loadMetrics = async () => {
    setMetricsError("");
    try {
      setMetrics(await getMetrics("duration"));
    } catch {
      setMetrics(null);
      setMetricsError("No duration model trained yet.");
    }
  };

  useEffect(() => {
    loadMetrics();
  }, []);

  const handleTrainDuration = async () => {
    const res = await trainDuration();
    setMessage(`Duration training queued: job #${res.job_id}. Check the Jobs page, then refresh metrics.`);
  };

  const handleTrainAnomaly = async () => {
    const res = await trainAnomaly();
    setMessage(`Anomaly training queued: job #${res.job_id}.`);
  };

  const handleDetect = async () => {
    setAnomalyError("");
    try {
      setAnomalies(await detectAnomalies(100));
    } catch {
      setAnomalies(null);
      setAnomalyError("No anomaly model trained yet. Train it first.");
    }
  };

  return (
    <div className="page">
      <section className="page-hero">
        <p className="eyebrow">Async machine learning</p>
        <h1>ML Training</h1>
        <p className="hero-copy">
          Queue duration prediction and anomaly detection training jobs. The worker saves trained artifacts for prediction.
        </p>
      </section>

      <section className="card">
        <div className="card-header">
          <div>
            <h2>Train models</h2>
            <p>Run this after generating sessions.</p>
          </div>
        </div>
        <div className="toolbar">
          <button onClick={handleTrainDuration}>Train Duration Model</button>
          <button onClick={handleTrainAnomaly}>Train Anomaly Model</button>
          <button onClick={loadMetrics}>Refresh Metrics</button>
        </div>
        {message && <p className="info">{message}</p>}
        <p>Track progress on the Jobs page.</p>
      </section>

      <section className="card">
        <div className="card-header">
          <div>
            <h2>Duration model metrics</h2>
            <p>Performance of the latest trained RandomForest on the test set.</p>
          </div>
        </div>
        {metricsError && <p className="info">{metricsError}</p>}
        {metrics && (
          <div className="stat-grid">
            <div className="stat-card">
              <div className="stat-label">R² (test set)</div>
              <div className="stat-value">{metrics.r2?.toFixed(3) ?? "—"}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">MAE (min)</div>
              <div className="stat-value">{metrics.mae?.toFixed(2) ?? "—"}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">RMSE (min)</div>
              <div className="stat-value">{metrics.rmse?.toFixed(2) ?? "—"}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Training rows</div>
              <div className="stat-value">{metrics.training_rows}</div>
            </div>
          </div>
        )}
      </section>

      <section className="card">
        <div className="card-header">
          <div>
            <h2>Anomaly detection</h2>
            <p>Scores stored sessions with the trained IsolationForest model.</p>
          </div>
        </div>
        <div className="toolbar">
          <button onClick={handleDetect}>Run Anomaly Detection</button>
        </div>
        <ErrorMessage message={anomalyError} />
        {anomalies && (
          <>
            <p className="info">
              Model {anomalies.model_version} scored {anomalies.scored} sessions,
              flagged {anomalies.anomalies.length}.
            </p>
            <table className="data-table">
              <thead>
                <tr>
                  <th>ID</th><th>Vehicle</th><th>Charger</th><th>Type</th>
                  <th>Energy</th><th>Duration</th><th>Anomaly score</th>
                </tr>
              </thead>
              <tbody>
                {anomalies.anomalies.map((a) => (
                  <tr key={a.id}>
                    <td>{a.id}</td><td>{a.vehicle_id}</td><td>{a.charger_id}</td>
                    <td>{a.charger_type}</td><td>{a.energy_kwh}</td>
                    <td>{a.duration_minutes}</td><td>{a.anomaly_score}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </>
        )}
      </section>
    </div>
  );
}