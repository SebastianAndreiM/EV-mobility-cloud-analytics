import { apiClient } from "./client";

export interface PredictInput {
  charger_type: string;
  start_battery_percent: number;
  end_battery_percent: number;
  battery_capacity_kwh: number;
  charging_power_kw: number;
  temperature_c: number;
  average_voltage: number;
  average_current: number;
}

export interface Metrics {
  model_type: string;
  model_version: string;
  mae: number | null;
  rmse: number | null;
  r2: number | null;
  training_rows: number;
  trained_at: string;
}

export interface DetectedAnomaly {
  id: number;
  vehicle_id: string;
  charger_id: string;
  charger_type: string;
  energy_kwh: number;
  duration_minutes: number;
  anomaly_score: number;
}

export interface AnomalyDetectionResult {
  model_version: string;
  scored: number;
  anomalies: DetectedAnomaly[];
}

export async function trainDuration() {
  const { data } = await apiClient.post("/ml/train-duration-model");
  return data;
}

export async function trainAnomaly() {
  const { data } = await apiClient.post("/ml/train-anomaly-model");
  return data;
}

export async function getMetrics(model_type = "duration"): Promise<Metrics> {
  const { data } = await apiClient.get("/ml/metrics", { params: { model_type } });
  return data;
}

export async function detectAnomalies(limit = 100): Promise<AnomalyDetectionResult> {
  const { data } = await apiClient.post("/ml/detect-anomalies", null, { params: { limit } });
  return data;
}
export async function predictDuration(input: PredictInput) {
  const { data } = await apiClient.post("/ml/predict-duration", input);
  return data;
}
