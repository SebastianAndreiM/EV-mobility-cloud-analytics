import { useState } from "react";
import { trainDuration, trainAnomaly } from "../api/mlApi";

export default function MLTrainingPage() {
  const [message, setMessage] = useState("");

  const handleTrainDuration = async () => {
    const res = await trainDuration();
    setMessage(`Duration training queued: job #${res.job_id}`);
  };
  const handleTrainAnomaly = async () => {
    const res = await trainAnomaly();
    setMessage(`Anomaly training queued: job #${res.job_id}`);
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
        </div>
        {message && <p className="info">{message}</p>}
        <p>Track progress on the Jobs page.</p>
      </section>
    </div>
  );
}
