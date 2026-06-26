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
    <div>
      <h1>ML Training</h1>
      <div className="toolbar">
        <button onClick={handleTrainDuration}>Train Duration Model</button>
        <button onClick={handleTrainAnomaly}>Train Anomaly Model</button>
      </div>
      {message && <p className="info">{message}</p>}
      <p>Track progress on the Jobs page.</p>
    </div>
  );
}
